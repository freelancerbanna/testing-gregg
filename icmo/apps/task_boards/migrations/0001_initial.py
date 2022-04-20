# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import dirtyfields.dirtyfields
import django_extensions.db.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('leads', '0003_program_contacts_to_mql_conversion'),
        ('resources', '0004_gantttask_completed_date'),
        ('companies', '0005_auto_20151207_1749'),
        ('budgets', '0004_auto_20150922_1747'),
        ('revenues', '0005_auto_20151006_1944'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('order', models.PositiveIntegerField(editable=False, db_index=True)),
                ('uuid', django_extensions.db.fields.ShortUUIDField(db_index=True, editable=False, blank=True)),
                ('name', models.CharField(default=b'New Task', max_length=150, blank=True)),
                ('description', models.TextField(blank=True)),
                ('task_type', models.CharField(blank=True, max_length=255, null=True, choices=[(b'email', b'Email'), (b'email_design', b'Email Design'), (b'email_content', b'Email Content'), (b'landing_page_design', b'Landing Page Design'), (b'landing_page_content', b'Landing Page Content'), (b'content', b'Content')])),
                ('status', models.CharField(default=b'unstarted', max_length=255, blank=True, choices=[(b'unstarted', b'Unstarted'), (b'started', b'Started'), (b'finished', b'Finished'), (b'delivered', b'Delivered'), (b'rejected', b'Rejected'), (b'accepted', b'Accepted')])),
                ('priority', models.CharField(default=b'normal', max_length=255, blank=True, choices=[(b'low', b'Low'), (b'normal', b'Normal'), (b'high', b'High')])),
                ('start_date', models.DateTimeField(null=True, blank=True)),
                ('end_date', models.DateTimeField(null=True, blank=True)),
                ('private', models.BooleanField(default=False)),
                ('budget_line_item', models.ForeignKey(blank=True, to='budgets.BudgetLineItem', null=True)),
                ('gantt_task', models.ForeignKey(blank=True, to='resources.GanttTask', null=True)),
                ('modified_by', models.ForeignKey(related_name='task_last_modified', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('program', models.ForeignKey(blank=True, to='leads.Program', null=True)),
                ('segment', models.ForeignKey(blank=True, to='revenues.Segment', null=True)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='TaskBoard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('name', models.CharField(max_length=150)),
                ('slug', django_extensions.db.fields.AutoSlugField(populate_from=b'name', editable=False, blank=True)),
                ('company', models.ForeignKey(to='companies.Company')),
                ('modified_by', models.ForeignKey(related_name='taskboard_last_modified', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('revenue_plan', models.ForeignKey(to='revenues.RevenuePlan')),
            ],
            options={
                'ordering': ('-name',),
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='TaskCheckListItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('order', models.PositiveIntegerField(editable=False, db_index=True)),
                ('uuid', django_extensions.db.fields.ShortUUIDField(db_index=True, editable=False, blank=True)),
                ('name', models.CharField(max_length=2048)),
                ('completed', models.BooleanField(default=False)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(related_name='checklist', to='task_boards.Task')),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TaskComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('uuid', django_extensions.db.fields.ShortUUIDField(db_index=True, editable=False, blank=True)),
                ('comment', models.TextField()),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(related_name='comments', to='task_boards.Task')),
            ],
            options={
                'ordering': ('created',),
            },
        ),
        migrations.CreateModel(
            name='TaskList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('order', models.PositiveIntegerField(editable=False, db_index=True)),
                ('uuid', django_extensions.db.fields.ShortUUIDField(db_index=True, editable=False, blank=True)),
                ('name', models.CharField(default=b'New Task List', max_length=150)),
                ('modified_by', models.ForeignKey(related_name='tasklist_last_modified', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('task_board', models.ForeignKey(to='task_boards.TaskBoard')),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='TaskTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', django_extensions.db.fields.ShortUUIDField(db_index=True, editable=False, blank=True)),
                ('name', models.CharField(max_length=255)),
                ('task_board', models.ForeignKey(to='task_boards.TaskBoard')),
            ],
        ),
        migrations.CreateModel(
            name='TaskUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(max_length=255, choices=[(b'owner', b'Owner'), (b'approver', b'Approver'), (b'reviewer', b'Reviewer')])),
                ('task', models.ForeignKey(related_name='assigned_users', to='task_boards.Task')),
                ('user', models.ForeignKey(related_name='assigned_tasks', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='task',
            name='tags',
            field=models.ManyToManyField(to='task_boards.TaskTag'),
        ),
        migrations.AddField(
            model_name='task',
            name='task_board',
            field=models.ForeignKey(to='task_boards.TaskBoard'),
        ),
        migrations.AddField(
            model_name='task',
            name='task_list',
            field=models.ForeignKey(to='task_boards.TaskList'),
        ),
        migrations.AddField(
            model_name='task',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='task_boards.TaskUser'),
        ),
        migrations.AlterUniqueTogether(
            name='tasktag',
            unique_together=set([('task_board', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='taskboard',
            unique_together=set([('slug', 'revenue_plan')]),
        ),
    ]
