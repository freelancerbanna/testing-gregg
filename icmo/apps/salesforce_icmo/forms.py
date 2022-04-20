from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, HTML, Field, Submit
from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from pytz import common_timezones

from core.forms import BootstrapFormMixin
from core.models import BLANK_CHOICE
from core.widgets import ArrayFieldSelectMultiple
from .models import SalesforceConnection, SegmentFieldTypes


class SalesforceConnectionForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = SalesforceConnection
        fields = []

    icmo_crispy_submit_name = 'Connect to Salesforce'


class SalesforceSettingsForm(forms.ModelForm):
    class Meta:
        model = SalesforceConnection
        fields = (
            'lead_segment_field', 'opportunity_segment_field', 'account_segment_field',
            'lead_campaign_field', 'opportunity_campaign_field', 'account_campaign_field',
            'sfdc_statuses_to_ignore', 'sfdc_end_statuses', 'salesforce_url', 'salesforce_timezone',
            'currency_conversion', 'take_oldest_opportunity_date'
        )

    def __init__(self, *args, **kwargs):
        super(SalesforceSettingsForm, self).__init__(*args, **kwargs)
        self.fields['lead_segment_field'].widget.choices = self._get_choices(
            self.instance.lead_field_choices)
        self.fields['opportunity_segment_field'].widget.choices = self._get_choices(
            self.instance.opportunity_field_choices)
        self.fields['account_segment_field'].widget.choices = self._get_choices(
            self.instance.account_field_choices)

        self.fields['lead_campaign_field'].widget.choices = self._get_choices(
            self.instance.lead_field_choices)
        self.fields['opportunity_campaign_field'].widget.choices = self._get_choices(
            self.instance.opportunity_field_choices)
        self.fields['account_campaign_field'].widget.choices = self._get_choices(
            self.instance.account_field_choices)

        self.fields['sfdc_end_statuses'].widget.choices = [(x, x) for x in self.instance.statuses]

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.html5_required = True
        self.helper.layout = Layout(
            Fieldset(
                'Salesforce Segment Mapping',
                HTML(
                    "<p>Which Salesforce field do you want to use to map to iCMO segments? iCMO "
                    "will try to map Salesforce data off of the Lead table, pivoting off of a "
                    "single field which you will select below.</p>"),
                Field('lead_segment_field'),
                Field('opportunity_segment_field'),
                Field('account_segment_field'),
                Field('segment_field_type'),
            ),
            Fieldset(
                'Salesforce Campaign Mapping',
                HTML("<p> Which Salesforce field do you want to use to map to iCMO campaigns? "
                     "iCMO will first try to map iCMO Campaigns based off of a field you choose "
                     "from the Lead table.</p>"),
                Field('lead_campaign_field'),
                Field('opportunity_campaign_field'),
                Field('account_campaign_field')
            ),
            Fieldset(
                'Salesforce Statuses',
                HTML("<p> Tell us a bit about your Salesforce statuses.</p>"),
                Field('sfdc_statuses_to_ignore'),
                Field('sfdc_end_statuses')
            ),
            Fieldset(
                'Misc',
                Field('salesforce_url'),
                Field('salesforce_timezone'),
                Field('currency_conversion'),
                Field('take_oldest_opportunity_date'),
            ),
            FormActions(
                Submit('save', 'Save changes'),
            )
        )

    lead_segment_field = forms.CharField(
        label="Lead Segment Field",
        help_text="This is the primary field used to map Salesforce contacts to iCMO segments.",
        widget=forms.Select, required=True
    )
    opportunity_segment_field = forms.CharField(
        label="Opportunity Segment Field",
        help_text="The opportunity field is used as a backup if there is no lead associated with "
                  "an Opportunity.",
        widget=forms.Select, required=False
    )
    account_segment_field = forms.CharField(
        label="Account Segment Field",
        help_text="The account field is used as a backup if there is no lead associated with an "
                  "Opportunity.",
        widget=forms.Select, required=False
    )

    lead_campaign_field = forms.CharField(
        label="Lead Source Field",
        help_text="This is the primary field used to map Salesforce contacts to iCMO segments.",
        widget=forms.Select, required=True
    )
    opportunity_campaign_field = forms.CharField(
        label="Opportunity Lead Source Field",
        help_text="The opportunity field is used as a backup if there is no lead associated with "
                  "an Opportunity.",
        widget=forms.Select, required=False
    )
    account_campaign_field = forms.CharField(
        label="Account Lead Source Field",
        help_text="The account field is used as a backup if there is no lead associated with an "
                  "Opportunity.",
        widget=forms.Select, required=False
    )
    sfdc_statuses_to_ignore = SimpleArrayField(
        forms.CharField(),
        label="Lead & Opportunity Statuses to Ignore",
        help_text="Which statuses do you want us to ignore?  Separate them with a comma",
        required=False
    )
    sfdc_end_statuses = SimpleArrayField(
        forms.CharField(),
        label="Lead & Opportunity End Statuses",
        help_text="Which statuses mark an endpoint (ex:  Closed - Won)",
        widget=ArrayFieldSelectMultiple, required=True
    )
    segment_field_type = forms.CharField(widget=forms.HiddenInput, required=False)

    @staticmethod
    def _get_choices(choices):
        return BLANK_CHOICE + tuple((x[0], x[0]) for x in choices)

    @staticmethod
    def _get_field_type_from_choices(choices, value):
        for field_name, field_type in choices:
            if field_name == value:
                if field_type in ('id', 'int', 'double', 'currency'):
                    return SegmentFieldTypes.NUMERIC
                return SegmentFieldTypes.TEXT_MATCH
        return None

    def clean_lead_segment_field(self):
        data = self.cleaned_data['lead_segment_field']
        field_type = self._get_field_type_from_choices(self.instance.lead_field_choices, data)
        if not field_type:
            raise forms.ValidationError('Invalid Lead Segment Field')
        self.cleaned_data['segment_field_type'] = field_type
        return data

    def clean_opportunity_segment_field(self):
        data = self.cleaned_data['opportunity_segment_field']
        if data:
            field_type = self._get_field_type_from_choices(self.instance.opportunity_field_choices,
                                                           data)
            if not field_type:
                raise forms.ValidationError('Invalid Opportunity Segment Field')
            if field_type != self.cleaned_data['segment_field_type']:
                raise forms.ValidationError("All segment fields must be the same type.")
        return data

    def clean_account_segment_field(self):
        data = self.cleaned_data['account_segment_field']
        if data:
            field_type = self._get_field_type_from_choices(self.instance.account_field_choices,
                                                           data)
            if not field_type:
                raise forms.ValidationError('Invalid Account Segment Field')
            if field_type != self.cleaned_data['segment_field_type']:
                raise forms.ValidationError("All segment fields must be the same type.")
        return data
