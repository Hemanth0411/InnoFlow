import requests
from ..ai_providers import AIProvider

class OllamaProvider(AIProvider):
    def __init__(self, base_url: str, model_name: str):
        self.base_url = base_url
        self.model_name = model_name

    def generate_completion(self, prompt: str, **kwargs):
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    **kwargs
                }
            )
            response.raise_for_status()
            return response.json().get("response")
        except Exception as e:
            print(f"Ollama Error: {e}")
            return None