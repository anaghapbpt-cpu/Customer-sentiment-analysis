import os
from typing import Tuple, Any
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class ModelLoadError(Exception):
    """Custom exception raised when model loading fails."""
    pass

DEFAULT_MODEL_NAME = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
LOCAL_MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "sentiment_model")

def load_model_and_tokenizer(model_path: str = None) -> Tuple[Any, Any]:
    """
    Loads tokenizer and model.
    Checks local models/sentiment_model directory first;
    if not present, falls back gracefully to pre-trained DistilBERT sentiment model.
    """
    target_path = model_path or LOCAL_MODEL_DIR
    
    if os.path.exists(target_path) and any(os.scandir(target_path)):
        try:
            tokenizer = AutoTokenizer.from_pretrained(target_path)
            model = AutoModelForSequenceClassification.from_pretrained(target_path)
            model.eval()
            return model, tokenizer
        except Exception as e:
            # Fall back if local model has corrupt weights
            pass

    try:
        tokenizer = AutoTokenizer.from_pretrained(DEFAULT_MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(DEFAULT_MODEL_NAME)
        model.eval()
        return model, tokenizer
    except Exception as exc:
        raise ModelLoadError(f"Failed to load model from both '{target_path}' and '{DEFAULT_MODEL_NAME}': {str(exc)}")
