# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('billing', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='billingcontract',
            name='signing_user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='billingcontract',
            name='subscription',
            field=models.ForeignKey(to='billing.Subscription'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='billingaccount',
            name='active_subscription',
            field=models.ForeignKey(related_name='active_for_account', blank=True, to='billing.Subscription', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='billingaccount',
            name='billing_company',
            field=models.ForeignKey(blank=True, to='companies.Company', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='billingaccount',
            name='modified_by',
            field=models.ForeignKey(related_name='billingaccount_last_modified', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='billingaccount',
            name='owner',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
