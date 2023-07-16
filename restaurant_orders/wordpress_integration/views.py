from core.models import Restaurant, Order
from core.decorators import woocommerce_authentication_required

from django.shortcuts import HttpResponse, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

@csrf_exempt
@require_POST
@woocommerce_authentication_required
def webhook(request, restaurant_pk):
    payload = request.body.decode('utf-8')
    restaurant = get_object_or_404(Restaurant, pk=restaurant_pk)

    order = Order.update_or_create_from_response(json.loads(payload), restaurant)
    if order is None:
        response = HttpResponse('Error, cannot read order properties!')
        response.status_code = 400
        return response

    return HttpResponse('success')
