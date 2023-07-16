from celery import shared_task

from django.core import serializers

from restaurant_orders.consumers import NotificationsConsumer

from core.utils import Orders, SendMail, SendSms
import re


def send_notification(is_success, message, user_pk):
    status = NotificationsConsumer.OK if is_success else NotificationsConsumer.ERROR
    NotificationsConsumer.send_notifications(
        user_pk,
        status,
        message
    )



@shared_task
def create_order_and_send_notification(order, items, is_email=None, is_sms=None, user_pk=None):
    order = [obj for obj in serializers.deserialize('json', order)]
    if len(order) != 1:
        return
    order = order[0].object

    phone = order.billing.get('phone')
    email = order.billing.get('email')
    new_order = Orders(order.restaurant, order.billing).create_custom_order(items)

 
#   if new_order is None:
#        send_notification(False,
#                          "Niestety nie udalo sie skontaktowac z restauracja, prosze sprowbowac ponownie pozniej.",
#                          user_pk)
#        return

    EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    if is_sms: # TODO: Make regex for sms
        sms = SendSms(new_order).send()
        send_notification(*sms, user_pk)

    if is_email and re.fullmatch(EMAIL_REGEX, str(email)):
        mail = SendMail(new_order).send()
        send_notification(*mail, user_pk)


    

