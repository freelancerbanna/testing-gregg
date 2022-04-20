from django.db.models.signals import post_delete
from django.dispatch import receiver

from companies.models import CompanyUser
from demos.models import DemoAccount


@receiver(post_delete, sender=DemoAccount, dispatch_uid='demo_account_post_delete')
def demo_account_post_delete(sender, instance, *args, **kwargs):
    for cu in CompanyUser.objects.filter(company=instance.company):
        if cu.user.companies.all().count() == 1:
            cu.user.delete()
    instance.company.delete()
