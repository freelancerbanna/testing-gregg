# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0006_auto_20160125_2350'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='item_type',
            field=models.CharField(default=b'program', max_length=10, choices=[(b'channel', b'Channel'), (b'program', b'Program')]),
        ),
        migrations.AddField(
            model_name='program',
            name='level',
            field=models.PositiveIntegerField(default=0, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='program',
            name='lft',
            field=models.PositiveIntegerField(default=0, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='program',
            name='order',
            field=models.PositiveIntegerField(default=1, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='program',
            name='parent',
            field=mptt.fields.TreeForeignKey(related_name='children', blank=True, to='leads.Program', null=True),
        ),
        migrations.AddField(
            model_name='program',
            name='rght',
            field=models.PositiveIntegerField(default=0, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='program',
            name='tree_id',
            field=models.PositiveIntegerField(default=0, editable=False, db_index=True),
            preserve_default=False,
        ),
    ]
