# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('icmo_users', '0005_icmouser_is_beta'),
    ]

    operations = [
        migrations.AlterField(
            model_name='icmouser',
            name='email',
            field=models.EmailField(unique=True, max_length=254, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='icmouser',
            name='groups',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups'),
        ),
        migrations.AlterField(
            model_name='icmouser',
            name='last_login',
            field=models.DateTimeField(null=True, verbose_name='last login', blank=True),
        ),
        migrations.AlterField(
            model_name='referral',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='email address'),
        ),
        migrations.AlterField(
            model_name='signuplead',
            name='email',
            field=models.EmailField(unique=True, max_length=254, editable=False),
        ),
    ]
