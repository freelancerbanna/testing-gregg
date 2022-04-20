# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('periods', '0009_auto_20160224_0234'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='period',
            options={'ordering': ('order',)},
        ),
        migrations.AddField(
            model_name='period',
            name='order',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='period',
            name='period_type',
            field=models.CharField(max_length=50, choices=[(b'month', b'Month'), (b'quarter', b'Quarter'), (b'year', b'Year')]),
        ),
    ]
