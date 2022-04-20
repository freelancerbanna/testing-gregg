# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('revenues', '0001_initial'),
        ('icmo_users', '0001_initial'),
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='icmouser',
            name='last_revenue_plan',
            field=models.ForeignKey(blank=True, editable=False, to='revenues.RevenuePlan', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='icmouser',
            name='user_permissions',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions'),
            preserve_default=True,
        ),
    ]
