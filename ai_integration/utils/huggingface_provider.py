from transformers import pipeline
from ..ai_providers import AIProvider

class HuggingFaceProvider(AIProvider):
    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate_completion(self, prompt: str, **kwargs):
        try:
            generator = pipeline("text-generation", model=self.model_name)
            result = generator(prompt, **kwargs)
            return result[0]["generated_text"]
        except Exception as e:
            print(f"HuggingFace Error: {e}")
            return None