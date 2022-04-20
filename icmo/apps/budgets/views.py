from rest_framework.reverse import reverse
from rest_framework_extensions.mixins import NestedViewSetMixin
from vanilla import TemplateView

from api.mixins import NestedKwargsMixin
from api.viewsets import IcmoModelViewSet
from budgets.models import BudgetLineItem
from budgets.serializers import BudgetLineItemSerializer
from core.cbvs import AppMixin
from revenues.models import RevenuePlan


class BudgetsView(AppMixin, TemplateView):
    item_required = RevenuePlan
    template_name = 'budgets/budget.html'
    app_name = 'budgets'

    def get_context_data(self, **kwargs):
        context_data = super(BudgetsView, self).get_context_data(**kwargs)
        context_data.update(dict(
            summary_api_url=reverse('companies-plans-horizontal-periods-list', kwargs=dict(
                parent_lookup_company__slug=self.request.selected_company.slug,
                parent_lookup_revenue_plan__slug=self.request.selected_plan.slug)),
            app_segment_content_template='budgets/budget_treelist.html'
        ))
        return context_data


class BudgetLineItemViewSet(NestedViewSetMixin, NestedKwargsMixin, IcmoModelViewSet):
    """
    API endpoint that allows programs to be viewed or edited.
    """
    lookup_field = 'slug'
    lookup_value_regex = '[\w-]+'
    serializer_class = BudgetLineItemSerializer
    queryset = BudgetLineItem.objects.select_related().all()
    app_name = 'budgets'

    def get_queryset(self):
        queryset = super(BudgetLineItemViewSet, self).get_queryset()
        return queryset.filter(
            segment__slug__in=self.request.company_user.permitted_segments_slugs)
