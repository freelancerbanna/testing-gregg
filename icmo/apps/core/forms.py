from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import ugettext as _

# This is just temporary for demonstration purposes
DASHBOARD_CHOICES = (
    ('plan', _('Plan Dashboard')),
    ('actuals', _('Actuals Dashboard')),
    ('comparison', _('Comparison Dashboard')),
    ('executive', _('CMO Dashboard')),
)
PERIOD_CHOICES = (
    ('1', 'Annual'),
    ('4', 'Quarterly'),
    ('12', 'Monthly'),
)
EXPORT_FORMAT_CHOICES = (
    ('PDF', 'PDF'),
    ('XLS', 'Excel'),
    ('CSV', 'CSV'),
)


class PeriodNavigationForm(forms.Form):
    period = forms.ChoiceField(label=_('Select a Period View'),
                               choices=PERIOD_CHOICES,
                               required=False, )


class ExportPageForm(forms.Form):
    export_pid = forms.CharField(widget=forms.HiddenInput())
    recipient = forms.EmailField(label=_('Send To'))
    subject = forms.CharField(label=_('Subject'), max_length=150)
    message = forms.CharField(label=_('Description'), widget=forms.Textarea)
    send_copy = forms.BooleanField(label=_('Copy me'), required=False)
    file_format = forms.ChoiceField(label=_('Format'),
                                    widget=forms.RadioSelect(),
                                    choices=EXPORT_FORMAT_CHOICES)


class BootstrapFormMixin(object):
    icmo_crispy_submit_name = None
    icmo_crispy_disable_form_tag = False

    def __init__(self, *args, **kwargs):
        super(BootstrapFormMixin, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.html5_required = True
        self.helper.form_tag = not self.icmo_crispy_disable_form_tag
        if self.icmo_crispy_submit_name:
            self.helper.add_input(
                Submit('submit', self.icmo_crispy_submit_name, css_class='btn-primary btn-bordered'))


class IncompleteModelFormMixin(object):
    def save(self, commit=True):
        if not self.instance and commit:
            raise ValueError(
                "ICMO: This form excludes one or more required fields, and therefore cannot "
                "create new objects by itself.  Please save with "
                "commit=False and add them yourself to the resulting unsaved object."
                "See https://docs.djangoproject.com/en/1.8/topics/forms/modelforms/#the-save-method for more details."
            )
        return super(IncompleteModelFormMixin, self).save(commit=commit)
