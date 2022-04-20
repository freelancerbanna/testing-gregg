# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0003_program_contacts_to_mql_conversion'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='fixed_budget',
            field=models.BooleanField(default=False),
        ),
    ]
