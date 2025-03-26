# workflows/utils.py
import logging
import io
from gtts import gTTS
from transformers import pipeline

logger = logging.getLogger(__name__)
summarizer_pipeline = pipeline("summarization", model="facebook/bart-large-cnn")

def execute_node(node, input_data, continue_on_error=False):
    """
    Execute a node with enhanced error handling and logging
    """
    try:
        # Handle None input
        if input_data is None:
            input_data = ""  # Default to empty string

        logger.info(f"Executing Node {node.id} ({node.type}) with input: {str(input_data)[:50]}...")
        
        result = None
        
        if node.type == "text_input":
            result = input_data
            
        elif node.type == "openai_tts":
            # Extract text from the dictionary
            if isinstance(input_data, dict):
                input_data = input_data.get("result", "")  # Extract text safely

            if not isinstance(input_data, str) or not input_data.strip():
                raise ValueError("Invalid input for TTS: Expected a non-empty string.")
            # Simulate TTS with error simulation
            if "simulate_failure" in node.config:
                raise ConnectionError("Simulated API connection failure")
                
            tts = gTTS(text=input_data, lang='en')
            audio_file = io.BytesIO()
           
            tts.write_to_fp(audio_file)
            audio_file.seek(0)
            result = "TTS audio generated successfully"
            
        elif node.type == "huggingface_summarization":
            summary = summarizer_pipeline(input_data)
            result = summary[0].get("summary_text", "No summary found")
            
        else:
            raise ValueError(f"Unknown node type: {node.type}")
            
        logger.info(f"Node {node.id} executed successfully. Output: {str(result)[:50]}...")
        return result
        
    except Exception as e:
        logger.error(f"Error in Node {node.id}: {str(e)}", exc_info=True)
        if not continue_on_error:
            raise  # Propagate error to stop workflow
        return f"ERROR: {str(e)}"