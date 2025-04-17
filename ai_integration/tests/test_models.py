from django.test import TestCase
from ai_integration.models import AIModelConfig, ModelComparison, ModelResponse

class AIModelConfigTest(TestCase):
    def test_create_model_config(self):
        config = AIModelConfig.objects.create(
            name="GPT-3.5",
            provider="OPENAI",
            model_name="gpt-3.5-turbo",
            api_key="test_key"
        )
        self.assertEqual(str(config), "OPENAI: gpt-3.5-turbo")

class ModelComparisonTest(TestCase):
    def test_comparison_creation(self):
        comparison = ModelComparison.objects.create(
            prompt="Test prompt"
        )
        self.assertEqual(str(comparison), "Comparison for: Test prompt...")

class ModelResponseTest(TestCase):
    def setUp(self):
        self.comparison = ModelComparison.objects.create(prompt="Test prompt")
        self.config = AIModelConfig.objects.create(
            name="GPT-3.5",
            provider="OPENAI",
            model_name="gpt-3.5-turbo",
            api_key="test_key"
        )
    
    def test_response_creation(self):
        response = ModelResponse.objects.create(
            comparison=self.comparison,
            model_config=self.config,
            response="Test response",
            latency=1.5
        )
        self.assertEqual(str(response), "OPENAI: gpt-3.5-turbo: Test response...")