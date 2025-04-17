import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from workflows.models import Workflow, Node, WorkflowExecution, NodeConnection
from workflows.tasks import run_workflow
from celery import shared_task
from workflows.serializers import NodeSerializer, WorkflowExecutionSerializer, WorkflowSerializer
from workflows.execution import execute_node

User = get_user_model()

class WorkflowManagementSystemTests(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        
    # Workflow Model Tests
    def test_create_workflow(self):
        workflow = Workflow.objects.create(name='Test Workflow', user=self.user)
        self.assertEqual(workflow.name, 'Test Workflow')
        self.assertEqual(workflow.user, self.user)
        
    def test_workflow_string_representation(self):
        workflow = Workflow.objects.create(name='Test Workflow', user=self.user)
        self.assertEqual(str(workflow), 'Test Workflow')
        
    # Node Model Tests
    def test_create_node(self):
        workflow = Workflow.objects.create(name='Test Workflow', user=self.user)
        node = Node.objects.create(
            workflow=workflow,
            type='text_input',
            config={'text': 'Hello, World!'},
            order=1
        )
        self.assertEqual(node.type, 'text_input')
        self.assertEqual(node.order, 1)
        
    def test_node_string_representation(self):
        workflow = Workflow.objects.create(name='Test Workflow', user=self.user)
        node = Node.objects.create(
            workflow=workflow,
            type='text_input',
            config={'text': 'Hello, World!'},
            order=1
        )
        self.assertEqual(str(node), f'text_input (Workflow: Test Workflow)')
        
    # WorkflowExecution Model Tests
    def test_create_workflow_execution(self):
        workflow = Workflow.objects.create(name='Test Workflow', user=self.user)
        execution = WorkflowExecution.objects.create(
            workflow=workflow,
            status='pending'
        )
        self.assertEqual(execution.status, 'pending')
        
    def test_workflow_execution_string_representation(self):
        workflow = Workflow.objects.create(name='Test Workflow', user=self.user)
        execution = WorkflowExecution.objects.create(
            workflow=workflow,
            status='pending'
        )
        self.assertEqual(str(execution), f'Execution of Test Workflow (Pending)')
        
    # NodeConnection Model Tests
    def test_create_node_connection(self):
        workflow = Workflow.objects.create(name='Test Workflow', user=self.user)
        node1 = Node.objects.create(
            workflow=workflow,
            type='text_input',
            config={'text': 'Hello, World!'},
            order=1
        )
        node2 = Node.objects.create(
            workflow=workflow,
            type='openai_tts',
            config={'voice': 'en'},
            order=2
        )
        connection = NodeConnection.objects.create(
            source_node=node1,
            target_node=node2,
            source_port='output',
            target_port='input'
        )
        self.assertEqual(connection.source_node, node1)
        self.assertEqual(connection.target_node, node2)
        
    # Workflow Serializer Tests
    def test_workflow_serializer(self):
        workflow = Workflow.objects.create(name='Test Workflow', user=self.user)
        serializer = WorkflowSerializer(workflow)
        self.assertIn('id', serializer.data)
        self.assertIn('name', serializer.data)
        self.assertIn('nodes', serializer.data)
        
    # Node Serializer Tests
    def test_node_serializer(self):
        workflow = Workflow.objects.create(name='Test Workflow', user=self.user)
        node = Node.objects.create(
            workflow=workflow,
            type='text_input',
            config={'text': 'Hello, World!'},
            order=1
        )
        serializer = NodeSerializer(node)
        self.assertIn('id', serializer.data)
        self.assertIn('type', serializer.data)
        self.assertIn('config', serializer.data)
        
    # WorkflowExecution Serializer Tests
    def test_workflow_execution_serializer(self):
        workflow = Workflow.objects.create(name='Test Workflow', user=self.user)
        execution = WorkflowExecution.objects.create(
            workflow=workflow,
            status='pending'
        )
        serializer = WorkflowExecutionSerializer(execution)
        self.assertIn('id', serializer.data)
        self.assertIn('status', serializer.data)
        self.assertIn('results', serializer.data)
        
    # Workflow View Tests
    def test_workflow_list_view(self):
        url = reverse('workflow-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_workflow_detail_view(self):
        workflow = Workflow.objects.create(name='Test Workflow', user=self.user)
        url = reverse('workflow-detail', args=[workflow.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_create_workflow_view(self):
        url = reverse('workflow-list')
        data = {
            'name': 'New Workflow',
            'user': self.user.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    # Node View Tests
    def test_node_list_view(self):
        workflow = Workflow.objects.create(name='Test Workflow', user=self.user)
        url = reverse('node-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_node_detail_view(self):
        workflow = Workflow.objects.create(name='Test Workflow', user=self.user)
        node = Node.objects.create(
            workflow=workflow,
            type='text_input',
            config={'text': 'Hello, World!'},
            order=1
        )
        url = reverse('node-detail', args=[node.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_create_node_view(self):
        workflow = Workflow.objects.create(name='Test Workflow', user=self.user)
        url = reverse('node-list')
        data = {
            'workflow': workflow.id,
            'type': 'text_input',
            'config': {'text': 'Hello, World!'},
            'order': 1
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    # WorkflowExecution View Tests
    def test_workflow_execution_list_view(self):
        workflow = Workflow.objects.create(name='Test Workflow', user=self.user)
        url = reverse('workflowexecution-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_workflow_execution_detail_view(self):
        workflow = Workflow.objects.create(name='Test Workflow', user=self.user)
        execution = WorkflowExecution.objects.create(
            workflow=workflow,
            status='pending'
        )
        url = reverse('workflowexecution-detail', args=[execution.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    # Task Tests
    def test_run_workflow_task(self):
        workflow = Workflow.objects.create(name='Test Workflow', user=self.user)
        execution = WorkflowExecution.objects.create(
            workflow=workflow,
            status='pending'
        )
        run_workflow.delay(workflow.id, execution.id)
        # Wait for task to complete (in a real test, you might need to mock Celery tasks)
        execution.refresh_from_db()
        self.assertIn(execution.status, ['completed', 'failed'])
        
    # Utils Tests
    def test_execute_node_util(self):
        workflow = Workflow.objects.create(name='Test Workflow', user=self.user)
        node = Node.objects.create(
            workflow=workflow,
            type='text_input',
            config={'text': 'Hello, World!'},
            order=1
        )
        result = execute_node(node, None)
        self.assertEqual(result, 'Hello, World!')
        
    def test_execute_tts_node_util(self):
        workflow = Workflow.objects.create(name='Test Workflow', user=self.user)
        node = Node.objects.create(
            workflow=workflow,
            type='openai_tts',
            config={'voice': 'en'},
            order=1
        )
        input_data = {'result': 'Hello, World!'}
        result = execute_node(node, input_data)
        self.assertEqual(result, 'TTS audio generated successfully')
        
    def test_execute_summarization_node_util(self):
        workflow = Workflow.objects.create(name='Test Workflow', user=self.user)
        node = Node.objects.create(
            workflow=workflow,
            type='huggingface_summarization',
            config={},
            order=1
        )
        input_data = 'This is a sample text to summarize.'
        result = execute_node(node, input_data)
        self.assertIsNotNone(result)