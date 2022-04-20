# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0007_auto_20160127_1754'),
    ]

    operations = [
        migrations.AlterField(
            model_name='program',
            name='item_type',
            field=models.CharField(default=b'program', max_length=10, choices=[(b'category', b'Category'), (b'program', b'Program')]),
        ),
    ]
