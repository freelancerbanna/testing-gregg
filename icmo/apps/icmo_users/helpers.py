from django.db import transaction

from billing.forms import SubscriptionChoiceForm
from billing.models import BillingAccount, Subscription
from icmo_users.forms import SignupAccountOwnerForm, SignupCompanyForm, SignupBillingContractForm, \
    SignupCouponForm
from icmo_users.models import SignupLead
from icmo_users.notifications import send_signup_welcome_preactivation_email, \
    send_account_activation_required_email


def create_user(request, form_data, payment_provider, payment_token):
    with transaction.atomic():
        # Create the User Account
        user_form = SignupAccountOwnerForm(form_data)
        if not user_form.is_valid():
            raise ValueError(user_form.errors)
        user = user_form.create_user()

        # Create the Billing Account
        billing_account = BillingAccount.objects.create(
            owner=user,
        )

        # Retrieve the coupon, if any
        coupon_form = SignupCouponForm(form_data)
        if not coupon_form.is_valid():
            raise ValueError(coupon_form.errors)
        coupon = coupon_form.coupon
        if coupon:
            # increment the times_redeemed counter
            coupon.increment()

        # Create the Company
        # Note we call commit=False because we do not collect the account in
        # the form
        company_form = SignupCompanyForm(form_data, prefix='company')
        if not company_form.is_valid():
            raise ValueError(company_form.errors)
        company = company_form.save(commit=False)
        company.account = billing_account
        company.save()

        # Save the company to the billing account as the contact company
        billing_account.company = company
        billing_account.save()

        # Save the company to the user as his Employer
        user.employer = company.name
        user.save()

        # Add the user as an owner to the new company
        company.assign_owner(user)

        # Get the Subscription Plan
        subscription_plan_form = SubscriptionChoiceForm(form_data)
        if not subscription_plan_form.is_valid():
            raise ValueError(subscription_plan_form.errors)

        # Create & Start the Subscription
        subscription = Subscription.start_subscription(
            billing_account,
            subscription_plan_form.subscription_plan,
            payment_provider, payment_token, coupon=coupon
        )

        # Link the new subscription to the billing account as the active subscription
        billing_account.set_active_subscription(subscription)

        # Create the Billing Contract
        # Note we call commit=False because we do not collect the account or
        # the user in the form
        contract_form = SignupBillingContractForm(form_data, prefix='signature')
        if not contract_form.is_valid():
            raise ValueError(contract_form.errors)
        contract = contract_form.save(commit=False)
        contract.account = billing_account
        contract.subscription = subscription
        contract.signing_user = user
        contract.company_name = company.name
        contract.save()

        # remove the signup lead record for this user
        SignupLead.objects.filter(email=user.email).delete()

        # send the welcome email
        send_signup_welcome_preactivation_email(request, user)

        # send the admin notification email
        send_account_activation_required_email(request, user)
    return user
