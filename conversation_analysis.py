import re
import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("conversation_analysis")

def split_sentences(text: str) -> list:
    """
    Split text into sentences using basic punctuation markers.
    
    This function splits text based on periods, exclamation marks, or question marks
    followed by a space. This is a simple approach for sentence segmentation.
    
    Args:
        text (str): The input text to be split into sentences.
        
    Returns:
        list: A list of individual sentences from the input text.
    """
    # Use \s+ to split on any whitespace (spaces, newlines, tabs) following
    # punctuation. This prevents sentences separated by newlines or multiple
    # spaces from being joined together.
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return sentences

def analyze_conversation(text: str) -> list:
    """
    Analyze a conversation by splitting it into sentences and analyzing each one.
    
    This function processes multi-sentence text by first splitting it into individual 
    sentences, then analyzing each sentence for sentiment, language, and intent.
    The results are also sent to a logging service for storage.
    
    Args:
        text (str): The conversation text to analyze.
        
    Returns:
        list: A list of dictionaries, each containing a sentence and its analysis.
    """
    # Import here to avoid heavy dependency when only split_sentences is used
    from app import LLMTagger
    import requests
    tagger = LLMTagger()
    sentences = split_sentences(text)
    results = []
    for sentence in sentences:
        analysis = tagger.tag(sentence)
        result_entry = {"sentence": sentence, "analysis": analysis}
        results.append(result_entry)
        
        # Prepare log data and send to logging service (Assuming FastAPI service)
        log_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "text": sentence,
            "analysis": analysis
        }
        try:
            # Assuming the log_service FastAPI is running on port 8000
            # Use a short timeout to avoid blocking the application
            response = requests.post("http://127.0.0.1:8000/log", json=log_data, timeout=2)
            if response.status_code != 200:
                logger.warning(f"Log service returned non-200 status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            logger.warning("Could not connect to log service - logs will not be saved to MongoDB")
        except requests.exceptions.Timeout:
            logger.warning("Timeout connecting to log service - continuing without logging")
        except Exception as e:
            logger.warning(f"Error connecting to log service: {e}")
    return results
