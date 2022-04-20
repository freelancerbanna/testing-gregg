from core.helpers import send_icmo_email


def send_share_notification_email(request, invited_user, inviter, company):
    context_data = dict(invited_user=invited_user, inviter=inviter, company=company)
    return send_icmo_email(request, invited_user.email, 'new_share', context_data)


# INVITED USER NOTIFICATIONS
def send_invited_user_activation_email(request, invited_user, inviter, company):
    context_data = dict(invited_user=invited_user, inviter=inviter, company=company)
    return send_icmo_email(request, invited_user.email, 'invited_user_activate', context_data)


def send_invited_user_welcome_email(request, invited_user):
    context_data = dict(invited_user=invited_user)
    return send_icmo_email(request, invited_user.email, 'invited_user_welcome', context_data)
