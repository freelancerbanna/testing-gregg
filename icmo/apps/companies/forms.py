from crispy_forms.layout import Field, Layout

from django import forms

from companies.models import Company, CompanyUser
from core.forms import BootstrapFormMixin, IncompleteModelFormMixin


class CompanyForm(BootstrapFormMixin, IncompleteModelFormMixin, forms.ModelForm):
    # todo this form works for new companies, but doesnt allow logo or fiscal year handling
    #  Account is a required field but it is excluded here so this form must
    # be saved with form.save(commit=False) which will return an unsaved object
    # to which the billing account can be attached.
    class Meta:
        model = Company
        exclude = ('account', 'is_active', 'logo', 'fiscal_year_start')
        widgets = {
            'zipcode': forms.TextInput(
                attrs={'data-fv-zipcode': "true",
                       'data-fv-zipcode-country': "company_country"}
            ),
            'website': forms.URLInput(attrs={
                'data-fv-uri-uri': 'true',
                'data-fv-uri-allowemptyprotocol': 'true'}
            )
        }


class CompanyUserForm(BootstrapFormMixin, IncompleteModelFormMixin, forms.ModelForm):
    class Meta:
        model = CompanyUser
        exclude = ('company', 'user', 'owner', 'is_active')

    user = forms.EmailField(label='Email')

    def __init__(self, *args, **kwargs):
        super(CompanyUserForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            'user',
            'group',
            'title',
            'permitted_segments_list',
        )
