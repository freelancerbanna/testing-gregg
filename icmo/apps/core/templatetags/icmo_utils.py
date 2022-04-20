from colorsys import rgb_to_hls, hls_to_rgb

from classytags.arguments import Argument, MultiKeywordArgument
from classytags.core import Tag, Options
from decimal import Decimal
from django import template

from core.helpers import reverse_strip_empty_kwargs, get_currency_whole_number_display, MONTHS_FULL

register = template.Library()


@register.filter
def get_dictionary_item(dictionary, key):
    """Grabs an item from a dictionary"""
    return dictionary.get(key)


@register.filter
def divide(numerator, denominator):
    """Does simple division of to numbers and returns the dividend"""
    if not denominator:
        denominator = 1
    return str(float(numerator) / float(denominator))


@register.filter
def percent(decimal, places=0):
    """Displays a decimal as a percent"""
    if not places or places == "0":
        return str(int(round(float(decimal) * 100, 0))) + '%'
    return str(round(float(decimal) * 100, int(places))) + '%'


@register.filter
def delta(start, end):
    """Returns the delta of start and end wrapped in a red or green span
    tag depending on if the result is positive or negative"""
    result = int(start) - int(end)
    return str(abs(result))


@register.filter
def wrap_in_list(item):
    return [item]


class BlankKwargsURL(Tag):
    """
    The regular url tag passes blank values to reverse, which for the sake of the top
    menu we need to avoid.
    """
    name = 'blank_kwargs_url'
    options = Options(
        Argument('name'),
        MultiKeywordArgument('url_kwargs', required=False)
    )

    def render_tag(self, context, name, url_kwargs):
        if not url_kwargs:
            url_kwargs = {}
            if context.get('selected_company'):
                url_kwargs['company_slug'] = context['selected_company'].slug
            if context.get('selected_plan'):
                url_kwargs['plan_slug'] = context['selected_plan'].slug
        # strip the empty kwargs
        return reverse_strip_empty_kwargs(name, kwargs=url_kwargs)


register.tag(BlankKwargsURL)


@register.filter
def whole_money(item):
    return get_currency_whole_number_display(item)


@register.filter
def full_month(month_3):
    return [x for x in MONTHS_FULL if x[0:3].lower() == month_3].pop()


@register.filter
def deslugify(value):
    return value.replace('_', ' ').title()


@register.filter
def gradient(hex_color, brightness_offset=1):
    """ takes a color like #87c95f and produces a lighter or darker variant """
    if len(hex_color) != 7:
        raise Exception(
            "Passed %s into color_variant(), needs to be in #87c95f format." % hex_color)
    rgb_int = [int(hex_color[x:x + 2], 16) for x in [1, 3, 5]]
    hls_int = list(rgb_to_hls(*[float(x)/255 for x in rgb_int]))
    hls_int[1] = max(0.1, hls_int[1] - (brightness_offset * .02))
    new_rgb_int = [int(x*255) for x in hls_to_rgb(*hls_int)]
    # hex() produces "0x88", we want just "88"
    return "#" + "".join([hex(i)[2:] for i in new_rgb_int])
