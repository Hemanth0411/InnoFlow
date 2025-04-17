import openai
from django.conf import settings
from ..ai_providers import AIProvider

class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name

    def generate_completion(self, prompt: str, **kwargs):
        try:
            openai.api_key = self.api_key
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI Error: {e}")
            return None