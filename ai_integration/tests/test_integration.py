from django.test import TestCase
from ai_integration.models import AIModelConfig, ModelComparison, ModelResponse
from ai_integration.tasks import run_ai_model_task
from unittest.mock import patch, MagicMock

class TestFullWorkflow(TestCase):
    @patch('ai_integration.providers_registry.ProviderRegistry.get_provider')
    def test_full_workflow(self, mock_get_provider):
        # Mock the provider and its generate_completion method
        mock_provider = MagicMock()
        mock_provider.generate_completion.return_value = 'I am fine, thank you!'
        mock_get_provider.return_value = mock_provider

        model_config = AIModelConfig.objects.create(
            name="Test Model",
            provider="OPENAI",
            model_name="gpt-3.5-turbo",
            api_key="your_openai_api_key"
        )
        comparison = ModelComparison.objects.create(prompt="Test prompt")

        run_ai_model_task(model_config.id, comparison.prompt, comparison.id)

        # Check if ModelResponse was created
        self.assertTrue(ModelResponse.objects.filter(comparison=comparison).exists())

        # Check if the response is not null
        model_response = ModelResponse.objects.get(comparison=comparison)
        self.assertIsNotNone(model_response.response)