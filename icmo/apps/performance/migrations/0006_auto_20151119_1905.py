# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('performance', '0005_auto_20150930_1955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='source',
            field=models.IntegerField(default=1, verbose_name='Source', choices=[(1, 'Manual'), (2, 'Sales Force'), (3, 'HubSpot')]),
            preserve_default=True,
        ),
    ]
