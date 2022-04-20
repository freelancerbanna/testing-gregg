# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0004_gantttask_completed_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ganttdependency',
            name='segment',
            field=models.ForeignKey(blank=True, to='revenues.Segment', null=True),
        ),
        migrations.AlterField(
            model_name='gantttask',
            name='segment',
            field=models.ForeignKey(blank=True, to='revenues.Segment', null=True),
        ),
        migrations.AlterField(
            model_name='usertask',
            name='segment',
            field=models.ForeignKey(blank=True, to='revenues.Segment', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='gantttask',
            unique_together=set([('revenue_plan', 'slug')]),
        ),
    ]
