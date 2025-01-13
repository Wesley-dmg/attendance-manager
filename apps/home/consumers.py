# from channels.generic.websocket import AsyncWebsocketConsumer
# import json

# class NotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = "notifications"
#         self.room_group_name = f'notifications_{self.user.id}'

#         # Joindre le groupe
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#         await self.accept()

#     async def disconnect(self, close_code):
#         # Quitter le groupe
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     # Recevoir une notification depuis le WebSocket
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']

#         # Envoyer le message à tous les membres du groupe
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message
#             }
#         )

#     # Recevoir un message du groupe
#     async def chat_message(self, event):
#         message = event['message']

#         # Envoyer le message au WebSocket
#         await self.send(text_data=json.dumps({
#             'message': message
#         }))
