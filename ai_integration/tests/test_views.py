from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ai_integration.models import AIModelConfig, ModelComparison
from unittest.mock import patch, MagicMock

class AIModelConfigViewSetTest(APITestCase):
    def setUp(self):
        self.url = reverse('aimodelconfig-list')  # Ensure this matches your URL name
        self.model_data = {
            'name': 'Test Model',
            'provider': 'OPENAI',
            'model_name': 'gpt-3.5-turbo',
            'is_active': True,
            'api_key': 'test-key',
            'parameters': {}  # Provide a default value for parameters
        }
        
    def test_create_model(self):
        response = self.client.post(self.url, self.model_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AIModelConfig.objects.count(), 1)
        
    def test_list_models(self):
        AIModelConfig.objects.create(**self.model_data)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class ModelComparisonViewSetTest(APITestCase):
    def setUp(self):
        # Create test models with parameters
        self.model1 = AIModelConfig.objects.create(
            name='Model 1',
            provider='OPENAI',
            model_name='gpt-3.5-turbo',
            api_key='test-key-1',
            is_active=True,
            parameters={}  # Provide a default value for parameters
        )
        
        self.model2 = AIModelConfig.objects.create(
            name='Model 2',
            provider='HUGGINGFACE',
            model_name='gpt2',
            api_key='test-key-2',
            is_active=True,
            parameters={}  # Provide a default value for parameters
        )
        
        # Create a comparison
        self.comparison = ModelComparison.objects.create(
            prompt='Test results prompt'
        )
        # Add models to the comparison
        self.comparison.compared_models.add(self.model1, self.model2)
        
        # Set up URLs
        self.comparison_url = reverse('modelcomparison-list')  # Ensure this matches your URL name
        
        # Create comparison data
        self.comparison_data = {
            'prompt': 'Test prompt',
            'compared_models': [self.model1.id, self.model2.id]
        }
        
        # Set up results URL
        self.results_url = reverse('modelcomparison-results', args=[self.comparison.id])
    
    @patch('ai_integration.views.ProviderRegistry.get_provider')
    def test_compare_models(self, mock_get_provider):
        # Mock the provider
        mock_provider = MagicMock()
        mock_provider.generate_completion.return_value = "Mocked response"
        mock_get_provider.return_value = mock_provider
        
        response = self.client.post(self.comparison_url, self.comparison_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ModelComparison.objects.count(), 2)  # 1 from setUp + 1 new
        
    def test_get_results(self):
        response = self.client.get(self.results_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)