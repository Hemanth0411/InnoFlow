from celery import shared_task
from ai_integration.models import AIModelConfig, ModelComparison, ModelResponse
from ai_integration.providers_registry import ProviderRegistry
import time

@shared_task
def run_ai_model_task(model_config_id: int, prompt: str, comparison_id: int) -> str:
    model_config = AIModelConfig.objects.get(id=model_config_id)
    
    start_time = time.time()
    
    # Use the provider registry to generate completion
    provider = ProviderRegistry.get_provider(
        model_config.provider.lower(),
        api_key=model_config.api_key,
        model_name=model_config.model_name,
        base_url=model_config.base_url
    )
    
    response = provider.generate_completion(prompt)
    
    latency = time.time() - start_time
    
    # Save the response
    comparison = ModelComparison.objects.get(id=comparison_id)
    ModelResponse.objects.create(
        comparison=comparison,
        model_config=model_config,
        response=response,
        latency=latency
    )
    
    return response