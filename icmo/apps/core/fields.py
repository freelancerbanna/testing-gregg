from copy import copy
from decimal import Decimal

from django.db.models.fields import DecimalField
from djmoney.models.fields import MoneyField


class CappedMoneyFieldMixin(object):
    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if len(str(int(Decimal(value.amount)))) > self.max_digits - self.decimal_places:
            # cap at 999..
            new_value = copy(value)
            new_value.amount = Decimal(self.max_digits * 9)
            if value.amount < 0:
                new_value.amount *= -1
            setattr(model_instance, self.attname, new_value)
        return super(CappedMoneyFieldMixin, self).pre_save(model_instance, add)


class CappedDecimalFieldMixin(object):
    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if len(str(int(Decimal(value)))) > self.max_digits - self.decimal_places:
            # cap at 999..
            new_value = Decimal(self.max_digits * 9)
            if value < 0:
                new_value *= -1
            setattr(model_instance, self.attname, new_value)
        return super(CappedDecimalFieldMixin, self).pre_save(model_instance, add)


class DefaultMoneyField(CappedMoneyFieldMixin, MoneyField):
    def __init__(self, verbose_name=None, name=None, max_digits=13,
                 decimal_places=0, default_currency='USD',
                 default=0, **kwargs):
        super(DefaultMoneyField, self).__init__(verbose_name=verbose_name, name=name,
                                                max_digits=max_digits,
                                                decimal_places=decimal_places,
                                                default_currency=default_currency,
                                                default=default, **kwargs)


class DecimalMoneyField(CappedMoneyFieldMixin, MoneyField):
    def __init__(self, verbose_name=None, name=None, max_digits=15,
                 decimal_places=2, default_currency='USD',
                 default=0, **kwargs):
        super(DecimalMoneyField, self).__init__(verbose_name=verbose_name, name=name,
                                                max_digits=max_digits,
                                                decimal_places=decimal_places,
                                                default_currency=default_currency,
                                                default=default, **kwargs)


class PercentField(CappedDecimalFieldMixin, DecimalField):
    def __init__(self, verbose_name=None, name=None, max_digits=8, decimal_places=1, default=0):
        super(PercentField, self).__init__(verbose_name=verbose_name, name=name,
                                           max_digits=max_digits,
                                           decimal_places=decimal_places, default=default)
