import calendar
from decimal import Decimal, ROUND_DOWN
import datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.utils import timezone


def round_money(amount):
    amount = Decimal(amount)
    return Decimal(amount.quantize(Decimal('.01'), rounding=ROUND_DOWN))


def apply_to_price(discount_type, discount, amount):
    if discount_type == 'amount_off':
        return max(round_money(Decimal(amount) - discount), 0)
    elif discount_type == 'percent_off':
        return round_money(Decimal(amount) * (100 - discount) / 100)

    raise ValueError("Unrecognized discount type, should be one of:  amount_off, percent_off")


def get_adjusted_fee(amount_off, percent_off, amount):
    if amount_off:
        return apply_to_price('amount_off', amount_off, amount)
    elif percent_off:
        return apply_to_price('percent_off', percent_off, amount)
    else:
        return amount


def get_utc_timestamp():
    return (datetime.datetime.utcnow() + datetime.timedelta(minutes=1)).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


def get_utc_unix_timestamp(datetime_to_convert=None):
    if not datetime_to_convert:
        datetime_to_convert = timezone.now()
    return calendar.timegm(datetime_to_convert.timetuple())


def convert_interval_to_days(interval, interval_duration):
    interval = interval.lower()
    if interval == 'day':
        return interval_duration
    if interval == 'week':
        return int(interval_duration) * 7
    if interval == 'month':
        return (
            (timezone.now() + relativedelta(months=+int(interval_duration))) - timezone.now()).days
    if interval == 'year':
        return int(interval_duration) * 365
    raise ValueError("Unrecognized interval")


def check_provider(provider_name):
    if provider_name not in settings.ICMO_BILLING_PROVIDERS:
        raise ValueError(
            "The provider %s is not mentioned in "
            "settings.ICMO_BILLING_PROVIDERS!" % provider_name
        )
    return provider_name
