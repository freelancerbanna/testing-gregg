# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0003_auto_20150922_1747'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stripecouponregistry',
            name='stripe_coupon_id',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
    ]
