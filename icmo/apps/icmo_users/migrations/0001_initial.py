# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import timezone_field.fields
import django_extensions.db.fields
import django_extensions.db.fields.json
import localflavor.us.models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IcmoUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(max_length=30, verbose_name='First Name')),
                ('last_name', models.CharField(max_length=30, verbose_name='Last Name')),
                ('email', models.EmailField(unique=True, max_length=75, verbose_name='Email')),
                ('phone_number', localflavor.us.models.PhoneNumberField(max_length=20, blank=True)),
                ('title', models.CharField(help_text=b'Title Override', max_length=255, blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='Staff status')),
                ('is_admin', models.BooleanField(default=False, help_text='Designates whether the user is an admin', verbose_name='Admin status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting billing.', verbose_name='Active')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='Date joined')),
                ('activation_token', django_extensions.db.fields.ShortUUIDField(unique=True, editable=False, blank=True)),
                ('company', models.CharField(help_text=b'Company Name Override', max_length=255, null=True, blank=True)),
                ('timezone', timezone_field.fields.TimeZoneField(default=b'America/Los_Angeles')),
                ('companies', models.ManyToManyField(to='companies.Company', through='companies.CompanyUser')),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', verbose_name='groups')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Referral',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=75, verbose_name='email address')),
                ('message', models.TextField(null=True, blank=True)),
                ('date_sent', models.DateTimeField(default=None, null=True, verbose_name='date sent')),
                ('referrer', models.ForeignKey(related_name='referrals', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SignupLead',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('first_name', models.CharField(max_length=30, editable=False, blank=True)),
                ('last_name', models.CharField(max_length=30, editable=False, blank=True)),
                ('email', models.EmailField(unique=True, max_length=75, editable=False)),
                ('phone_number', localflavor.us.models.PhoneNumberField(max_length=20, editable=False, blank=True)),
                ('title', models.CharField(max_length=255, editable=False, blank=True)),
                ('company_name', models.CharField(max_length=255, editable=False, blank=True)),
                ('fields', django_extensions.db.fields.json.JSONField(editable=False)),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Suggestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField(null=True, blank=True)),
                ('date_sent', models.DateTimeField(default=None, null=True, verbose_name='date sent')),
                ('user', models.ForeignKey(related_name='suggestions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
