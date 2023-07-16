import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer
import channels.layers

from asgiref.sync import sync_to_async, async_to_sync


class NotificationsConsumer(AsyncWebsocketConsumer):
    OK = 'ok'
    ERROR = 'error'
    WARNING = 'warning'

    async def connect(self):
        self.room_group_name = ''
        user = self.scope["user"]
        if not user.is_authenticated:
            return False

        self.room_name = f'user_{user.pk}'
        self.room_group_name = f'notifications_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        raise StopConsumer

    async def notify(self, event):
        await self.send(event['data'])

    @staticmethod
    def send_notifications(user_pk, status, message):
        layer = channels.layers.get_channel_layer()

        async_to_sync(layer.group_send)(f'notifications_user_{user_pk}', {
            'type': 'notify',
            'data': json.dumps({
                'status': status,
                'message': message
            })
        })
