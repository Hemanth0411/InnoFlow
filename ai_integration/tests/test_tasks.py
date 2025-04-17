from django.test import TestCase
from unittest.mock import patch, MagicMock
from ai_integration.tasks import run_ai_model_task
from ai_integration.models import AIModelConfig, ModelComparison, ModelResponse
from ai_integration.providers_registry import ProviderRegistry

class RunAIModelTaskTest(TestCase):
    def setUp(self):
        self.model_config = AIModelConfig.objects.create(
            name="Test Model",
            provider="OPENAI",
            model_name="gpt-3.5-turbo",
            is_active=True,
            api_key="test_key",
            parameters={}  # ✅ FIX: set empty or dummy parameters
        )
        self.comparison = ModelComparison.objects.create(
        prompt="Test prompt"
    )
        self.comparison.compared_models.add(self.model_config)
    
    @patch('ai_integration.providers_registry.ProviderRegistry.get_provider')
    def test_run_openai_task(self, mock_get_provider):
        # Mock the provider
        mock_provider = MagicMock()
        mock_provider.generate_completion.return_value = "OpenAI response"
        mock_get_provider.return_value = mock_provider
        
        # Call the task
        response = run_ai_model_task(self.model_config.id, "Test prompt", self.comparison.id)
        
        # Check that the provider was called
        mock_provider.generate_completion.assert_called_once_with("Test prompt")
        
        # Check the response
        self.assertEqual(response, "OpenAI response")
        
        # Check that a ModelResponse was created
        model_response = ModelResponse.objects.get(
        comparison=self.comparison, model_config=self.model_config
        )

        self.assertEqual(model_response.response, "OpenAI response")
        self.assertIsNotNone(model_response.latency)
    
    @patch('ai_integration.providers_registry.ProviderRegistry.get_provider')
    def test_run_claude_task(self, mock_get_provider):
        # Update model config to use Anthropic
        self.model_config.provider = "ANTHROPIC"
        self.model_config.save()
        
        # Mock the provider
        mock_provider = MagicMock()
        mock_provider.generate_completion.return_value = "Claude response"
        mock_get_provider.return_value = mock_provider
        
        # Call the task
        response = run_ai_model_task(self.model_config.id, "Test prompt", self.comparison.id)
        
        # Check that the provider was called
        mock_provider.generate_completion.assert_called_once_with("Test prompt")
        
        # Check the response
        self.assertEqual(response, "Claude response")