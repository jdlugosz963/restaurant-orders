from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer
import channels.layers

from asgiref.sync import sync_to_async, async_to_sync

from core.models import Restaurant, Order

from django.db.models import signals
from django.dispatch import receiver
from django.core import serializers


class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        restaurant_pk = self.scope['url_route']['kwargs']['restaurant_pk']
        self.restaurant = sync_to_async(Restaurant.get_user_restaurant_or_404)(restaurant_pk, self.scope['user'])
        if not self.restaurant:
            return

        self.room_name = str(restaurant_pk)
        self.room_group_name = f'restaurant_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        raise StopConsumer 

    async def new_order(self, event):
        await self.send(event['data'])

    @staticmethod
    @receiver(signals.post_save, sender=Order)
    def order_observer(sender, instance, **kwargs):
        if not instance.can_display:
            return

        layer = channels.layers.get_channel_layer()

        async_to_sync(layer.group_send)(f'restaurant_{instance.restaurant.pk}', {
            'type': 'new.order',
            'data': serializers.serialize('json', (instance, ))
        })
