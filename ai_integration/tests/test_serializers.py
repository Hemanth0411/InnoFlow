from rest_framework.test import APITestCase
from ai_integration.serializers import AIModelConfigSerializer, ModelComparisonSerializer, ModelResponseSerializer, CompareModelsSerializer, TaskStatusSerializer
from ai_integration.models import AIModelConfig, ModelResponse, ModelComparison, TaskStatus

class TestAIModelConfigSerializer(APITestCase):
    def test_serialize_model_config(self):
        model_config = AIModelConfig.objects.create(
            name="Test Model",
            provider="OPENAI",
            model_name="gpt-3.5-turbo",
            api_key="your_openai_api_key"
        )
        serializer = AIModelConfigSerializer(model_config)
        self.assertIn("name", serializer.data)
        self.assertIn("provider", serializer.data)

class TestModelResponseSerializer(APITestCase):
    def test_serialize_model_response(self):
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
        serializer = ModelResponseSerializer(response)
        self.assertIn("response", serializer.data)
        self.assertIn("latency", serializer.data)

class TestModelComparisonSerializer(APITestCase):
    def test_serialize_model_comparison(self):
        model_config = AIModelConfig.objects.create(
            name="Test Model",
            provider="OPENAI",
            model_name="gpt-3.5-turbo",
            api_key="your_openai_api_key"
        )
        comparison = ModelComparison.objects.create(prompt="Test prompt")
        comparison.compared_models.add(model_config)
        serializer = ModelComparisonSerializer(comparison)
        self.assertIn("prompt", serializer.data)
        self.assertIn("compared_models", serializer.data)

class TestTaskStatusSerializer(APITestCase):
    def test_serialize_task_status(self):
        task_status = TaskStatus.objects.create(
            task_id="test_task_id",
            status="pending"
        )
        serializer = TaskStatusSerializer(task_status)
        self.assertIn("task_id", serializer.data)
        self.assertIn("status", serializer.data)