# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('revenues', '0006_auto_20160111_1529'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='revenueplan',
            unique_together=set([('slug', 'company')]),
        ),
    ]
