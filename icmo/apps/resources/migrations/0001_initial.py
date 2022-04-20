# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import dirtyfields.dirtyfields
import django_extensions.db.fields
import mptt.fields
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('revenues', '0001_initial'),
        ('budgets', '0002_budgetlineitem_company'),
        ('companies', '0002_auto_20150908_2126'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GanttDependency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dependency_id', django_extensions.db.fields.ShortUUIDField(unique=True, editable=False, blank=True)),
                ('item_type', models.PositiveSmallIntegerField(choices=[(0, b'Finish-Finish'), (1, b'Finish-Start'), (2, b'Start-Finish'), (3, b'Start-Start')])),
                ('company', models.ForeignKey(to='companies.Company')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GanttTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('order', models.PositiveIntegerField(editable=False, db_index=True)),
                ('slug', django_extensions.db.fields.AutoSlugField(populate_from=b'name', editable=False, blank=True)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('expanded', models.BooleanField(default=False)),
                ('percent_complete', models.SmallIntegerField(default=0)),
                ('summary', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=255, blank=True)),
                ('description', models.TextField(blank=True)),
                ('past_due', models.BooleanField(default=False)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('budget_line_item', models.OneToOneField(null=True, blank=True, to='budgets.BudgetLineItem')),
                ('company', models.ForeignKey(to='companies.Company')),
                ('modified_by', models.ForeignKey(related_name='gantttask_last_modified', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', blank=True, to='resources.GanttTask', null=True)),
                ('revenue_plan', models.ForeignKey(to='revenues.RevenuePlan')),
                ('segment', models.ForeignKey(to='revenues.Segment')),
            ],
            options={
                'ordering': ('order',),
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SchedulerEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', django_extensions.db.fields.ShortUUIDField(unique=True, editable=False, blank=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('start_datetime', models.DateTimeField()),
                ('end_datetime', models.DateTimeField()),
                ('is_all_day', models.BooleanField(default=False)),
                ('recurrence_exception', models.TextField(blank=True)),
                ('recurrence_rule', models.TextField(blank=True)),
                ('company', models.ForeignKey(to='companies.Company')),
                ('gantt_task', models.OneToOneField(null=True, blank=True, to='resources.GanttTask')),
                ('icmo_user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('recurrence', models.ForeignKey(blank=True, to='resources.SchedulerEvent', null=True)),
                ('revenue_plan', models.ForeignKey(blank=True, to='revenues.RevenuePlan', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('assignment_id', django_extensions.db.fields.ShortUUIDField(unique=True, editable=False, blank=True)),
                ('value', models.PositiveSmallIntegerField(default=0)),
                ('company', models.ForeignKey(to='companies.Company')),
                ('resource', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('revenue_plan', models.ForeignKey(to='revenues.RevenuePlan')),
                ('segment', models.ForeignKey(to='revenues.Segment')),
                ('task', models.ForeignKey(to='resources.GanttTask')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='gantttask',
            unique_together=set([('segment', 'slug')]),
        ),
        migrations.AddField(
            model_name='ganttdependency',
            name='predecessor',
            field=models.ForeignKey(related_name='successors', blank=True, to='resources.GanttTask', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ganttdependency',
            name='revenue_plan',
            field=models.ForeignKey(to='revenues.RevenuePlan'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ganttdependency',
            name='segment',
            field=models.ForeignKey(to='revenues.Segment'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ganttdependency',
            name='successor',
            field=models.ForeignKey(related_name='predecessors', blank=True, to='resources.GanttTask', null=True),
            preserve_default=True,
        ),
    ]
