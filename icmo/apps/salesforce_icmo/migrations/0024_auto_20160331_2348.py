# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import dirtyfields.dirtyfields


class Migration(migrations.Migration):

    dependencies = [
        ('revenues', '0007_auto_20160211_1818'),
        ('performance', '0012_auto_20160314_1850'),
        ('leads', '0010_auto_20160314_1850'),
        ('salesforce_icmo', '0023_salesforcevirtualcontact_segment_field_text_value_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesforceRevenuePlanMapEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('segment_value', models.CharField(max_length=255)),
                ('source_value', models.CharField(max_length=255)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='performance.Campaign', null=True)),
                ('connection', models.ForeignKey(to='salesforce_icmo.SalesforceConnection')),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='leads.Program', null=True)),
                ('revenue_plan', models.ForeignKey(to='revenues.RevenuePlan')),
                ('salesforce_revenue_plan', models.ForeignKey(related_name='map_entries', to='salesforce_icmo.SalesforceRevenuePlan')),
                ('segment', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='revenues.Segment', null=True)),
            ],
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.RemoveField(
            model_name='salesforcecampaigntoicmocampaign',
            name='icmo_campaign',
        ),
        migrations.RemoveField(
            model_name='salesforcecampaigntoicmocampaign',
            name='salesforce_campaign',
        ),
        migrations.RemoveField(
            model_name='salesforceleadhistory',
            name='connection',
        ),
        migrations.RemoveField(
            model_name='salesforceleadhistory',
            name='salesforce_lead',
        ),
        migrations.RemoveField(
            model_name='salesforcerevenueplancampaignmonthperformance',
            name='connection',
        ),
        migrations.RemoveField(
            model_name='salesforcerevenueplancampaignmonthperformance',
            name='salesforce_revenue_plan',
        ),
        migrations.RemoveField(
            model_name='salesforcerevenueplancampaignmonthperformance',
            name='salesforce_revenue_plan_campaign',
        ),
        migrations.RemoveField(
            model_name='salesforcerevenueplancampaignmonthperformance',
            name='segment',
        ),
        migrations.RemoveField(
            model_name='salesforcerevenueplanprogrammap',
            name='programs',
        ),
        migrations.RemoveField(
            model_name='salesforcerevenueplanprogrammap',
            name='salesforce_revenue_plan',
        ),
        migrations.RemoveField(
            model_name='salesforcerevenueplansegmentmap',
            name='revenue_plan',
        ),
        migrations.RemoveField(
            model_name='salesforcerevenueplansegmentmap',
            name='salesforce_revenue_plan',
        ),
        migrations.RemoveField(
            model_name='salesforcerevenueplansegmentmap',
            name='segment',
        ),
        migrations.DeleteModel(
            name='SalesforceCampaignToICMOCampaign',
        ),
        migrations.DeleteModel(
            name='SalesforceLeadHistory',
        ),
        migrations.DeleteModel(
            name='SalesforceRevenuePlanCampaignMonthPerformance',
        ),
        migrations.DeleteModel(
            name='SalesforceRevenuePlanProgramMap',
        ),
        migrations.DeleteModel(
            name='SalesforceRevenuePlanSegmentMap',
        ),
    ]
