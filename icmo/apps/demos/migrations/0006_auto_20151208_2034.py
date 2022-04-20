# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demos', '0005_auto_20151005_2113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='demoaccount',
            name='email',
            field=models.EmailField(help_text=b'This should be an email that does not yet exist on the system.', max_length=254),
        ),
    ]
