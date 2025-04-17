class MockTextInputHandler:
    def execute(self, node, input_data=None):
        return node.config.get('text', 'default text')

class MockTTSHandler:
    def execute(self, node, input_data):
        return f"TTS audio generated for: {input_data}"

class MockSummarizationHandler:
    def execute(self, node, input_data):
        return f"Summary of: {input_data[:50]}..."

# Register mock handlers
HANDLERS = {
    'text_input': MockTextInputHandler,
    'openai_tts': MockTTSHandler,
    'huggingface_summarization': MockSummarizationHandler
}