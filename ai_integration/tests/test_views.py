from rest_framework.test import APITestCase
from ai_integration.models import AIModelConfig, ModelResponse, ModelComparison, TaskStatus

class TestAIModelConfigViewSet(APITestCase):
    def test_list_model_configs(self):
        AIModelConfig.objects.create(
            name="Test Model",
            provider="OPENAI",
            model_name="gpt-3.5-turbo",
            api_key="your_openai_api_key"
        )
        response = self.client.get('/ai/aimodelconfig/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

class TestModelComparisonViewSet(APITestCase):
    def test_create_model_comparison(self):
        model_config = AIModelConfig.objects.create(
            name="Test Model",
            provider="OPENAI",
            model_name="gpt-3.5-turbo",
            api_key="your_openai_api_key"
        )
        data = {
            "prompt": "Test prompt",
            "compared_models": [model_config.id]
        }
        # Ensure the model_config is not deleted before the task is executed
        model_config_id = model_config.id
        response = self.client.post('/ai/modelcomparison/', data, format='json')
        self.assertEqual(response.status_code, 201)
        # You can also check if the task was triggered correctly
        # from celery.result import AsyncResult
        # task_id = response.json().get('task_id')
        # task_result = AsyncResult(task_id)
        # self.assertEqual(task_result.status, 'PENDING')

class TestTaskStatusViewSet(APITestCase):
    def test_list_task_status(self):
        TaskStatus.objects.create(
            task_id="test_task_id",
            status="pending"
        )
        response = self.client.get('/ai/taskstatus/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)