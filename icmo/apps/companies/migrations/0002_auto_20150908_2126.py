# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0002_auto_20150908_2126'),
        ('companies', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='share',
            name='created_by',
            field=models.ForeignKey(related_name='shares_granted', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='share',
            name='user',
            field=models.ForeignKey(related_name='shares', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='companyuserinvitation',
            name='company',
            field=models.ForeignKey(to='companies.Company'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='companyuserinvitation',
            name='inviting_user',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='companyuserinvitation',
            name='modified_by',
            field=models.ForeignKey(related_name='companyuserinvitation_last_modified', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='companyuserinvitation',
            name='user',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='companyusergroup',
            name='company',
            field=models.ForeignKey(to='companies.Company'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='companyusergroup',
            name='modified_by',
            field=models.ForeignKey(related_name='companyusergroup_last_modified', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='companyusergroup',
            unique_together=set([('company', 'name')]),
        ),
        migrations.AddField(
            model_name='companyuser',
            name='company',
            field=models.ForeignKey(related_name='users', to='companies.Company'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='companyuser',
            name='group',
            field=models.ForeignKey(to='companies.CompanyUserGroup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='companyuser',
            name='modified_by',
            field=models.ForeignKey(related_name='companyuser_last_modified', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='companyuser',
            name='user',
            field=models.ForeignKey(related_name='permissions', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='companyuser',
            unique_together=set([('company', 'user')]),
        ),
        migrations.AddField(
            model_name='company',
            name='account',
            field=models.ForeignKey(related_name='companies', to='billing.BillingAccount'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='company',
            name='modified_by',
            field=models.ForeignKey(related_name='company_last_modified', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='company',
            unique_together=set([('account', 'name'), ('account', 'slug')]),
        ),
    ]
