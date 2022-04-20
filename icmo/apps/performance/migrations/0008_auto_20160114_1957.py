# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('performance', '0007_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='source',
            field=models.IntegerField(default=1, verbose_name='Source', choices=[(1, b'Manual'), (2, b'Salesforce'), (3, b'HubSpot')]),
        ),
    ]
