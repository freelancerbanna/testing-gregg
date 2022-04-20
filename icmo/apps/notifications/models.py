from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template import Context
from django.template.loader import render_to_string
from django_extensions.db.models import TimeStampedModel

from .settings import NOTIFICATION_TYPE_CHOICES, NOTIFICATION_TYPES


class CompanyUserNotificationSubscription(TimeStampedModel):
    company = models.ForeignKey('companies.Company')
    company_user = models.ForeignKey('companies.CompanyUser')
    notification_type = models.CharField(max_length=255, choices=NOTIFICATION_TYPE_CHOICES)
    frequency = models.CharField(max_length=255, editable=False)
    params = models.TextField(blank=True)
    params_display = models.TextField(blank=True)

    def send_notification(self, notification_type, instance):
        context_data = dict(
            company=self.company,
            company_user=self.company_user,
            user=self.company_user.user,
            instance=instance,
            notification_type=self.notification_type,
        )
        context = Context()
        subject = render_to_string(notification_type.subject_template(), context_data, context)
        html_body = render_to_string(notification_type.body_template(), context_data, context)
        msg = EmailMultiAlternatives(subject=subject, body=None, to=[self.company_user.user.email])
        msg.attach_alternative(html_body, "text/html")
        return msg.send()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.frequency = NOTIFICATION_TYPES[self.notification_type].frequency
        super(CompanyUserNotificationSubscription, self).save(*args, **kwargs)
