from django.core.urlresolvers import reverse
from django.db.models import Q
from rest_framework_extensions.mixins import NestedViewSetMixin
from vanilla import TemplateView

from api.mixins import NestedKwargsMixin
from api.viewsets import IcmoModelViewSet
from companies.forms import CompanyUserForm
from companies.models import CompanyUser, CompanyUserGroup
from companies.serializers import CompanySerializer, CompanyUserSerializer, \
    CompanyUserGroupSerializer
from core.cbvs import HidePlanBarMixin, AppMixin


class CompaniesListView(HidePlanBarMixin, TemplateView):
    template_name = 'companies/companies.html'

    def get_context_data(self, **kwargs):
        context = super(CompaniesListView, self).get_context_data(**kwargs)
        context.update(dict(
            app_name='user',
            api_url=reverse('company-list'),
            your_companies=[x.company for x in self.request.user.permissions.all()]
        ))
        return context


class PermissionsView(AppMixin, HidePlanBarMixin, TemplateView):
    template_name = 'companies/permissions.html'
    app_name = 'permissions'

    def get_context_data(self, **kwargs):
        context = super(PermissionsView, self).get_context_data(**kwargs)
        context.update(dict(
            app_name='user',
            api_url=reverse('company-list'),
            company_users=CompanyUser.objects.filter(
                Q(owner=True) | Q(group__permissions__in=['view', 'change']),
                user=self.request.user),
            add_user_form=CompanyUserForm()
        ))
        return context


class CompanyViewSet(NestedViewSetMixin, IcmoModelViewSet):
    lookup_field = 'slug'
    lookup_value_regex = '[\w-]+'
    serializer_class = CompanySerializer

    def get_queryset(self):
        owner = self.request.query_params.get('owned', None)
        shared = self.request.query_params.get('shared', None)
        if owner is not None:
            queryset = self.request.user.owned_companies
        elif shared is not None:
            queryset = self.request.user.shared_companies
        else:
            queryset = self.request.user.companies
        return queryset


class CompanyUserViewSet(NestedViewSetMixin, NestedKwargsMixin, IcmoModelViewSet):
    lookup_field = 'slug'
    lookup_value_regex = '[\w-]+'
    serializer_class = CompanyUserSerializer
    queryset = CompanyUser.objects.filter(company__is_active=True, user__is_active=True)
    app_name = 'permissions'

    def get_queryset(self):
        queryset = super(CompanyUserViewSet, self).get_queryset()
        return queryset.filter(company__slug__in=self.request.user.companies_slugs)


class CompanyUserGroupViewSet(NestedViewSetMixin, NestedKwargsMixin, IcmoModelViewSet):
    lookup_field = 'slug'
    lookup_value_regex = '[\w-]+'
    serializer_class = CompanyUserGroupSerializer
    queryset = CompanyUserGroup.objects.filter(company__is_active=True)
    app_name = 'permissions'

    def get_queryset(self):
        queryset = super(CompanyUserGroupViewSet, self).get_queryset()
        return queryset.filter(company__in=self.request.user.companies.all())
