from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import AIModelConfig, ModelComparison, TaskStatus
from .serializers import AIModelConfigSerializer, ModelComparisonSerializer
from .utils.openai_provider import OpenAIProvider
from .serializers import TaskStatusSerializer
from .providers_registry import ProviderRegistry
from ai_integration.tasks import run_ai_model_task  # Import the task here
from django.db import transaction

class TaskStatusViewSet(viewsets.ModelViewSet):
    queryset = TaskStatus.objects.all()
    serializer_class = TaskStatusSerializer
    
class AIModelConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet for AI model configurations
    """
    queryset = AIModelConfig.objects.all()
    serializer_class = AIModelConfigSerializer


class ModelComparisonViewSet(viewsets.ModelViewSet):
    queryset = ModelComparison.objects.all()
    serializer_class = ModelComparisonSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        prompt = serializer.validated_data['prompt']
        model_configs = serializer.validated_data['compared_models']
        
        # Create the comparison instance
        comparison = serializer.save()
        
        # Prepare results structure
        results = {}
        
        # Use on_commit to ensure the task runs after the transaction is committed
        transaction.on_commit(lambda: self._run_ai_model_task(comparison.id, prompt, model_configs))
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def _run_ai_model_task(self, comparison_id, prompt, model_configs):
        for model_config in model_configs:
            run_ai_model_task.delay(
                model_config_id=model_config.id,
                prompt=prompt,
                comparison_id=comparison_id
            )
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        comparison = self.get_object()
        # Just an example response; you can change as needed
        return Response({
            "comparison_id": comparison.id,
            "results": "Dummy results or actual data"
        })

    @action(detail=False, methods=['post'], url_path='compare-models')
    def compare_models(self, request):
        prompt = request.data.get('prompt')
        models = request.data.get('models')
        
        # Your model comparison logic
        results = {}
        for model_id in models:
            model = AIModelConfig.objects.get(id=model_id)
            provider = OpenAIProvider(api_key=model.api_key, model_name=model.model_name)
            response = provider.generate_completion(prompt)
            results[model.name] = response
        
        # Create a comparison object
        comparison = ModelComparison.objects.create(prompt=prompt)
        comparison.results = results
        comparison.save()
        
        # Triggering the task with the required arguments
        run_ai_model_task.delay(
            model_config_id=comparison.id,  # The model configuration ID
            prompt=prompt,  # The prompt
            comparison_id=comparison.id  # The comparison ID
        )
        
        return Response({
            "comparison_id": comparison.id,
            "results": results
        }, status=status.HTTP_201_CREATED)
