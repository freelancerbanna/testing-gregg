from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from paypalrestsdk import WebhookEvent

from billing.providers.paypal_rest.models import AwaitingPaypalAuthorization


def flatten_webhook_json(obj, prefix=None):
    """
    Turns a nested dict into a flat dict where keys are joined by underscores.
    Flattens webhook links
    :param obj: dict: the webhook request_json to flatten
    :param prefix: used in recursion
    :return: a flat dict
    """
    output = {}
    for key, val in obj.items():
        newkey = "_".join([x for x in [prefix, key] if x])
        if type(val) is dict:
            output.update(flatten_webhook_json(val, prefix=newkey))
        elif key == 'links' and type(val) is list:
            for link in val:
                output["%s_%s" % (newkey, link['rel'])] = link['href']
        else:
            output[newkey] = val
    return output


def verify_webhook_request(request):
    trans_sig = request.META.get('HTTP_PAYPAL_TRANSMISSION_SIG')
    auth_algo = request.META.get('HTTP_PAYPAL_AUTH_ALGO')
    cert_url = request.META.get('HTTP_PAYPAL_CERT_URL')
    trans_id = request.META.get('HTTP_PAYPAL_TRANSMISSION_ID')
    trans_time = request.META.get('HTTP_PAYPAL_TRANSMISSION_TIME')
    # This is 'WEBHOOK_ID' for sandbox tests otherwise its the webhook id.
    webhook_id = settings.PAYPAL_WEBHOOK_ID
    return WebhookEvent.verify(trans_id, trans_time, webhook_id, request.body, cert_url,
                               trans_sig, auth_algo)


def paypal_retrieve_form_data_and_token(request):
    """
    Retrieves the form data which was tucked away in the db until now
    :param request:
    :return: tuple: form_data, token
    :raise ObjectDoesNotExist:
    """
    paypal_auth_request = request.session.get('paypal', {})
    token = paypal_auth_request.get('token')
    data_uuid = paypal_auth_request.get('data_uuid')

    if not all([token, data_uuid]):
        raise ObjectDoesNotExist
    awaiting_auth_data = AwaitingPaypalAuthorization.objects.get(uuid=data_uuid)
    del request.session['paypal']  # comment out while debugging paypal flow'
    return awaiting_auth_data.form_data, token
