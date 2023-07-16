from django.http import HttpResponse
from core.models import Restaurant

import base64
import hashlib
import hmac

def get_webhook_secret_from_restaurant(pk):
    try:
        token = Restaurant.objects.get(pk=pk).woocommerce_webhook_secret
        if token != '':
            return token
    except Restaurant.DoesNotExist:
        pass
    return None

def compare_signatures(body, webhook_secret, request_sig):
    signature = hmac.new(webhook_secret.encode(), body, hashlib.sha256).digest()
    return hmac.compare_digest(request_sig.encode(), base64.b64encode(signature))


def woocommerce_authentication_required(view):
    def inner(request, restaurant_pk, *args, **kwargs):
        webhook_secret = get_webhook_secret_from_restaurant(restaurant_pk)
        request_sig = request.headers.get('x-wc-webhook-signature')

        if not webhook_secret or not request_sig:
            return HttpResponse('Unauthorized')

        if compare_signatures(request.body, webhook_secret, request_sig):
            return view(request, restaurant_pk, *args, **kwargs)

        response = HttpResponse('Unauthorized')
        response.status_code = 403
        return response
    return inner
