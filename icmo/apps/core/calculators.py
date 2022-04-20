from __future__ import division

from decimal import Decimal
from math import ceil

from core.helpers import round_to_one_decimal_place, round_to_two_decimal_places


def cost_per_mql(cost, mql):
    if cost.amount and mql:
        return round_to_two_decimal_places(cost.amount / Decimal(mql))
    return Decimal(0)


def cost_per_sql(cost, sql):
    if cost.amount and sql:
        return round_to_two_decimal_places(cost.amount / Decimal(sql))
    return Decimal(0)


def average_sale(sales_revenue, sales):
    if sales_revenue.amount and sales:
        return round_to_two_decimal_places(sales_revenue.amount / Decimal(sales))
    return Decimal(0)


def touches_to_mql_conversion(mql, touches):
    if touches and mql:
        return min(Decimal('9999999'),
                   round_to_one_decimal_place(Decimal(mql) / Decimal(touches) * 100))
    return Decimal(0)


def contacts_to_mql_conversion(mql, contacts):
    if contacts and mql:
        return min(Decimal('9999999'),
                   round_to_one_decimal_place(Decimal(mql) / Decimal(contacts) * 100))
    return Decimal(0)


def mql_to_sql_conversion(sql, mql):
    if sql and mql:
        return min(Decimal('9999999'),
                   round_to_one_decimal_place(Decimal(sql) / Decimal(mql) * 100))
    return Decimal(0)


def sql_to_sale_conversion(sales, sql):
    if sales and sql:
        return min(Decimal('9999999'),
                   round_to_one_decimal_place(Decimal(sales) / Decimal(sql) * 100))
    return Decimal(0)


def roi(revenue, budget):
    return currency_growth(revenue, budget)


def touches_per_contact(touches, contacts):
    if touches and contacts:
        return int(ceil(touches / contacts))
    return 0


def currency_growth(new, old):
    return growth(new.amount, old.amount)


def growth(new, old):
    if new and old:
        result = (Decimal(new) - Decimal(old)) / Decimal(old) * 100
        return max(Decimal('-9999999'),  # bounds
                   min(Decimal('9999999'),
                       Decimal(result).quantize(Decimal('1.'))))
    return Decimal(0)
