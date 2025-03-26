# workflows/tests.py
from django.test import TestCase
from workflows.utils import execute_node
from workflows.models import Workflow, Node
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()

class AdvancedExecuteNodeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass')
        cls.workflow = Workflow.objects.create(
            name="Test Workflow",
            user=cls.user,
            config={'continue_on_error': True}
        )
        
    def test_continue_on_error(self):
        node1 = Node.objects.create(
            workflow=self.workflow,
            type="text_input",
            order=1
        )
        node2 = Node.objects.create(
            workflow=self.workflow,
            type="force_failure",
            order=2
        )
        
        # First node should succeed
        result1 = execute_node(node1, "Test input", continue_on_error=True)
        self.assertEqual(result1, "Test input")
        
        # Second node should fail but continue
        with self.assertLogs(logger='workflows.utils', level='ERROR') as cm:
            result2 = execute_node(node2, "Test input", continue_on_error=True)
            self.assertIn("ERROR", result2)
            self.assertIn("Unknown node type", cm.output[0])

    @patch('workflows.utils.gTTS')
    def test_network_failure(self, mock_tts):
        mock_tts.side_effect = ConnectionError("API unavailable")
        node = Node.objects.create(
            workflow=self.workflow,
            type="openai_tts",
            config={'simulate_failure': True},
            order=1
        )
        
        with self.assertRaises(ConnectionError):
            execute_node(node, "Test input", continue_on_error=False)

    def test_async_execution_flow(self):
        # Test full workflow execution through Celery
        from workflows.tasks import run_workflow
        
        # Create test nodes
        Node.objects.create(
            workflow=self.workflow,
            type="text_input",
            order=1
        )
        Node.objects.create(
            workflow=self.workflow,
            type="openai_tts",
            order=2
        )
        
        result = run_workflow(self.workflow.id)
        self.assertEqual(result['completed_nodes'], 2)
        self.assertTrue(result['success'])