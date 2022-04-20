from django.core.urlresolvers import reverse
from rest_framework_extensions.mixins import NestedViewSetMixin
from vanilla import TemplateView

from api.mixins import NestedKwargsMixin
from api.viewsets import IcmoModelViewSet
from core.cbvs import AppMixin
from performance.models import Campaign
from performance.serializers import CampaignSerializer
from revenues.models import RevenuePlan


class CampaignListView(AppMixin, TemplateView):
    item_required = RevenuePlan
    template_name = 'performance/campaigns.html'
    app_name = 'performance'

    def get_context_data(self, **kwargs):
        context_data = super(CampaignListView, self).get_context_data(**kwargs)
        context_data.update(dict(
            summary_api_url=reverse('companies-plans-horizontal-periods-list', kwargs=dict(
                parent_lookup_company__slug=self.request.selected_company.slug,
                parent_lookup_revenue_plan__slug=self.request.selected_plan.slug)),
            app_segment_content_template='performance/two_pane_view.html'
        ))
        return context_data


class CampaignViewSet(NestedViewSetMixin, NestedKwargsMixin, IcmoModelViewSet):
    """
    API endpoint that allows revenue plans to be viewed or edited.
    """
    lookup_field = 'slug'
    lookup_value_regex = '[\w-]+'
    serializer_class = CampaignSerializer
    queryset = Campaign.objects.all()
    app_name = 'performance'

    def get_queryset(self):
        queryset = super(CampaignViewSet, self).get_queryset()
        return queryset.filter(segment__in=self.request.company_user.permitted_segments.all())
