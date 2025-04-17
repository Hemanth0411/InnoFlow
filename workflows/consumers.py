import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging

logger = logging.getLogger(__name__)

class WorkflowExecutionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        execution_id = self.scope.get('url_route', {}).get('kwargs', {}).get('execution_id')
        if not execution_id:
            await self.close()
            return
        self.execution_id = execution_id
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.execution_group_name,
            self.channel_name
        )

    async def send_update(self, event):
        message = event['message']
        status = event['status']
        results = event.get('results', {})
        errors = event.get('errors', {})

        await self.send(text_data=json.dumps({
            'message': message,
            'status': status,
            'results': results,
            'errors': errors
        }))