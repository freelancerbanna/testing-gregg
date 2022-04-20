from django.db.models.signals import post_save
from django.dispatch import receiver

from resources.models import GanttTask
from .helpers import BaseNotification


class TaskOverdueNotification(BaseNotification):
    slug = 'task_overdue'
    name = 'Task Overdue'
    frequency = 'occurrence'


@receiver(post_save, sender=GanttTask, dispatch_uid='company_post_save_handler')
def gantttask_notifications(sender, instance, *args, **kwargs):
    from .models import CompanyUserNotificationSubscription
    if 'past_due' in instance.get_dirty_fields() and instance.past_due:
        task_emails = [item.resource.email for item in instance.usertask_set.all()]
        for sub in CompanyUserNotificationSubscription.objects.filter(
                company=instance.company,
                notification_type='task_overdue',
                company_user__user__email__in=task_emails):
            sub.send_notification(TaskOverdueNotification, instance)
