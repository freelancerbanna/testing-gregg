# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cloudinary.models
import dirtyfields.dirtyfields
import django_extensions.db.fields
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('name', models.CharField(max_length=150, verbose_name='Company Name')),
                ('slug', django_extensions.db.fields.AutoSlugField(populate_from=b'name', editable=False, blank=True)),
                ('website', models.URLField(max_length=150, blank=True)),
                ('address1', models.CharField(max_length=255, verbose_name='Address 1')),
                ('address2', models.CharField(max_length=255, verbose_name='Address 2', blank=True)),
                ('city', models.CharField(max_length=75)),
                ('state', models.CharField(max_length=2, choices=[(b'', b''), (b'AL', b'Alabama'), (b'AK', b'Alaska'), (b'AB', 'Alberta'), (b'AS', b'American Samoa'), (b'AZ', b'Arizona'), (b'AR', b'Arkansas'), (b'AA', b'Armed Forces Americas'), (b'AE', b'Armed Forces Europe'), (b'AP', b'Armed Forces Pacific'), (b'BC', 'British Columbia'), (b'CA', b'California'), (b'CO', b'Colorado'), (b'CT', b'Connecticut'), (b'DE', b'Delaware'), (b'DC', b'District of Columbia'), (b'FL', b'Florida'), (b'GA', b'Georgia'), (b'GU', b'Guam'), (b'HI', b'Hawaii'), (b'ID', b'Idaho'), (b'IL', b'Illinois'), (b'IN', b'Indiana'), (b'IA', b'Iowa'), (b'KS', b'Kansas'), (b'KY', b'Kentucky'), (b'LA', b'Louisiana'), (b'ME', b'Maine'), (b'MB', 'Manitoba'), (b'MD', b'Maryland'), (b'MA', b'Massachusetts'), (b'MI', b'Michigan'), (b'MN', b'Minnesota'), (b'MS', b'Mississippi'), (b'MO', b'Missouri'), (b'MT', b'Montana'), (b'NE', b'Nebraska'), (b'NV', b'Nevada'), (b'NB', 'New Brunswick'), (b'NH', b'New Hampshire'), (b'NJ', b'New Jersey'), (b'NM', b'New Mexico'), (b'NY', b'New York'), (b'NL', 'Newfoundland and Labrador'), (b'NC', b'North Carolina'), (b'ND', b'North Dakota'), (b'MP', b'Northern Mariana Islands'), (b'NT', 'Northwest Territories'), (b'NS', 'Nova Scotia'), (b'NU', 'Nunavut'), (b'OH', b'Ohio'), (b'OK', b'Oklahoma'), (b'ON', 'Ontario'), (b'OR', b'Oregon'), (b'PA', b'Pennsylvania'), (b'PE', 'Prince Edward Island'), (b'PR', b'Puerto Rico'), (b'QC', 'Quebec'), (b'RI', b'Rhode Island'), (b'SK', 'Saskatchewan'), (b'SC', b'South Carolina'), (b'SD', b'South Dakota'), (b'TN', b'Tennessee'), (b'TX', b'Texas'), (b'UT', b'Utah'), (b'VT', b'Vermont'), (b'VI', b'Virgin Islands'), (b'VA', b'Virginia'), (b'WA', b'Washington'), (b'WV', b'West Virginia'), (b'WI', b'Wisconsin'), (b'WY', b'Wyoming'), (b'YT', 'Yukon')])),
                ('zip', models.CharField(max_length=12)),
                ('country', models.CharField(default=b'US', max_length=3, choices=[(b'', b''), (b'US', b'United States'), (b'CA', b'Canada')])),
                ('logo', cloudinary.models.CloudinaryField(max_length=255, null=True, blank=True)),
                ('fiscal_year_start', models.PositiveSmallIntegerField(default=1, choices=[(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')])),
            ],
            options={
                'verbose_name_plural': 'Companies',
                'permissions': (('view_company', 'View company'),),
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='CompanyUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('slug', django_extensions.db.fields.AutoSlugField(populate_from=(b'company', b'user'), editable=False, blank=True)),
                ('title', models.CharField(max_length=75, blank=True)),
                ('owner', models.BooleanField(default=False)),
                ('permitted_segments_list', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='CompanyUserGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('slug', django_extensions.db.fields.AutoSlugField(populate_from=b'name', editable=False, blank=True)),
                ('name', models.CharField(max_length=255)),
                ('editable', models.BooleanField(default=True, help_text=b'Some default plans should never be deleted or edited by the user')),
                ('revenue_plans', models.CharField(default=b'none', max_length=50, choices=[(b'none', b'None'), (b'view', b'View'), (b'change', b'Change')])),
                ('program_mix', models.CharField(default=b'none', max_length=50, choices=[(b'none', b'None'), (b'view', b'View'), (b'change', b'Change')])),
                ('budgets', models.CharField(default=b'none', max_length=50, choices=[(b'none', b'None'), (b'view', b'View'), (b'change', b'Change')])),
                ('performance', models.CharField(default=b'none', max_length=50, choices=[(b'none', b'None'), (b'view', b'View'), (b'change', b'Change')])),
                ('resources', models.CharField(default=b'none', max_length=50, choices=[(b'none', b'None'), (b'view', b'View'), (b'change', b'Change')])),
                ('timeline', models.CharField(default=b'none', max_length=50, choices=[(b'none', b'None'), (b'view', b'View'), (b'change', b'Change')])),
                ('dashboards', models.CharField(default=b'none', max_length=50, choices=[(b'none', b'None'), (b'view', b'View'), (b'change', b'Change')])),
                ('permissions', models.CharField(default=b'none', max_length=50, choices=[(b'none', b'None'), (b'view', b'View'), (b'change', b'Change')])),
                ('live_plan_only', models.BooleanField(default=True)),
                ('permitted_segments_list', models.TextField(help_text=b'Restrict this group to certain segments.  Each exact segment name should be entered on a separate line.  Note, in the case that all of the segments a user has access to are not found or are inactive, users from  this group will not be able to access anything.', blank=True)),
                ('publish_plans', models.BooleanField(default=False)),
                ('archive_plans', models.BooleanField(default=False)),
                ('share', models.CharField(default=b'none', max_length=50, choices=[(b'none', b'None'), (b'none', b'View'), (b'none', b'Change')])),
                ('moderate_shares', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='CompanyUserInvitation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('target_email', models.EmailField(max_length=255)),
                ('is_new_user', models.BooleanField(default=False)),
                ('accepted', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Share',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('application_name', models.CharField(max_length=25, verbose_name='Application Name')),
                ('object_name', models.CharField(max_length=25, verbose_name='Object Name')),
                ('object_id', models.IntegerField(verbose_name='Object ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
