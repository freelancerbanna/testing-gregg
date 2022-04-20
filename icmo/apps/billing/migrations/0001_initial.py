# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal
import dirtyfields.dirtyfields
import django.utils.timezone
import django_extensions.db.fields
import django_extensions.db.fields.json


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AwaitingPaypalAuthorization',
            fields=[
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('uuid', django_extensions.db.fields.ShortUUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('form_data', django_extensions.db.fields.json.JSONField(editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BillingAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('account_number', models.CharField(unique=True, max_length=11, editable=False)),
                ('limit_max_companies', models.PositiveSmallIntegerField(default=0, null=True, blank=True)),
            ],
            options={
                'ordering': ('created',),
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='BillingContract',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', django_extensions.db.fields.AutoSlugField(populate_from=[b'account', b'version', b'date'], editable=False, blank=True)),
                ('name', models.CharField(max_length=255, verbose_name=b'Print your name')),
                ('title', models.CharField(max_length=255)),
                ('company_name', models.CharField(max_length=255)),
                ('date', models.DateField(auto_now_add=True)),
                ('signature_json', models.TextField(blank=True)),
                ('signature_uri_b64', models.TextField(blank=True)),
                ('version', models.CharField(default=1, max_length=255, editable=False)),
                ('pdf_url', models.URLField(blank=True)),
                ('account', models.ForeignKey(to='billing.BillingAccount')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('is_active', models.BooleanField(default=False, verbose_name='active')),
                ('is_live', models.BooleanField(default=False, verbose_name=b'live', editable=False)),
                ('code', models.CharField(max_length=25)),
                ('short_description', models.CharField(max_length=100)),
                ('duration', models.CharField(default=b'once', max_length=25, choices=[(b'forever', b'Forever'), (b'once', b'Once'), (b'repeating', b'Repeating')])),
                ('amount_off', models.DecimalField(null=True, max_digits=7, decimal_places=2, blank=True)),
                ('percent_off', models.PositiveIntegerField(null=True, blank=True)),
                ('currency', models.CharField(default=b'USD', max_length=3, choices=[(b'USD', b'USD'), (b'CAD', b'CAD')])),
                ('duration_in_months', models.PositiveSmallIntegerField(help_text=b'If duration is repeating, the number of month this coupon applies.', null=True, blank=True)),
                ('max_redemptions', models.PositiveIntegerField(null=True, blank=True)),
                ('times_redeemed', models.PositiveIntegerField(default=0, editable=False)),
                ('redeem_by', models.DateTimeField(null=True, blank=True)),
                ('setup_fee_amount_off', models.DecimalField(null=True, max_digits=7, decimal_places=2, blank=True)),
                ('setup_fee_percent_off', models.PositiveIntegerField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='PaypalCouponRegistry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('code', models.CharField(max_length=25)),
                ('short_description', models.CharField(max_length=100)),
                ('duration', models.CharField(max_length=25)),
                ('amount_off', models.DecimalField(null=True, max_digits=7, decimal_places=2, blank=True)),
                ('percent_off', models.PositiveIntegerField(null=True, blank=True)),
                ('currency', models.CharField(max_length=3)),
                ('duration_in_months', models.PositiveSmallIntegerField(help_text=b'If duration is repeating, the number of month this coupon applies.', null=True, blank=True)),
                ('setup_fee_amount_off', models.DecimalField(null=True, max_digits=7, decimal_places=2, blank=True)),
                ('setup_fee_percent_off', models.PositiveIntegerField(null=True, blank=True)),
                ('icmo_coupon', models.ForeignKey(to='billing.Coupon')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PaypalNotification',
            fields=[
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('id', models.CharField(max_length=100, serialize=False, primary_key=True)),
                ('create_time', models.DateField()),
                ('resource_type', models.CharField(max_length=100)),
                ('event_type', models.CharField(max_length=100)),
                ('summary', models.CharField(max_length=200)),
                ('resource_id', models.CharField(max_length=100)),
                ('resource_create_time', models.CharField(max_length=100)),
                ('resource_update_time', models.CharField(max_length=100)),
                ('resource_state', models.CharField(max_length=100)),
                ('resource_amount_total', models.CharField(max_length=100)),
                ('resource_amount_currency', models.CharField(max_length=100)),
                ('resource_amount_details_subtotal', models.CharField(max_length=100)),
                ('resource_parent_payment', models.CharField(max_length=100)),
                ('resource_valid_until', models.CharField(max_length=100)),
                ('resource_links_self', models.URLField()),
                ('resource_links_capture', models.URLField()),
                ('resource_links_void', models.URLField()),
                ('resource_links_parent_payment', models.URLField()),
                ('links_self', models.URLField()),
                ('links_resend', models.URLField()),
                ('request_json', django_extensions.db.fields.json.JSONField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PaypalSubscriptionPlanRegistry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('paypal_plan_id', models.CharField(unique=True, max_length=100)),
                ('name', models.CharField(max_length=255)),
                ('short_description', models.CharField(max_length=255)),
                ('currency', models.CharField(max_length=3)),
                ('interval', models.CharField(max_length=10)),
                ('interval_count', models.PositiveSmallIntegerField()),
                ('amount', models.DecimalField(max_digits=7, decimal_places=2)),
                ('discount_period_interval', models.CharField(max_length=10, null=True, blank=True)),
                ('discount_period_interval_count', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('discount_period_interval_duration', models.PositiveIntegerField(null=True, blank=True)),
                ('discount_period_amount', models.DecimalField(null=True, max_digits=7, decimal_places=2, blank=True)),
                ('setup_fee_amount', models.DecimalField(null=True, max_digits=7, decimal_places=2, blank=True)),
                ('is_active', models.BooleanField(default=False)),
                ('icmo_coupon', models.ForeignKey(blank=True, to='billing.Coupon', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='PaypalSubscriptionRegistry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('paypal_subscription_id', models.CharField(unique=True, max_length=255)),
                ('paypal_plan_id', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StripeCouponRegistry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stripe_coupon_id', models.CharField(max_length=255)),
                ('setup_fee_amount_off', models.DecimalField(null=True, max_digits=7, decimal_places=2, blank=True)),
                ('setup_fee_percent_off', models.PositiveIntegerField(null=True, blank=True)),
                ('icmo_coupon', models.ForeignKey(to='billing.Coupon')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StripeSubscriptionPlanRegistry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stripe_plan_id', models.CharField(max_length=255)),
                ('setup_fee_name', models.CharField(max_length=100, blank=True)),
                ('setup_fee_amount', models.PositiveIntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StripeSubscriptionRegistry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stripe_subscription_id', models.CharField(max_length=255)),
                ('stripe_customer_id', models.CharField(max_length=255)),
                ('card_last_4', models.CharField(max_length=4, blank=True)),
                ('card_kind', models.CharField(max_length=50, blank=True)),
                ('card_exp_month', models.PositiveIntegerField(null=True, blank=True)),
                ('card_exp_year', models.PositiveIntegerField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('is_active', models.BooleanField(default=False, verbose_name='active')),
                ('is_live', models.BooleanField(default=False, verbose_name=b'live', editable=False)),
                ('provider_name', models.CharField(blank=True, max_length=30, editable=False, choices=[(b'stripe', b'Stripe'), (b'paypal_rest', b'PayPal')])),
                ('status', models.CharField(blank=True, max_length=255, choices=[(b'active', b'Active'), (b'trialing', b'Trialing'), (b'past_due', b'Past Due'), (b'canceled', b'Canceled'), (b'unpaid', b'Unpaid')])),
                ('cancel_at_period_end', models.BooleanField(default=False)),
                ('canceled_at', models.DateTimeField(null=True, editable=False, blank=True)),
                ('trial_end', models.DateTimeField(null=True, blank=True)),
                ('account', models.ForeignKey(editable=False, to='billing.BillingAccount')),
                ('coupon', models.ForeignKey(blank=True, editable=False, to='billing.Coupon', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SubscriptionPlan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('is_active', models.BooleanField(default=False, verbose_name='active')),
                ('is_live', models.BooleanField(default=False, verbose_name=b'live', editable=False)),
                ('name', models.CharField(max_length=100)),
                ('slug', django_extensions.db.fields.AutoSlugField(populate_from=b'name', editable=False, blank=True)),
                ('short_description', models.CharField(max_length=200)),
                ('full_description', models.TextField()),
                ('statement_description', models.CharField(help_text=b'This will (may) appear on the bank statement, max 22 characters, cannot include <>"\' characters.', max_length=22)),
                ('limit_max_companies', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('currency', models.CharField(default=b'USD', max_length=3, choices=[(b'USD', b'USD'), (b'CAD', b'CAD')])),
                ('interval', models.CharField(default=b'month', max_length=10, choices=[(b'day', b'Day'), (b'week', b'Week'), (b'month', b'Month'), (b'year', b'Year')])),
                ('interval_count', models.PositiveSmallIntegerField(default=1, null=True, verbose_name=b'Intervals between charges')),
                ('amount', models.DecimalField(verbose_name=b'Amount (per period)', max_digits=7, decimal_places=2)),
                ('amount_display_interval', models.PositiveSmallIntegerField(help_text=b"If you want the pricing interval display to be different than the billing interval (for example show monthly pricing but bill quarterly), then set this to the number of intervals you'd like to display.", null=True, blank=True)),
                ('free_trial_period_interval', models.CharField(blank=True, max_length=10, null=True, choices=[(b'day', b'Day'), (b'week', b'Week'), (b'month', b'Month'), (b'year', b'Year')])),
                ('free_trial_period_interval_duration', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('setup_fee_name', models.CharField(max_length=100, blank=True)),
                ('setup_fee_amount', models.DecimalField(default=Decimal('0.00'), max_digits=7, decimal_places=2)),
                ('setup_fee_description', models.CharField(max_length=200, blank=True)),
                ('minimum_duration_in_intervals', models.PositiveSmallIntegerField(null=True, blank=True)),
            ],
            options={
                'ordering': ('interval', 'amount'),
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.AddField(
            model_name='subscription',
            name='plan',
            field=models.ForeignKey(editable=False, to='billing.SubscriptionPlan'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stripesubscriptionregistry',
            name='icmo_subscription',
            field=models.ForeignKey(to='billing.Subscription'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stripesubscriptionplanregistry',
            name='icmo_plan',
            field=models.ForeignKey(to='billing.SubscriptionPlan'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='paypalsubscriptionregistry',
            name='icmo_subscription',
            field=models.ForeignKey(to='billing.Subscription'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='paypalsubscriptionplanregistry',
            name='icmo_plan',
            field=models.ForeignKey(to='billing.SubscriptionPlan'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='paypalsubscriptionplanregistry',
            name='variant_of',
            field=models.ForeignKey(blank=True, to='billing.PaypalSubscriptionPlanRegistry', null=True),
            preserve_default=True,
        ),
    ]
