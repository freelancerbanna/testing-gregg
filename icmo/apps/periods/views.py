from collections import defaultdict

import django_filters
from django.http import Http404
from django.conf import settings
from djmoney.models.fields import MoneyPatched
from rest_framework import filters
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_extensions.cache.decorators import cache_response
from rest_framework_extensions.mixins import NestedViewSetMixin

from api.mixins import NestedKwargsMixin
from core.api_cache import ICMOAPIListKeyConstructor
from core.helpers import get_currency_whole_number_display
from core.models import BLANK_CHOICE
from periods.models import Period, PERIOD_CHOICES, PeriodTypes, ResolutionTypes
from periods.serializers import PeriodSerializer


class PeriodFilter(filters.FilterSet):
    class Meta:
        model = Period
        fields = ['period', 'period_type', 'period_range', 'resolution']

    period = django_filters.ChoiceFilter(name='period', choices=BLANK_CHOICE + PERIOD_CHOICES)
    period_range = django_filters.MethodFilter(name='period', action='filter_period_range',
                                               required=False)
    period_type = django_filters.AllValuesFilter(name='period_type',
                                                 choices=PeriodTypes.choices,
                                                 required=False)
    resolution = django_filters.AllValuesFilter(name='resolution', choices=ResolutionTypes.choices,
                                                required=False)

    def filter_period_range(self, queryset, value):
        if value and self.data['period_type'] == 'month':
            try:
                start, end = value.split('-')
            except ValueError:
                return queryset
            sample_period = queryset.first()
            if not sample_period:
                return queryset
            months = sample_period.company.fiscal_months_by_name
            try:
                start_i, end_i = months.index(start), months.index(end)
            except ValueError:
                return queryset
            q_months = months[start_i:end_i + 1]
            return queryset.filter(period__in=q_months)
        return queryset


class PeriodViewSet(NestedViewSetMixin, NestedKwargsMixin, ListModelMixin,
                    GenericViewSet):
    """
    API endpoint that allows revenue plan segments to be viewed or edited.
    """
    lookup_field = 'pk'
    lookup_value_regex = '[\w-]+'
    queryset = Period.objects.select_related('company', 'revenue_plan', 'segment', 'program',
                                             'campaign', 'custom_budget_line_item').all()
    serializer_class = PeriodSerializer
    filter_class = PeriodFilter

    @cache_response(key_func=ICMOAPIListKeyConstructor(), cache=settings.API_CACHE_NAME)
    def list(self, *args, **kwargs):
        return super(PeriodViewSet, self).list(*args, **kwargs)


class PeriodHorizontalListView(GenericAPIView):
    resolution = None
    serializer_class = PeriodSerializer
    simple_fields = ('pk', 'period', 'period_type', 'resolution',)
    fk_fields = ('company', 'revenue_plan', 'segment',
                 'program', 'custom_budget_line_item', 'campaign',)

    def get_queryset(self):
        self.resolution = self.request.query_params.get('resolution', None)
        if not self.resolution:
            raise Http404

        return Period.objects.select_related('company', 'revenue_plan', 'segment', 'program',
                                             'campaign', 'custom_budget_line_item').filter(
            resolution=self.resolution)

    def sanitize_value(self, value):
        if type(value) is MoneyPatched:
            localized_whole_number = get_currency_whole_number_display(value)
            value = dict([
                ('amount', value.amount),
                ('currency', value.currency.code),
                ('localized', str(value)),
                ('localized_whole_number', localized_whole_number),
            ])
        return value

    def get_fk_values(self, field, obj):
        output = {field: None, "%s_name" % field: None}
        if hasattr(obj, field) and getattr(obj, field):
            output[field] = getattr(getattr(obj, field), 'slug')
            output["%s_name" % field] = getattr(getattr(obj, field), 'name')
        return output

    @cache_response(key_func=ICMOAPIListKeyConstructor(), cache=settings.API_CACHE_NAME)
    def get(self, request, format=None, parent_lookup_revenue_plan__slug=None,
            parent_lookup_company__slug=None, parent_lookup_segment__slug=None):
        queryset = self.get_queryset()
        if not (parent_lookup_revenue_plan__slug and parent_lookup_company__slug):
            raise Http404
        queryset = queryset.filter(revenue_plan__slug=parent_lookup_revenue_plan__slug,
                                   company__slug=parent_lookup_company__slug)
        if parent_lookup_segment__slug:
            queryset = queryset.filter(segment__slug=parent_lookup_segment__slug)

        output = defaultdict(dict)
        for obj in queryset:
            grouper = getattr(obj, "%s_id" % self.resolution)
            for field in self.simple_fields:
                output[grouper][field] = getattr(obj, field)
            for field in self.fk_fields:
                output[grouper].update(self.get_fk_values(field, obj))
            for field in obj.icmo_fields:
                for suffix in ('plan', 'actual', 'variance'):
                    new_field = "%s_%s_%s" % (obj.period, field, suffix)
                    old_field = "%s_%s" % (field, suffix)
                    output[grouper][new_field] = self.sanitize_value(getattr(obj, old_field))

        return Response(output.values())
