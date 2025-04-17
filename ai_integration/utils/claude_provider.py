import anthropic
from django.conf import settings
from ..ai_providers import AIProvider

class ClaudeProvider(AIProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_completion(self, prompt: str, **kwargs):
        try:
            client = anthropic.Client(self.api_key)
            response = client.completions.create(
                prompt=f"{anthropic.HUMAN_PROMPT} {prompt}{anthropic.AI_PROMPT}",
                model="claude-2",
                max_tokens_to_sample=1000,
                **kwargs
            )
            return response.completion
        except Exception as e:
            print(f"Claude Error: {e}")
            return None