# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('periods', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='period',
            name='touches_actual',
            field=models.IntegerField(default=0, editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='period',
            name='touches_per_contact_actual',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='period',
            name='touches_per_contact_plan',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='period',
            name='touches_per_contact_variance',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='period',
            name='touches_plan',
            field=models.IntegerField(default=0, editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='period',
            name='touches_variance',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
