from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import User
from asgiref.sync import sync_to_async
import base64
from io import BytesIO


class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(self.channel_name)
        self.room_name = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = 'chat_{}'.format(self.room_name)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        message_json = json.loads(text_data)
        message = message_json['message']
        username = message_json['username']
        user_obj = User.objects.get(username=username)
        avatar_b64 = user_obj.get_avatar_base64()
        print("username ", username)

        print("Message ", message)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chatroom_message',
                'message': message,
                'username': username,
                'avatar_b64': avatar_b64
            }
        )

    async def chatroom_message(self, event):
        message = event['message']
        username = event['username']
        avatar_b64 = event['avatar_b64']
        await self.send(text_data=json.dumps(
            {
                'message': message,
                'username': username,
                'avatar_b64': avatar_b64
            }
        ))
