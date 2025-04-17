# workflows/tests/test_integration.py
from channels.testing import WebsocketCommunicator
from django.test import TestCase
from workflows.consumers import WorkflowExecutionConsumer
import json

class WorkflowExecutionIntegrationTest(TestCase):
    async def test_workflow_execution_with_websocket(self):
        communicator = WebsocketCommunicator(WorkflowExecutionConsumer, "/ws/workflow-executions/1/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Simulate a workflow execution update
        await communicator.send_json_to({
            'type': 'send_update',
            'message': 'Workflow execution started',
            'status': 'running'
        })

        response = await communicator.receive_json_from()
        self.assertEqual(response['status'], 'running')
        self.assertEqual(response['message'], 'Workflow execution started')

        await communicator.disconnect()