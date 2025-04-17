from django.test import TestCase
from ai_integration.models import AIModelConfig, ModelComparison, ModelResponse
from ai_integration.serializers import (
    AIModelConfigSerializer, 
    ModelResponseSerializer, 
    ModelComparisonSerializer,
    CompareModelsSerializer
)

class AIModelConfigSerializerTest(TestCase):
    def setUp(self):
        self.model_data = {
            'name': 'Test Model',
            'provider': 'OPENAI',
            'model_name': 'gpt-4-turbo',
            'is_active': True,
            'parameters': {}  # 
        }

        self.model = AIModelConfig.objects.create(**self.model_data)
        self.serializer = AIModelConfigSerializer(instance=self.model)
    
    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'name', 'provider', 'model_name', 'is_active', 'parameters']))
    
    def test_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['name'], self.model_data['name'])
        self.assertEqual(data['provider'], self.model_data['provider'])
        self.assertEqual(data['model_name'], self.model_data['model_name'])
        self.assertEqual(data['is_active'], self.model_data['is_active'])
        self.assertEqual(data['parameters'], self.model_data['parameters'])

class CompareModelsSerializerTest(TestCase):
    def test_valid_data(self):
        data = {
            'prompt': 'Test prompt',
            'model_ids': [1, 2, 3]
        }
        serializer = CompareModelsSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_invalid_data(self):
        # Missing required field
        data = {'prompt': 'Test prompt'}
        serializer = CompareModelsSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('model_ids', serializer.errors)
        
        # Invalid model_ids format
        data = {'prompt': 'Test prompt', 'model_ids': 'not_a_list'}
        serializer = CompareModelsSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('model_ids', serializer.errors)