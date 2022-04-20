# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('periods', '0008_auto_20160202_1646'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='period',
            options={'ordering': ('-modified', '-created'), 'get_latest_by': 'modified'},
        ),
        migrations.AddField(
            model_name='period',
            name='unique_id',
            field=models.CharField(default='2016224234562550816395', unique=True, max_length=255),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='period',
            unique_together=set([]),
        ),
    ]
