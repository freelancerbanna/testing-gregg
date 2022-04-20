# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from companies.models import AppPermissions


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    CompanyUserGroup = apps.get_model("companies", "CompanyUserGroup")
    db_alias = schema_editor.connection.alias
    CompanyUserGroup.objects.using(db_alias).filter(name='Admin').update(
        task_boards=AppPermissions.CHANGE)
    CompanyUserGroup.objects.using(db_alias).filter(name='Planner').update(
        task_boards=AppPermissions.CHANGE)
    CompanyUserGroup.objects.using(db_alias).filter(name='Updater').update(
        task_boards=AppPermissions.NONE)
    CompanyUserGroup.objects.using(db_alias).filter(name='Dashboards Only').update(
        task_boards=AppPermissions.NONE)


class Migration(migrations.Migration):
    dependencies = [
        ('companies', '0004_companyusergroup_task_boards'),
    ]

    operations = [
        migrations.RunPython(forwards_func),
    ]
