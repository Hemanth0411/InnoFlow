from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    def generate_completion(self, prompt: str, **kwargs) -> str:
        """Generate a completion based on the prompt."""
        pass