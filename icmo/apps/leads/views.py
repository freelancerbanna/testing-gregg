from django.core.urlresolvers import reverse
from rest_framework_extensions.cache.decorators import cache_response
from rest_framework_extensions.mixins import NestedViewSetMixin
from vanilla import TemplateView

from api.mixins import NestedKwargsMixin
from api.viewsets import IcmoModelViewSet
from core.api_cache import ICMOAPIListKeyConstructor
from core.cbvs import AppMixin
from periods.models import Period
from revenues.forms import SegmentForm
from revenues.models import RevenuePlan
from serializers import ProgramSerializer
from .models import Program


class ProgramMixView(AppMixin, TemplateView):
    item_required = RevenuePlan
    template_name = 'programs/program_mix.html'
    app_name = 'program_mix'

    def get_context_data(self, **kwargs):
        context_data = super(ProgramMixView, self).get_context_data(**kwargs)
        context_data.update(dict(
            summary_api_url=reverse('company-plans-periods-list', kwargs=dict(
                parent_lookup_company__slug=self.request.selected_company.slug,
                parent_lookup_revenue_plan__slug=self.request.selected_plan.slug)),
            segment_form=SegmentForm(),
            funnel_data=Period.objects.filter(
                company=self.request.selected_company,
                revenue_plan=self.request.selected_plan,
                resolution='revenue_plan', period='year').first(),
            app_segment_content_template='programs/program_grid.html'
        ))
        return context_data

    def post(self, request, *args, **kwargs):
        segment_form = SegmentForm(request.POST)
        if segment_form.is_valid():
            segment = segment_form.save(commit=False)
            segment.revenue_plan = request.selected_plan
            segment.save()
        context_data = self.get_context_data(segment_form=segment_form)
        return self.render_to_response(context_data)


class ProgramViewSet(NestedViewSetMixin, NestedKwargsMixin, IcmoModelViewSet):
    """
    API endpoint that allows programs to be viewed or edited.
    """
    lookup_field = 'slug'
    lookup_value_regex = '[\w-]+'
    queryset = Program.objects.select_related().all()
    serializer_class = ProgramSerializer
    app_name = 'program_mix'

    def list(self, *args, **kwargs):
        return super(ProgramViewSet, self).list(*args, **kwargs)
