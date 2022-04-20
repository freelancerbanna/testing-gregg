# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('periods', '0007_auto_20150930_1955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='period',
            name='roi_actual',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='period',
            name='roi_plan',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='period',
            name='roi_variance',
            field=models.IntegerField(default=0, editable=False),
        ),
    ]
