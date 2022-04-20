# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('task_boards', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('action', models.CharField(max_length=255)),
                ('target', models.CharField(max_length=255)),
                ('actor', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-modified',),
            },
        ),
        migrations.AlterField(
            model_name='task',
            name='uuid',
            field=django_extensions.db.fields.ShortUUIDField(db_index=True, unique=True, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='taskchecklistitem',
            name='uuid',
            field=django_extensions.db.fields.ShortUUIDField(db_index=True, unique=True, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='taskcomment',
            name='uuid',
            field=django_extensions.db.fields.ShortUUIDField(db_index=True, unique=True, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='tasktag',
            name='uuid',
            field=django_extensions.db.fields.ShortUUIDField(db_index=True, unique=True, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='taskhistory',
            name='task',
            field=models.ForeignKey(related_name='history', to='task_boards.Task'),
        ),
    ]
