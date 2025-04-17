from unittest.mock import patch, MagicMock
from unittest import TestCase
from ai_integration.utils.claude_provider import ClaudeProvider 
from ai_integration.utils.deepseek_provider import DeepSeekProvider 
from ai_integration.utils.openai_provider import OpenAIProvider
from ai_integration.utils.huggingface_provider import HuggingFaceProvider 
from ai_integration.utils.ollama_provider import OllamaProvider

class TestClaudeProvider(TestCase):
    @patch('anthropic.Client')
    def test_generate_completion(self, mock_client):
        api_key = "your_claude_api_key"
        provider = ClaudeProvider(api_key)
        prompt = "Hello, how are you?"
        
        mock_response = MagicMock()
        mock_response.completion = 'I am fine, thank you!'
        mock_client.return_value.completions.create.return_value = mock_response
        
        response = provider.generate_completion(prompt)
        self.assertIsNotNone(response)
        self.assertEqual(response, 'I am fine, thank you!')

class TestDeepSeekProvider(TestCase):
    @patch('requests.post')
    def test_generate_completion(self, mock_post):
        api_key = "your_deepseek_api_key"
        model_name = "your_model_name"
        provider = DeepSeekProvider(api_key, model_name)
        prompt = "Hello, how are you?"
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "I am fine, thank you!"}}]}
        mock_response.raise_for_status = MagicMock()  # Mock the raise_for_status method
        mock_post.return_value = mock_response
        
        response = provider.generate_completion(prompt)
        self.assertIsNotNone(response)
        self.assertEqual(response, 'I am fine, thank you!')

class TestHuggingFaceProvider(TestCase):
    @patch('ai_integration.utils.huggingface_provider.pipeline')
    def test_generate_completion(self, mock_pipeline):
        model_name = "gpt2"
        provider = HuggingFaceProvider(model_name)
        prompt = "Hello, how are you?"

        # Simulate the callable pipeline returning our mocked text
        mock_callable = MagicMock()
        mock_callable.return_value = [{"generated_text": "I am fine, thank you!"}]
        mock_pipeline.return_value = mock_callable

        response = provider.generate_completion(prompt)
        self.assertIsNotNone(response)
        self.assertEqual(response, 'I am fine, thank you!')

class TestOllamaProvider(TestCase):
    @patch('requests.post')
    def test_generate_completion(self, mock_post):
        base_url = "http://your_ollama_base_url"
        model_name = "your_model_name"
        provider = OllamaProvider(base_url, model_name)
        prompt = "Hello, how are you?"
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "I am fine, thank you!"}
        mock_response.raise_for_status = MagicMock()  # Mock the raise_for_status method
        mock_post.return_value = mock_response
        
        response = provider.generate_completion(prompt)
        self.assertIsNotNone(response)
        self.assertEqual(response, 'I am fine, thank you!')

class TestOpenAIProvider(TestCase):
    @patch('openai.ChatCompletion.create')
    def test_generate_completion(self, mock_create):
        api_key = "your_openai_api_key"
        model_name = "gpt-3.5-turbo"
        provider = OpenAIProvider(api_key, model_name)
        prompt = "Hello, how are you?"
        
        mock_message = MagicMock()
        mock_message.content = 'I am fine, thank you!'

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_create.return_value = mock_response

        
        response = provider.generate_completion(prompt)
        self.assertIsNotNone(response)
        self.assertEqual(response, 'I am fine, thank you!')