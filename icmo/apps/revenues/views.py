from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_extensions.mixins import NestedViewSetMixin
from vanilla import TemplateView

from api.mixins import NestedKwargsMixin
from api.viewsets import IcmoModelViewSet
from companies.models import Company
from core.cbvs import ItemRequiredMixin, AppMixin
from revenues.models import Segment, RevenuePlan
from .forms import ClonePlanForm
from .serializers import RevenuePlanSerializer, SegmentSerializer


class StartView(ItemRequiredMixin, TemplateView):
    template_name = 'revenues/start_map_example.html'
    item_required = Company

    def get_context_data(self, **kwargs):
        context = super(StartView, self).get_context_data(**kwargs)
        context.update(dict(
            app_name='start'
        ))
        return context


class RevenuePlanListView(AppMixin, TemplateView):
    item_required = Company
    template_name = 'revenues/revenue_plans.html'
    app_name = 'revenue_plans'

    def get_context_data(self, **kwargs):
        context_data = super(RevenuePlanListView, self).get_context_data(**kwargs)
        plans_qs = self.request.company_user.permitted_revenue_plans
        context_data.update(dict(
            clone_plan_form=ClonePlanForm(),
            has_plans=plans_qs.count(),
            api_url=reverse('company-plans-list', kwargs=dict(
                parent_lookup_company__slug=self.request.selected_company.slug)),
        ))
        return context_data


class RevenuePlanViewSet(NestedViewSetMixin, NestedKwargsMixin, IcmoModelViewSet):
    """
    API endpoint that allows revenue plans to be viewed or edited.
    """
    lookup_field = 'slug'
    lookup_value_regex = '[\w-]+'
    serializer_class = RevenuePlanSerializer

    def get_queryset(self):
        """ Optional:  Filter plan by plan_type """
        queryset = self.request.company_user.permitted_revenue_plans.all()
        plan_type = self.request.query_params.get('plan_type', None)
        if plan_type is not None:
            queryset = queryset.filter(plan_type=plan_type)
        return queryset


class ClonePlanView(NestedViewSetMixin, NestedKwargsMixin, APIView):
    def post(self, request, *args, **kwargs):
        plan = get_object_or_404(RevenuePlan, company=request.selected_company,
                                 slug=self.get_parents_query_dict().get('revenue_plan__slug'))
        if not all(k in request.POST for k in ('name', 'year')):
            return Response(dict(error='You must supply at least a name and a year'), status=400)

        if RevenuePlan.objects.filter(company=request.selected_company,
                                      is_active=True,
                                      name=request.POST.get('name')).exists():
            return Response(
                dict(error='A plan with this name already exists, please choose a new name'),
                status=400)

        plan.clone(
            request.POST.get('name'), request.POST.get('year'),
            request.POST.get('programs'), request.POST.get('budget_plans'),
            request.POST.get('budget_actuals'), request.POST.get('performance_actuals'),
            request.POST.get('tasks'), request.POST.get('task_states')
        )

        return Response(status=200)


class SegmentViewSet(NestedViewSetMixin, NestedKwargsMixin, IcmoModelViewSet):
    """
    API endpoint that allows revenue plan segments to be viewed or edited.
    """
    lookup_field = 'slug'
    lookup_value_regex = '[\w-]+'
    serializer_class = SegmentSerializer
    queryset = Segment.objects.all()

    def get_queryset(self):
        queryset = super(SegmentViewSet, self).get_queryset()
        return queryset.select_related().filter(
            slug__in=self.request.company_user.permitted_segments_slugs)


class CloneSegmentView(NestedViewSetMixin, NestedKwargsMixin, APIView):
    def post(self, request, *args, **kwargs):
        source_segment = get_object_or_404(Segment, revenue_plan=self.request.selected_plan,
                                           slug=self.get_parents_query_dict().get('segment__slug'))
        if not request.POST.get('name') and not request.POST.get('target'):
            return Response(dict(error='You must supply either a name or a target segment'),
                            status=400)

        target_segment = None
        if request.POST.get('name') and Segment.objects.filter(revenue_plan=request.selected_plan,
                                                               is_active=True,
                                                               name=request.POST.get(
                                                                   'name')).exists():
            return Response(
                dict(
                    error="A segment with this name already exists, please choose a new name or "
                          "select it as a target from the drop down"
                ),
                status=400
            )
        elif request.POST.get('target'):
            target_segment = Segment.objects.filter(revenue_plan=request.selected_plan,
                                                    slug=request.POST.get('target')).first()
            if not target_segment:
                return Response(dict(error="Target segment could not be found"), status=400)

            if target_segment == source_segment:
                return Response(dict(error="Cannot clone a segment onto itself."), status=400)

        source_segment.clone(
            target_segment if target_segment else request.POST.get('name'),
            request.POST.get('programs'), request.POST.get('budget_plans'),
            request.POST.get('budget_actuals'),
            request.POST.get('performance_actuals'),
            request.POST.get('tasks'), request.POST.get('task_states')
        )

        return Response(status=200)
