# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0003_auto_20150922_1747'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyUserNotificationSubscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('notification_type', models.CharField(max_length=255, choices=[(b'task_overdue', b'Task Overdue')])),
                ('frequency', models.CharField(max_length=255, editable=False)),
                ('params', models.TextField(blank=True)),
                ('params_display', models.TextField(blank=True)),
                ('company', models.ForeignKey(to='companies.Company')),
                ('company_user', models.ForeignKey(to='companies.CompanyUser')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
            bases=(models.Model,),
        ),
    ]
