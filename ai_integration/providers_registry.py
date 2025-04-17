from .utils.openai_provider import OpenAIProvider
from .utils.huggingface_provider import HuggingFaceProvider
from .utils.ollama_provider import OllamaProvider
from .utils.claude_provider import ClaudeProvider
from .utils.deepseek_provider import DeepSeekProvider

class ProviderRegistry:
    _providers = {}

    @classmethod
    def register_provider(cls, provider_name: str, provider_class):
        cls._providers[provider_name] = provider_class

    @classmethod
    def get_provider(cls, provider_name: str, **kwargs):
        provider_class = cls._providers.get(provider_name)
        if not provider_class:
            raise ValueError(f"Provider '{provider_name}' not found")
        return provider_class(**kwargs)

# Register providers
ProviderRegistry.register_provider("openai", OpenAIProvider)
ProviderRegistry.register_provider("huggingface", HuggingFaceProvider)
ProviderRegistry.register_provider("ollama", OllamaProvider)
ProviderRegistry.register_provider("claude", ClaudeProvider)
ProviderRegistry.register_provider("deepseek", DeepSeekProvider)