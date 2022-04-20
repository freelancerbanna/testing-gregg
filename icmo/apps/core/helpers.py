# coding=utf-8
from decimal import Decimal
from decimal import ROUND_UP
from urlparse import urljoin, urlsplit

import re
import requests
from random import randint
from babel.numbers import format_currency
from django import template
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.template.loader import get_template, render_to_string
from django.utils import translation

MONTHS_FULL = (
    'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
    'October', 'November', 'December'
)
MONTHS_3 = ('jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec')
QUARTERS = ('q1', 'q2', 'q3', 'q4')
FISCAL_YEAR = ('fiscal_year',)
ALL_TIME_PERIODS = MONTHS_3 + QUARTERS + FISCAL_YEAR


def validate_email_with_mailgun(email):
    return requests.get(
        "https://api.mailgun.net/v3/address/validate",
        auth=("api", settings.MAILGUN_PUBLIC_KEY),
        params={"address": email}
    )


def full_reverse(url_name):
    return urljoin(settings.ROOT_URL, reverse(url_name))


def full_url_from_path(url_path):
    return urljoin(settings.ROOT_URL, urlsplit(url_path).path)


def template_exists(template_name):
    try:
        get_template(template_name)
        return True
    except template.TemplateDoesNotExist:
        return False


def generate_pdf(template_name, context):
    content = render_to_string(template_name, context)
    params = {'user': settings.HYPDF_USER, 'password': settings.HYPDF_PASSWORD,
              'test': 'true' if settings.DEBUG else 'false', 'content': content}

    r = requests.post('https://www.hypdf.com/htmltopdf', data=params)
    return r


def send_email(request, email, subject_template, txt_body_template, html_body_template,
               context_data,
               attachment=None):
    context = RequestContext(request)
    subject = render_to_string(subject_template, context_data, context)

    # When turned on in mandrill auto-text will automatically create a text version
    # of this template
    text_body = None
    if template_exists(txt_body_template):
        text_body = render_to_string(txt_body_template, context_data, context)
    html_body = None
    if template_exists(html_body_template):
        html_body = render_to_string(html_body_template, context_data, context)

    if not any([text_body, html_body]):
        raise ValueError("You must supply at minimum either a text template or an html template.")

    msg = EmailMultiAlternatives(subject=subject, body=text_body, to=[email])
    if template_exists(html_body_template):
        msg.attach_alternative(html_body, "text/html")
    if attachment:
        msg.attach(**attachment)
    return msg.send()


def send_icmo_email(request, email, email_type, context_data, attachment=None):
    return send_email(request, email,
                      'icmo_users/email/%s_subject.txt' % email_type,
                      'icmo_users/email/%s_body.txt' % email_type,
                      'icmo_users/email/%s_body.html' % email_type,
                      context_data, attachment=attachment)


def generate_random_alphanumeric_string(max_length=20):
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()-_=+?,.<>'
    return "".join([chars[randint(0, len(chars) - 1)] for x in range(0, max_length)])


def reverse_strip_empty_kwargs(*args, **kwargs):
    if 'kwargs' in kwargs:
        kwargs['kwargs'] = {k: v for k, v in kwargs['kwargs'].items() if v}
    return reverse(*args, **kwargs)


def icmo_reverse(name, request):
    kwargs = {}
    if hasattr(request, 'selected_company') and request.selected_company:
        kwargs['company_slug'] = request.selected_company.slug
    if hasattr(request, 'selected_plan') and request.selected_plan:
        kwargs['plan_slug'] = request.selected_plan.slug
    return reverse_strip_empty_kwargs(name, kwargs=kwargs)


def get_currency_whole_number_display(value):
    whole_number = round_currency_to_whole_number(value)
    locale = translation.to_locale(translation.get_language())
    return format_currency(whole_number, value.currency.code, u'¤#,##0', locale=locale)


def get_fiscal_year_months(start_month_num, month_type=None):
    month_type = month_type or "number"
    nums = range(1, 13)
    fiscal_months = nums[start_month_num - 1:] + nums[:start_month_num - 1]
    if month_type == 'name':
        return [MONTHS_3[x - 1] for x in fiscal_months]
    return fiscal_months


def get_fiscal_year_quarters(start_month_num, month_type=None):
    fiscal_months = get_fiscal_year_months(start_month_num, month_type=month_type)
    return dict(q1=fiscal_months[0:3], q2=fiscal_months[3:6], q3=fiscal_months[6:9],
                q4=fiscal_months[9:12])


def get_fiscal_quarter_by_month_name(start_month_num, month_3):
    for quarter, months in get_fiscal_year_quarters(start_month_num, 'name').items():
        if month_3 in months:
            return quarter
    raise ValueError("Could not find month: %s.  Check your spelling" % month_3)


def round_currency_to_whole_number(value):
    return round_to_whole_number(value.amount)


def round_to_whole_number(value):
    return Decimal(value).quantize(Decimal('1.'), rounding=ROUND_UP)


def round_to_one_decimal_place(value):
    return Decimal(value).quantize(Decimal('1.0'))


def round_to_two_decimal_places(value):
    return Decimal(value).quantize(Decimal('1.00'))


def obj_class_name_humanized(obj):
    return re.sub(r'([a-z])([A-Z])', r'\1 \2', obj.__class__.__name__)
