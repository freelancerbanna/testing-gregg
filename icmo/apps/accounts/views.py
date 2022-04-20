import copy

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _
from vanilla import TemplateView, FormView

from billing.forms import AccountOwnerEditForm
from billing.models import BillingAccount
from budgets.models import BudgetLineItem
from companies.models import Company
from core.cbvs import HidePlanBarMixin, ItemRequiredMixin
from core.helpers import icmo_reverse
from icmo_users.forms import ReferAFriendForm, SendASuggestionForm, PasswordUpdateForm, \
    IcmoUserForm
from icmo_users.models import Suggestion, Referral
from leads.models import Program
from performance.models import Campaign
from revenues.models import RevenuePlan, Segment
from task_boards.models import TaskBoard

NAME_TO_CLASS_MAP = {
    "Campaign": Campaign,
    "Budget Line Item": BudgetLineItem,
    "Program": Program,
    "Segment": Segment,
    "Revenue Plan": RevenuePlan,
    "Company": Company,
    "TaskBoard": TaskBoard
}
CLASS_TO_NAME_MAP = {v: k for k, v in NAME_TO_CLASS_MAP.items()}


class RecycleBinView(ItemRequiredMixin, HidePlanBarMixin, TemplateView):
    item_required = Company
    http_method_names = ('get', 'post')
    template_name = 'accounts/recycle_bin.html'

    def get_context_data(self, **kwargs):
        context = super(RecycleBinView, self).get_context_data(**kwargs)
        inactive_items = []
        for obj in self.request.user.owned_companies.filter(is_active=False):
            inactive_items.append(dict(
                name=obj,
                type="Company",
                unique_slug=obj.unique_slug,
                deactivated=obj.modified,
                deactivated_by=obj.modified_by
            ))

        if self.request.company_user:
            if self.request.company_user.can_change('revenue_plans'):
                for obj in RevenuePlan.all_objects.filter(is_active=False,
                                                          company=self.request.selected_company):
                    inactive_items.append(dict(
                        name=obj,
                        type="Revenue Plan",
                        unique_slug=obj.unique_slug,
                        deactivated=obj.modified,
                        deactivated_by=obj.modified_by
                    ))
            if self.request.company_user.can_change(
                    'revenue_plans') and not self.request.company_user.is_segment_restricted:
                for obj in Segment.all_objects.filter(is_active=False,
                                                      company=self.request.selected_company):
                    inactive_items.append(dict(
                        name=obj,
                        type="Segment",
                        unique_slug=obj.unique_slug,
                        deactivated=obj.modified,
                        deactivated_by=obj.modified_by
                    ))
            if self.request.company_user.can_change('program_mix'):
                for obj in Program.all_objects.filter(is_active=False,
                                                      company=self.request.selected_company,
                                                      segment__in=self.request.company_user.permitted_segments):
                    inactive_items.append(dict(
                        name=obj,
                        type="Program",
                        unique_slug=obj.unique_slug,
                        deactivated=obj.modified,
                        deactivated_by=obj.modified_by
                    ))
            if self.request.company_user.can_change('budgets'):
                for obj in BudgetLineItem.all_objects.filter(is_active=False,
                                                             company=self.request.selected_company,
                                                             segment__in=self.request.company_user.permitted_segments):
                    inactive_items.append(dict(
                        name=obj,
                        type="Budget Item",
                        unique_slug=obj.unique_slug,
                        deactivated=obj.modified,
                        deactivated_by=obj.modified_by
                    ))
            if self.request.company_user.can_change('performance'):
                for obj in Campaign.all_objects.filter(is_active=False,
                                                       company=self.request.selected_company,
                                                       segment__in=self.request.company_user.permitted_segments):
                    inactive_items.append(dict(
                        name=obj,
                        type="Campaign",
                        unique_slug=obj.unique_slug,
                        deactivated=obj.modified,
                        deactivated_by=obj.modified_by
                    ))
            if self.request.company_user.can_change('task_boards'):
                for obj in TaskBoard.all_objects.filter(is_active=False,
                                                        company=self.request.selected_company):
                    inactive_items.append(dict(
                        name=obj,
                        type="TaskBoard",
                        unique_slug=obj.unique_slug,
                        deactivated=obj.modified,
                        deactivated_by=obj.modified_by
                    ))
        context.update(dict(
            inactive_items=inactive_items
        ))
        return context

    def post(self, request, *args, **kwargs):
        if not all([request.POST.get(x) for x in ('uniqueSlug', 'objectType', 'action')]):
            messages.error(request, "An error has occurred please reload the page and try again")
            return HttpResponseBadRequest(content="Missing required args")
        unique_slug = self.request.POST.get('uniqueSlug')
        object_type = self.request.POST.get('objectType')
        action = self.request.POST.get('action')

        if action not in ('restore', 'delete'):
            messages.error(request, "An error has occurred please reload the page and try again")
            return HttpResponseBadRequest(content="Invalid action")

        klass = NAME_TO_CLASS_MAP[object_type]
        try:
            obj = klass.get_by_unique_slug(unique_slug)
        except klass.DoesNotExist:
            messages.error(request, "Could not %s that object" % action)
            # todo log rollbar error
            return HttpResponseBadRequest(content="Could not find object by that id")
        if action == 'restore':
            obj.activate(request.user)
            messages.success(request, "%s restored successfully." % object_type)
        elif action == 'delete':
            obj.delete()
            messages.success(request, "%s deleted successfully." % object_type)
        return HttpResponse(status=200)


class AccountView(HidePlanBarMixin, TemplateView):
    template_name = 'accounts/account.html'

    def get_context_data(self, **kwargs):
        context = super(AccountView, self).get_context_data(**kwargs)
        billing = None
        if hasattr(self.request.user, 'billingaccount'):
            billing = self.request.user.billingaccount
        context.update(dict(
            billing=billing
        ))
        if self.request.GET.get('edit'):
            if self.request.GET.get('edit') == 'user':
                context['user_form'] = IcmoUserForm(instance=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        form = IcmoUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "User profile saved.")
            return HttpResponseRedirect(icmo_reverse('user_details', request))
        context = self.get_context_data()
        context['user_form'] = form
        return self.render_to_response(context)


class SuggestionView(HidePlanBarMixin, FormView):
    template_name = 'accounts/send_a_suggestion.html'
    form_class = SendASuggestionForm

    def form_valid(self, form):
        message = form.cleaned_data['message']
        Suggestion.objects.create(user=self.request.user, message=message)
        messages.success(self.request, _('Thank you for sending us your suggestion.'))
        context = self.get_context_data(form=self.get_form())
        return self.render_to_response(context)


class ConnectorsView(ItemRequiredMixin, HidePlanBarMixin, TemplateView):
    template_name = 'accounts/integrations.html'
    item_required = Company


class HelpView(HidePlanBarMixin, TemplateView):
    template_name = 'accounts/help/help.html'


def refer_a_friend(request):
    """Send a referral"""
    warning = _("Sorry. Couldn't process your referral request.")
    if request.POST.get('refer_a_friend', False):
        form = ReferAFriendForm(request.POST)
        if request.user.is_active and form.is_valid():
            referrer = request.user
            if ('message' in form.cleaned_data
                and len(form.cleaned_data['message']) > 1):
                message = form.cleaned_data['message']
            else:
                message = None

            emails = form.cleaned_data['emails'].split(',')
            for email in emails:
                Referral.objects.create(referrer=referrer,
                                        email=email.strip(),
                                        message=message)
            messages.success(request, _('Thank you for referring us.'))
        else:
            messages.warning(request, warning)
    else:
        messages.warning(request, warning)

    if request.META.get('HTTP_REFERER', False):
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect(reverse('user_logout'))


@login_required(login_url='/account/signup')
def user_details(request, account_id, extra_context):
    user = request.user
    if account_id == '0':
        # User has no account and is using granted access
        account = None
    elif user.is_superuser:
        account = BillingAccount.objects.get(pk=account_id)
    else:
        account = get_object_or_404(BillingAccount, pk=account_id, owner=user)

    if request.GET and 'o' in request.GET:
        open_drawer = request.GET['o']
    else:
        open_drawer = None

    if request.POST and 'csrfmiddlewaretoken' in request.POST:
        updated_user = False
        my_user_form = AccountOwnerEditForm(request.POST, prefix="user",
                                            instance=user)
        get_args = ''
        if 'company' in extra_context:
            get_args += "?c=%d" % extra_context['company'].pk
        # Validation is updating the user instance, so work with a copy to
        # determine if changes were made...
        old_user = copy.copy(user)
        if my_user_form.is_valid():
            if old_user.email != my_user_form.cleaned_data['email']:
                updated_user = True
            if old_user.first_name != my_user_form.cleaned_data['first_name']:
                updated_user = True
            if old_user.last_name != my_user_form.cleaned_data['last_name']:
                updated_user = True
            if updated_user:
                user.save()

        # Figure out if we need to process the password form or not
        if ((not updated_user
             and request.POST.get('password-password', False))
            or (request.POST.get('password-password', False)
                and request.POST.get('password-new_password', False)
                and request.POST.get('password-confirm_password', False)
                )):

            my_password_form = PasswordUpdateForm(request.POST,
                                                  prefix="password",
                                                  instance=user
                                                  )
            if my_password_form.is_valid():
                user.set_password(my_password_form.cleaned_data['new_password'])
                user.save()
                success = _("Your password has been updated.")
                messages.success(request, success)
                account_id = 0
                if account:
                    account_id = account.pk
                redirect = reverse('user_details',
                                   kwargs={'account_id': account_id}) + get_args
                return HttpResponseRedirect(redirect)

            else:
                open_drawer = 'password'
        else:
            if updated_user:
                success = _("Your user information has been updated.")
                messages.success(request, success)
                if '?' in get_args:
                    get_args += '&o=user'
                else:
                    get_args += '?o=user'

                account_id = 0
                if account:
                    account_id = account.pk
                redirect = reverse('user_details',
                                   kwargs={'account_id': account_id}) + get_args
                return HttpResponseRedirect(redirect)
            else:
                my_password_form = PasswordUpdateForm(prefix="password")

    else:
        my_user_form = AccountOwnerEditForm(instance=user, prefix="user")
        my_password_form = PasswordUpdateForm(prefix="password")

    context = {
        "title": _('My User Details'),
        "subtitle": _('My User Details'),
        "account_page": True,  # Highlights account tab in nav menu
        "account": account,
        "my_user_form": my_user_form,
        "my_password_form": my_password_form,
        "open_drawer": open_drawer,
    }
    context.update(extra_context or {})
    return render(request, 'icmo_users/user_details.html', context)
