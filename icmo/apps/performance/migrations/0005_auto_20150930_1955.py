# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('performance', '0004_auto_20150922_2008'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='apr_contacts_to_mql_conversion',
            field=core.fields.PercentField(default=0, max_digits=4, decimal_places=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='campaign',
            name='aug_contacts_to_mql_conversion',
            field=core.fields.PercentField(default=0, max_digits=4, decimal_places=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='campaign',
            name='dec_contacts_to_mql_conversion',
            field=core.fields.PercentField(default=0, max_digits=4, decimal_places=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='campaign',
            name='feb_contacts_to_mql_conversion',
            field=core.fields.PercentField(default=0, max_digits=4, decimal_places=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='campaign',
            name='jan_contacts_to_mql_conversion',
            field=core.fields.PercentField(default=0, max_digits=4, decimal_places=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='campaign',
            name='jul_contacts_to_mql_conversion',
            field=core.fields.PercentField(default=0, max_digits=4, decimal_places=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='campaign',
            name='jun_contacts_to_mql_conversion',
            field=core.fields.PercentField(default=0, max_digits=4, decimal_places=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='campaign',
            name='mar_contacts_to_mql_conversion',
            field=core.fields.PercentField(default=0, max_digits=4, decimal_places=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='campaign',
            name='may_contacts_to_mql_conversion',
            field=core.fields.PercentField(default=0, max_digits=4, decimal_places=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='campaign',
            name='nov_contacts_to_mql_conversion',
            field=core.fields.PercentField(default=0, max_digits=4, decimal_places=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='campaign',
            name='oct_contacts_to_mql_conversion',
            field=core.fields.PercentField(default=0, max_digits=4, decimal_places=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='campaign',
            name='q1_contacts_to_mql_conversion',
            field=core.fields.PercentField(default=0, max_digits=4, decimal_places=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='campaign',
            name='q2_contacts_to_mql_conversion',
            field=core.fields.PercentField(default=0, max_digits=4, decimal_places=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='campaign',
            name='q3_contacts_to_mql_conversion',
            field=core.fields.PercentField(default=0, max_digits=4, decimal_places=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='campaign',
            name='q4_contacts_to_mql_conversion',
            field=core.fields.PercentField(default=0, max_digits=4, decimal_places=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='campaign',
            name='sep_contacts_to_mql_conversion',
            field=core.fields.PercentField(default=0, max_digits=4, decimal_places=1),
            preserve_default=True,
        ),
    ]
