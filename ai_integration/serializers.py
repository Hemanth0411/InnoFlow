from rest_framework import serializers
from .models import AIModelConfig, ModelComparison, ModelResponse
from .models import TaskStatus

class AIModelConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIModelConfig
        fields = ['id', 'name', 'provider', 'model_name', 'is_active', 'parameters']

class ModelResponseSerializer(serializers.ModelSerializer):
    model_config = AIModelConfigSerializer()
    
    class Meta:
        model = ModelResponse
        fields = ['id', 'model_config', 'response', 'latency', 'created_at']

class ModelComparisonSerializer(serializers.ModelSerializer):
    compared_models = serializers.PrimaryKeyRelatedField(
        many=True, queryset=AIModelConfig.objects.all()
    )

    class Meta:
        model = ModelComparison
        fields = ['id', 'prompt', 'compared_models', 'created_at']

class CompareModelsSerializer(serializers.Serializer):
    prompt = serializers.CharField()
    model_ids = serializers.ListField(child=serializers.IntegerField())

class TaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStatus
        fields = '__all__'