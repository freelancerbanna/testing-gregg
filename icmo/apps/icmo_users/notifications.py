from django.conf import settings

from core.helpers import send_icmo_email
from icmo_users.models import IcmoUser


# SIGNUP NOTIFICATIONS
def send_signup_welcome_preactivation_email(request, user):
    context_data = dict(user=user)
    contract = user.billingcontract_set.all().first()
    attachment = dict(filename="%s.pdf" % contract.slug,
                      content=contract.generate_pdf().content,
                      mimetype='application/pdf')
    return send_icmo_email(request, user.email, 'welcome_preactivation', context_data,
                           attachment=attachment)


def send_signup_welcome_postactivation_email(request, user):
    context_data = dict(user=user)
    return send_icmo_email(request, user.email, 'welcome_postactivation', context_data)


def send_account_activation_required_email(request, new_user):
    # To ensure the activation token is correct, lets requery the user
    new_user = IcmoUser.objects.get(pk=new_user.pk)
    context_data = dict(new_user=new_user,
                        subscription=new_user.billingaccount.subscription_set.all().first())
    contract = new_user.billingcontract_set.all().first()
    attachment = dict(filename="%s.pdf" % contract.slug,
                      content=contract.generate_pdf().content,
                      mimetype='application/pdf')
    return send_icmo_email(request, settings.ACTIVATION_TEAM_EMAIL, 'account_activation_required',
                           context_data,
                           attachment=attachment)


def send_account_activation_postactivation_email(request, new_user, password):
    context_data = dict(new_user=new_user, password=password,
                        subscription=new_user.billingaccount.subscription_set.all().first())
    return send_icmo_email(request, settings.ACTIVATION_TEAM_EMAIL,
                           'account_activation_postactivation',
                           context_data)

