# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0004_program_fixed_budget'),
    ]

    operations = [
        migrations.AlterField(
            model_name='program',
            name='roi',
            field=models.IntegerField(default=0, editable=False),
        ),
    ]
