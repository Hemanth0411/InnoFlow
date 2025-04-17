from django.test import TestCase
from ai_integration.models import AIModelConfig, ModelComparison, ModelResponse, TaskStatus

class TestAIModelConfig(TestCase):
    def test_create_model_config(self):
        model_config = AIModelConfig(
            name="Test Model",
            provider="OPENAI",
            model_name="gpt-3.5-turbo",
            api_key="your_openai_api_key"
        )
        model_config.save()
        self.assertEqual(model_config.name, "Test Model")
        
class TestModelComparison(TestCase):
    def test_create_model_comparison(self):
        model_config = AIModelConfig.objects.create(
            name="Test Model",
            provider="OPENAI",
            model_name="gpt-3.5-turbo",
            api_key="your_openai_api_key"
        )
        comparison = ModelComparison.objects.create(prompt="Test prompt")
        comparison.compared_models.add(model_config)
        self.assertEqual(comparison.prompt, "Test prompt")

class TestModelResponse(TestCase):
    def test_create_model_response(self):
        model_config = AIModelConfig.objects.create(
            name="Test Model",
            provider="OPENAI",
            model_name="gpt-3.5-turbo",
            api_key="your_openai_api_key"
        )
        comparison = ModelComparison.objects.create(prompt="Test prompt")
        response = ModelResponse.objects.create(
            comparison=comparison,
            model_config=model_config,
            response="Test response",
            latency=0.5
        )
        self.assertEqual(response.response, "Test response")

class TestTaskStatus(TestCase):
    def test_create_task_status(self):
        task_status = TaskStatus.objects.create(
            task_id="test_task_id",
            status="pending"
        )
        self.assertEqual(task_status.task_id, "test_task_id")