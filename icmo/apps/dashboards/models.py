from django.db import models
from django_extensions.db.fields import AutoSlugField
from core.models import IcmoModel


class Dashboard(IcmoModel):
    class Meta:
        unique_together = ('company', 'slug')
    slug = AutoSlugField(populate_from=('company', 'name'))
    company = models.ForeignKey('companies.Company', blank=True, null=True)
    user = models.ForeignKey('icmo_users.IcmoUser', blank=True, null=True)
    name = models.CharField(max_length=255)
