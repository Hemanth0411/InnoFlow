from django.test import TestCase
from unittest.mock import patch, MagicMock
from ai_integration.providers_registry import ProviderRegistry

class OpenAIUtilsTest(TestCase):
    @patch('ai_integration.providers_registry.ProviderRegistry.get_provider')
    def test_openai_text_completion_success(self, mock_get_provider):
        # Mock the provider
        mock_provider = MagicMock()
        mock_provider.generate_completion.return_value = "Test response"
        mock_get_provider.return_value = mock_provider
        
        # Get the provider
        provider = ProviderRegistry.get_provider(
            "openai",
            api_key="test_key",
            model_name="gpt-3.5-turbo"
        )
        
        # Call the function
        result = provider.generate_completion("Test prompt")
        
        # Verify
        self.assertEqual(result, "Test response")