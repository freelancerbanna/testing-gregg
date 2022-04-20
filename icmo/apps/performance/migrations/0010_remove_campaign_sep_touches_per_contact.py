# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('performance', '0009_auto_20160309_1703'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaign',
            name='sep_touches_per_contact',
        ),
    ]
