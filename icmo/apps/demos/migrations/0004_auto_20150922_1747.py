# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('demos', '0003_demoaccount_template'),
    ]

    operations = [
        migrations.AlterField(
            model_name='demoaccount',
            name='created',
            field=django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='demoaccount',
            name='email',
            field=models.EmailField(help_text=b'This should be an email that does not yet exist on the system.', max_length=75),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='demoaccount',
            name='modified',
            field=django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified'),
            preserve_default=True,
        ),
    ]
