import json
from woocommerce import API
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from django.core.mail import send_mail
from django.conf import settings

from core.models import Order

class Sender():
    def __init__(self, order):
        self.order = order

    def get_order_url(self):
        order_id = self.order.wp_id
        order_key = self.order.wp_order_key
        restaurant_url = self.order.restaurant.wordpress_url
        return f'{restaurant_url}/zamowienie/order-pay/{order_id}/?pay_for_order=true&key={order_key}'

    def get_message_body(self):
        return f'Prosze dokonac platnosci: {self.get_order_url()}'

    def send(self) -> (bool, str):
        pass


class SendSms(Sender): 
    def __init__(self, order):
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token  = settings.TWILIO_TOKEN
        
        self.client = Client(account_sid, auth_token)
        self.from_ = "+17432007359"
        
        super().__init__(order)

    def send(self) -> (bool, str):
        phone = self.order.billing.get('phone', None)
        phone = "+48609155122"
        if phone:
            try:
                message = self.client.messages.create(to=phone,
                                                      from_=self.from_,
                                                      body=self.get_message_body())
            except TwilioRestException as err:
                return (False, err.msg)
            else:
                return (True, 'Wyslano sms')
        return (False, 'Nie znaleziono numeru telefonu.')



class SendMail(Sender):
    def send(self) -> (bool, str):
        email = self.order.billing.get('email', None)
        email = 'jdlugosz963@gmail.com'
        if email:  # Jesli sie spierdoli to wypluje  
            try:
                send_mail('Strona do zaplaty', self.get_message_body(), 'no-reply@reami.pl', (email, ), fail_silently=False)
            except smtplib.SMTPException:
                return (False, "Niestety nie udalo sie wyslac maila.")
            else:
                return (True, "Wyslano maila.")
        return (False, "Nie znaleziono maila.")


class Orders:
    def __init__(self, restaurant, billing):
        self.restaurant = restaurant
        self.billing = billing

        self.wcapi = API(
            url=restaurant.wordpress_url,
            consumer_key=restaurant.woocommerce_consumer_key,
            consumer_secret=restaurant.woocommerce_consumer_secret,
            timeout=7
        )

    def get_custom_order_data(self, items):
        return {
            "payment_method": "bacs",
            "payment_method_title": "Direct Bank Transfer",
            "set_paid": False,
            "billing": self.billing,
            "shipping": self.billing,
            "line_items": [
                {
                    "product_id": pk,
                    "total": total,
                    "quantity": 1,
                } for pk, total in items
            ]
        }

    def create_custom_order(self, items):
        data = self.get_custom_order_data(items)
        response = self.wcapi.post("orders", data=data).json()
        return Order.create_from_response_disable_view(response, self.restaurant)

