from django.core.urlresolvers import reverse
from rest_framework.viewsets import ModelViewSet
from rest_framework_extensions.mixins import NestedViewSetMixin
from vanilla import TemplateView

from api.mixins import NestedKwargsMixin
from core.cbvs import HidePlanBarMixin
from .forms import CompanyUserNotificationSubscriptionForm
from .models import CompanyUserNotificationSubscription
from .serializers import CompanyUserNotificationSubscriptionSerializer


class NotificationSubscriptionView(HidePlanBarMixin, TemplateView):
    template_name = 'notifications/notifications.html'

    def get_context_data(self, **kwargs):
        context = super(NotificationSubscriptionView, self).get_context_data(**kwargs)
        context.update(dict(
            app_name='user',
            api_url=reverse('company-list'),
            companies=self.request.user.companies.all(),
            form=CompanyUserNotificationSubscriptionForm(),
        ))
        return context


class NotificationSubscriptionViewSet(NestedViewSetMixin, NestedKwargsMixin, ModelViewSet):
    lookup_field = 'pk'
    lookup_value_regex = '[0-9]+'
    serializer_class = CompanyUserNotificationSubscriptionSerializer
    queryset = CompanyUserNotificationSubscription.objects.all()
    app_name = 'notifications'
