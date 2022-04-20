# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0003_auto_20150922_1747'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyusergroup',
            name='task_boards',
            field=models.CharField(default=b'none', max_length=50, choices=[(b'none', b'None'), (b'view', b'View'), (b'change', b'Change')]),
            preserve_default=True,
        ),
    ]
