from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django import forms
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext as _

from core.forms import BootstrapFormMixin, IncompleteModelFormMixin
from core.models import PartialUpdatesModel
from revenues.models import Segment


class PlanNavigationForm(forms.Form):
    plan = forms.ChoiceField(label=_('Selected Plan'), required=False)
    action = forms.CharField(initial='change_plan', widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        company_user = kwargs.pop('company_user')
        super(PlanNavigationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'switch_plan_form'
        self.helper.form_action = reverse_lazy('switch_plan')
        self.helper.form_method = 'GET'
        self.helper.layout = Layout(
            Field('plan', css_class='input-sm col-xs-3')
        )
        choices = [('', 'No Plan Selected')]
        last_plan_type = None
        for plan in company_user.permitted_revenue_plans:
            if plan.plan_type != last_plan_type:
                last_plan_type = plan.plan_type
                choices.append(('', '-- %s Plans --' % plan.get_plan_type_display()))
            choices.append((plan.slug, plan.name))
        self.fields['plan'].choices = choices


class ClonePlanForm(forms.Form):
    # We need to set the 'template' company id
    t = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(label=_('New Name'), max_length=150)


class SharePlanForm(forms.Form):
    pid = forms.CharField(widget=forms.HiddenInput())
    recipient = forms.ChoiceField(label=_('Share To'))
    subject = forms.CharField(label=_('Subject'), max_length=150)
    message = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        super(SharePlanForm, self).__init__(*args, **kwargs)
        if instance:
            shared_users = []
            for share in instance.active_shares:
                shared_users.append(share.user)
            choices = []
            for user in instance.company.active_users:
                if not user in shared_users:
                    if user.first_name and user.last_name:
                        name = "%s %s" % (user.first_name, user.last_name)
                    else:
                        name = user.email
                    choices.append((user.pk, name))
            self.fields['recipient'].choices = choices
            self.fields['pid'].initial = instance.pk


class UnsharePlanForm(forms.Form):
    pid = forms.CharField(widget=forms.HiddenInput())
    recipient = forms.CharField(widget=forms.HiddenInput())


class SegmentForm(BootstrapFormMixin, IncompleteModelFormMixin, forms.ModelForm):
    class Meta:
        model = Segment
        fields = ('name', 'average_sale', 'goal_q1', 'goal_q2', 'goal_q3', 'goal_q4')

    def __init__(self, *args, **kwargs):
        super(SegmentForm, self).__init__(*args, **kwargs)
        self.helper.form_class += ' money-form'
