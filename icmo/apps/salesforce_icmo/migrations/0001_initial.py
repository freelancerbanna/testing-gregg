# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal
import core.fields
import dirtyfields.dirtyfields
import djmoney.models.fields
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('revenues', '0006_auto_20160111_1529'),
        ('performance', '0008_auto_20160114_1957'),
        ('leads', '0009_auto_20160204_0310'),
        ('companies', '0005_auto_20151207_1749'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesforceAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sfdc_id', models.CharField(max_length=255)),
                ('sfdc_account_source', models.CharField(max_length=255)),
                ('sfdc_industry', models.CharField(max_length=255, blank=True)),
                ('sfdc_annual_revenue', models.BigIntegerField(null=True)),
                ('sfdc_created_date', models.DateTimeField()),
                ('sfdc_is_deleted', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='SalesforceCampaignToICMOCampaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('icmo_campaign', models.ForeignKey(related_name='salesforce_source', to='performance.Campaign')),
            ],
        ),
        migrations.CreateModel(
            name='SalesforceConnection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('access_token', models.CharField(max_length=255, blank=True)),
                ('expires_at', models.DateTimeField(null=True)),
                ('refresh_token', models.CharField(max_length=255, blank=True)),
                ('id_url', models.URLField(max_length=2048, blank=True)),
                ('instance_url', models.URLField(max_length=2048, blank=True)),
                ('signature', models.CharField(max_length=255, blank=True)),
                ('issued_at', models.CharField(max_length=255, blank=True)),
                ('last_sync', models.DateTimeField(auto_now=True, null=True)),
                ('company', models.OneToOneField(to='companies.Company')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SalesforceEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event_stage', models.CharField(max_length=255)),
                ('event_date', models.DateTimeField()),
                ('amount', models.DecimalField(null=True, max_digits=14, decimal_places=2)),
                ('connection', models.ForeignKey(to='salesforce_icmo.SalesforceConnection')),
            ],
        ),
        migrations.CreateModel(
            name='SalesforceLead',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sfdc_id', models.CharField(max_length=255)),
                ('sfdc_status', models.CharField(max_length=255)),
                ('sfdc_lead_source', models.CharField(max_length=255)),
                ('sfdc_industry', models.CharField(max_length=255, blank=True)),
                ('sfdc_annual_revenue', models.BigIntegerField(null=True)),
                ('sfdc_converted_date', models.DateTimeField(null=True)),
                ('sfdc_converted_account_id', models.CharField(max_length=255)),
                ('sfdc_converted_contact_id', models.CharField(max_length=255)),
                ('sfdc_converted_opportunity_id', models.CharField(max_length=255)),
                ('sfdc_created_date', models.DateTimeField()),
                ('sfdc_is_deleted', models.BooleanField()),
                ('connection', models.ForeignKey(related_name='leads', to='salesforce_icmo.SalesforceConnection')),
                ('salesforce_account', models.ForeignKey(related_name='salesforce_lead', blank=True, to='salesforce_icmo.SalesforceAccount', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SalesforceOpportunity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sfdc_id', models.CharField(max_length=255)),
                ('sfdc_account_id', models.CharField(max_length=255)),
                ('sfdc_amount', models.DecimalField(null=True, max_digits=14, decimal_places=2)),
                ('sfdc_close_date', models.DateTimeField(null=True)),
                ('sfdc_lead_source', models.CharField(max_length=255)),
                ('sfdc_stage_name', models.CharField(max_length=255)),
                ('sfdc_created_date', models.DateTimeField()),
                ('sfdc_is_deleted', models.BooleanField()),
                ('connection', models.ForeignKey(related_name='opportunities', to='salesforce_icmo.SalesforceConnection')),
                ('salesforce_account', models.ForeignKey(blank=True, to='salesforce_icmo.SalesforceAccount', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SalesforceRevenuePlan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('segment_mapping_field', models.CharField(default=b'industry', max_length=255, choices=[(b'industry', b'Company Industry'), (b'annualrevenue', b'Company Annual Revenue')])),
                ('connection', models.ForeignKey(related_name='connected_plans', to='salesforce_icmo.SalesforceConnection')),
                ('revenue_plan', models.OneToOneField(to='revenues.RevenuePlan')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SalesforceRevenuePlanCampaignMonthPerformance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('month', models.PositiveSmallIntegerField()),
                ('contacts', models.PositiveSmallIntegerField(default=0)),
                ('mql', models.PositiveSmallIntegerField(default=0)),
                ('sql', models.PositiveSmallIntegerField(default=0)),
                ('sales', models.PositiveSmallIntegerField(default=0)),
                ('sales_revenue_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('sales_revenue', core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=0, default_currency=b'USD')),
                ('connection', models.ForeignKey(to='salesforce_icmo.SalesforceConnection')),
                ('salesforce_revenue_plan', models.ForeignKey(to='salesforce_icmo.SalesforceRevenuePlan')),
            ],
            options={
                'ordering': ('salesforce_revenue_plan_campaign', 'month'),
            },
        ),
        migrations.CreateModel(
            name='SalesforceRevenuePlanProgramMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.CharField(max_length=255)),
                ('map_type', models.CharField(default=b'source', max_length=50, choices=[(b'source', b'Source'), (b'campaign', b'Campaign')])),
                ('programs', models.ManyToManyField(to='leads.Program')),
                ('salesforce_revenue_plan', models.ForeignKey(to='salesforce_icmo.SalesforceRevenuePlan')),
            ],
            options={
                'ordering': ('map_type', 'name'),
            },
        ),
        migrations.CreateModel(
            name='SalesforceRevenuePlanSegmentMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mapping_field', models.CharField(max_length=255, choices=[(b'industry', b'Company Industry'), (b'annualrevenue', b'Company Annual Revenue')])),
                ('sfdc_value_1', models.CharField(max_length=255, blank=True)),
                ('sfdc_value_2', models.CharField(max_length=255, blank=True)),
                ('revenue_plan', models.ForeignKey(to='revenues.RevenuePlan')),
                ('salesforce_revenue_plan', models.ForeignKey(related_name='segment_map', to='salesforce_icmo.SalesforceRevenuePlan')),
                ('segment', models.ForeignKey(blank=True, to='revenues.Segment', null=True)),
            ],
            options={
                'ordering': ('sfdc_value_1',),
            },
        ),
        migrations.CreateModel(
            name='SalesforceVirtualContact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lead_source', models.CharField(max_length=255)),
                ('lead_source_slug', models.CharField(max_length=255)),
                ('industry', models.CharField(max_length=255, blank=True)),
                ('annual_revenue', models.BigIntegerField(null=True)),
                ('is_virtual', models.BooleanField(default=False)),
                ('connection', models.ForeignKey(related_name='virtual_contacts', to='salesforce_icmo.SalesforceConnection')),
                ('salesforce_account', models.OneToOneField(related_name='virtual_contact', null=True, to='salesforce_icmo.SalesforceAccount')),
                ('salesforce_lead', models.OneToOneField(related_name='virtual_contact', null=True, to='salesforce_icmo.SalesforceLead')),
            ],
        ),
        migrations.AddField(
            model_name='salesforcerevenueplancampaignmonthperformance',
            name='salesforce_revenue_plan_campaign',
            field=models.ForeignKey(to='salesforce_icmo.SalesforceRevenuePlanProgramMap'),
        ),
        migrations.AddField(
            model_name='salesforcerevenueplancampaignmonthperformance',
            name='segment',
            field=models.ForeignKey(to='revenues.Segment'),
        ),
        migrations.AddField(
            model_name='salesforcelead',
            name='salesforce_opportunity',
            field=models.ForeignKey(related_name='salesforce_lead', blank=True, to='salesforce_icmo.SalesforceOpportunity', null=True),
        ),
        migrations.AddField(
            model_name='salesforceevent',
            name='virtual_contact',
            field=models.ForeignKey(to='salesforce_icmo.SalesforceVirtualContact'),
        ),
        migrations.AddField(
            model_name='salesforcecampaigntoicmocampaign',
            name='salesforce_campaign',
            field=models.ForeignKey(related_name='icmo_campaigns', to='salesforce_icmo.SalesforceRevenuePlanProgramMap'),
        ),
        migrations.AddField(
            model_name='salesforceaccount',
            name='connection',
            field=models.ForeignKey(related_name='accounts', to='salesforce_icmo.SalesforceConnection'),
        ),
    ]
