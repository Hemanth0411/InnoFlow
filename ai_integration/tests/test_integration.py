from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch
from ai_integration.models import AIModelConfig
from ai_integration.providers_registry import ProviderRegistry

# to run this: 
# 1. Open wsl and run this command: sudo service redis-server start
# 2. Then run this:  redis-cli ping
# 3. If you get PONG as output then your redis server is running.

class IntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.model_url = reverse('aimodelconfig-list')
        self.compare_url = reverse('modelcomparison-compare-models')  # This should now work
    
    @patch('ai_integration.views.run_ai_model_task')
    def test_full_workflow(self, mock_run_task):
        # Mock the delay method
        mock_run_task.delay.return_value = "Mocked AI response"

        # Create a model config
        model_data = {
            'name': 'Test GPT Model',
            'provider': 'OPENAI',
            'model_name': 'gpt-3.5-turbo',
            'api_key': 'test-key'
        }
        response = self.client.post(self.model_url, model_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        model_id = response.data['id']

        # Compare models
        comparison_data = {
            'prompt': 'Test prompt',
            'models': [model_id]
        }
        response = self.client.post(self.compare_url, comparison_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # ✅ Check that delay was called
        mock_run_task.delay.assert_called_once()
