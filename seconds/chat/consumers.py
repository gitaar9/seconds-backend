from django.contrib.auth.models import AnonymousUser

import json

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

from seconds.game.models import Game


def serialize_game(game):
    from seconds.game.serializers import GameSerializer

    class FakeRequest:
        def __init__(self, user):
            self.user = user

    return GameSerializer(
        instance=game,
        context={'request': FakeRequest(None)}
    ).data


class ChatConsumer(AsyncWebsocketConsumer):
    @staticmethod
    @database_sync_to_async
    def get_user_game_json(user):
        return serialize_game(user.game) if not isinstance(user, AnonymousUser) and user.in_game else {}

    async def connect(self):
        game_json = await self.get_user_game_json(self.scope["user"])
        if 'code' in game_json:
            game_code = game_json['code']
        else:
            if self.scope['game_code'] is not None:
                game_code = self.scope['game_code']
            else:
                return

        self.room_name = 'main'
        self.room_group_name = game_code

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    # async def receive(self, text_data):
    #     # Send message to room group
    #     game_json = await self.get_user_game_json(self.scope["user"])
    #     print("receive ", game_json)
    #     # This makes that a message is send over the group channel
    #     await self.channel_layer.group_send(
    #         self.room_group_name, {"type": "chat_message", "game": game_json}
    #     )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["game"]
        print("chat_message ", message)
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"game": message}))


def send_game_update(game):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(game.code, {"type": "chat_message", "game": serialize_game(game)})
