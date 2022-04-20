from django import forms
from django.forms.widgets import Input
from django.utils.datastructures import MultiValueDict


class PhoneInput(Input):
    input_type = 'tel'

    def __init__(self, attrs=None):
        if attrs is not None:
            self.input_type = attrs.pop('type', self.input_type)
        else:
            attrs = {}
        attrs.update({
            'pattern': '^(?:\+1|1-)?[\-\(\)\[\]\s]*(?:\d[\-\(\)\[\]\s]*){10}$',
            'data-fv-regexp-message': 'Invalid US/CA phone number'
        })
        super(PhoneInput, self).__init__(attrs)


class ArrayFieldSelectMultiple(forms.SelectMultiple):
    # https://gist.github.com/stephane/00e73c0002de52b1c601
    """This is a Form Widget for use with a Postgres ArrayField. It implements
    a multi-select interface that can be given a set of `choices`.
    You can provide a `delimiter` keyword argument to specify the delimeter used.
    """

    def __init__(self, *args, **kwargs):
        # Accept a `delimiter` argument, and grab it (defaulting to a comma)
        self.delimiter = kwargs.pop("delimiter", ",")
        super(ArrayFieldSelectMultiple, self).__init__(*args, **kwargs)

    def render_options(self, choices, value):
        # value *should* be a list, but it might be a delimited string.
        if isinstance(value, str):  # python 2 users may need to use basestring instead of str
            value = value.split(self.delimiter)
        return super(ArrayFieldSelectMultiple, self).render_options(choices, value)

    def value_from_datadict(self, data, files, name):
        if isinstance(data, MultiValueDict):
            # Normally, we'd want a list here, which is what we get from the
            # SelectMultiple superclass, but the SimpleArrayField expects to
            # get a delimited string, so we're doing a little extra work.
            return self.delimiter.join(data.getlist(name))
        return data.get(name, None)
