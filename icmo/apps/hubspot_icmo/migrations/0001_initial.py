# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import dirtyfields.dirtyfields
import django_extensions.db.fields
from decimal import Decimal
import core.fields
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('revenues', '0006_auto_20160111_1529'),
        ('performance', '0008_auto_20160114_1957'),
        ('leads', '0003_program_contacts_to_mql_conversion'),
        ('companies', '0005_auto_20151207_1749'),
    ]

    operations = [
        migrations.CreateModel(
            name='HubspotCampaignToICMOCampaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='HubspotCompany',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hs_company_id', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=1024)),
                ('annualrevenue', models.IntegerField(null=True, blank=True)),
                ('industry', models.CharField(max_length=255, blank=True)),
                ('state', models.CharField(max_length=255, blank=True)),
                ('city', models.CharField(max_length=255, blank=True)),
                ('country', models.CharField(max_length=255, blank=True)),
                ('company', models.ForeignKey(to='companies.Company')),
            ],
        ),
        migrations.CreateModel(
            name='HubspotConnection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('hub_id', models.CharField(help_text=b'Log into HubSpot to find your Hub ID in the upper righthand corner of the HubSpot application.', max_length=255)),
                ('access_token', models.CharField(max_length=255)),
                ('expires_at', models.DateTimeField(null=True)),
                ('refresh_token', models.CharField(max_length=255)),
                ('last_sync', models.DateTimeField(auto_now=True, null=True)),
                ('contacts_last_modified_date', models.DateTimeField(null=True, blank=True)),
                ('company', models.OneToOneField(to='companies.Company')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
        ),
        migrations.CreateModel(
            name='HubspotContact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vid', models.PositiveIntegerField()),
                ('associatedcompanyid', models.CharField(max_length=255, blank=True)),
                ('current_lifecyclestage', models.CharField(max_length=255)),
                ('hs_analytics_first_url', models.URLField(max_length=2048)),
                ('hs_analytics_source', models.CharField(max_length=255)),
                ('hs_analytics_source_data_1', models.CharField(max_length=2048)),
                ('hs_analytics_source_data_2', models.CharField(max_length=2048)),
                ('industry', models.CharField(max_length=255)),
                ('annualrevenue', models.PositiveIntegerField(null=True, blank=True)),
                ('campaign_name_guess', models.CharField(default=b'Unknown', max_length=255)),
                ('campaign_name_slug', models.CharField(max_length=255)),
                ('remote_timestamp', models.DateTimeField(null=True)),
                ('company', models.ForeignKey(to='companies.Company')),
                ('connection', models.ForeignKey(related_name='contacts', to='hubspot_icmo.HubspotConnection')),
            ],
        ),
        migrations.CreateModel(
            name='HubspotContactEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event_date', models.DateTimeField()),
                ('event_stage', models.CharField(max_length=50, choices=[(b'subscriber', b'Subscriber'), (b'lead', b'Lead'), (b'marketingqualifiedlead', b'Marketingqualifiedlead'), (b'salesqualifiedlead', b'Salesqualifiedlead'), (b'opportunity', b'Opportunity'), (b'customer', b'Customer')])),
                ('company', models.ForeignKey(to='companies.Company')),
                ('connection', models.ForeignKey(related_name='events', to='hubspot_icmo.HubspotConnection')),
                ('contact', models.ForeignKey(related_name='events', to='hubspot_icmo.HubspotContact')),
            ],
        ),
        migrations.CreateModel(
            name='HubspotDeal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deal_id', models.CharField(max_length=255)),
                ('contact_vid', models.CharField(max_length=255, blank=True)),
                ('hs_company_id', models.CharField(max_length=255, blank=True)),
                ('dealname', models.CharField(max_length=255)),
                ('amount_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('amount', core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=2)),
                ('dealstage', models.CharField(max_length=255)),
                ('dealstage_last_modified', models.DateTimeField()),
                ('closedwon_date', models.DateTimeField(null=True, blank=True)),
                ('company', models.ForeignKey(to='companies.Company')),
                ('connection', models.ForeignKey(related_name='deals', to='hubspot_icmo.HubspotConnection')),
                ('contact', models.ForeignKey(blank=True, to='hubspot_icmo.HubspotContact', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='HubspotRevenuePlan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('segment_mapping_field', models.CharField(default=b'industry', max_length=255, choices=[(b'industry', b'Company Industry'), (b'annualrevenue', b'Company Annual Revenue')])),
                ('connection', models.ForeignKey(related_name='connected_plans', to='hubspot_icmo.HubspotConnection')),
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
            name='HubspotRevenuePlanCampaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.CharField(max_length=255)),
                ('hubspot_revenue_plan', models.ForeignKey(to='hubspot_icmo.HubspotRevenuePlan')),
                ('programs', models.ManyToManyField(to='leads.Program')),
                ('revenue_plan', models.ForeignKey(to='revenues.RevenuePlan')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='HubspotRevenuePlanCampaignMonthPerformance',
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
                ('sales_revenue', core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=0)),
                ('connection', models.ForeignKey(to='hubspot_icmo.HubspotConnection')),
                ('hubspot_revenue_plan', models.ForeignKey(to='hubspot_icmo.HubspotRevenuePlan')),
                ('hubspot_revenue_plan_campaign', models.ForeignKey(to='hubspot_icmo.HubspotRevenuePlanCampaign')),
                ('segment', models.ForeignKey(to='revenues.Segment')),
            ],
            options={
                'ordering': ('hubspot_revenue_plan_campaign', 'month'),
            },
        ),
        migrations.CreateModel(
            name='HubspotRevenuePlanSegmentMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mapping_field', models.CharField(max_length=255, choices=[(b'industry', b'Company Industry'), (b'annualrevenue', b'Company Annual Revenue')])),
                ('hs_value_1', models.CharField(max_length=255, blank=True)),
                ('hs_value_2', models.CharField(max_length=255, blank=True)),
                ('hubspot_revenue_plan', models.ForeignKey(related_name='segment_map', to='hubspot_icmo.HubspotRevenuePlan')),
                ('revenue_plan', models.ForeignKey(to='revenues.RevenuePlan')),
                ('segment', models.ForeignKey(blank=True, to='revenues.Segment', null=True)),
            ],
            options={
                'ordering': ('hs_value_1',),
            },
        ),
        migrations.AddField(
            model_name='hubspotcompany',
            name='connection',
            field=models.ForeignKey(related_name='hs_companies', to='hubspot_icmo.HubspotConnection'),
        ),
        migrations.AddField(
            model_name='hubspotcampaigntoicmocampaign',
            name='hubspot_campaign',
            field=models.ForeignKey(related_name='icmo_campaigns', to='hubspot_icmo.HubspotRevenuePlanCampaign'),
        ),
        migrations.AddField(
            model_name='hubspotcampaigntoicmocampaign',
            name='icmo_campaign',
            field=models.ForeignKey(related_name='hubspot_campaigns', to='performance.Campaign'),
        ),
    ]
