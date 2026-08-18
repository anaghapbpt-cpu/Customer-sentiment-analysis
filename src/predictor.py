from typing import List, Dict, Any, Optional
import torch
import torch.nn.functional as F
from src.model import load_model_and_tokenizer

_GLOBAL_RESOURCES = None

def get_default_resources():
    global _GLOBAL_RESOURCES
    if _GLOBAL_RESOURCES is None:
        _GLOBAL_RESOURCES = load_model_and_tokenizer()
    return _GLOBAL_RESOURCES

def predict_sentiment(text: str, resources: Optional[tuple] = None) -> Dict[str, Any]:
    """
    Predict sentiment for a single review.
    Returns dictionary with sentiment (POSITIVE/NEGATIVE), confidence (percentage), and probabilities.
    """
    if not text or not text.strip():
        return {"error": "Review text cannot be empty."}

    model, tokenizer = resources if resources is not None else get_default_resources()

    inputs = tokenizer(
        text.strip(),
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True
    )

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = F.softmax(logits, dim=-1).squeeze().tolist()

    if isinstance(probs, float):
        probs = [1.0 - probs, probs]

    # Map labels: index 0 -> NEGATIVE, index 1 -> POSITIVE (Standard SST-2 / binary classification)
    # Check id2label if available
    id2label = getattr(model.config, "id2label", {0: "NEGATIVE", 1: "POSITIVE"})
    pred_idx = int(torch.argmax(logits, dim=-1).item())
    pred_label = id2label.get(pred_idx, "POSITIVE" if pred_idx == 1 else "NEGATIVE").upper()
    confidence = probs[pred_idx] * 100.0

    return {
        "text": text,
        "sentiment": pred_label,
        "confidence": round(confidence, 2),
        "probabilities": {
            "negative": round(probs[0] * 100.0, 2),
            "positive": round(probs[1] * 100.0, 2)
        }
    }

def predict_sentiment_batch(texts: List[str], batch_size: int = 32, resources: Optional[tuple] = None) -> List[Dict[str, Any]]:
    """
    Predict sentiment for a batch of reviews efficiently.
    """
    if not texts:
        return []

    model, tokenizer = resources if resources is not None else get_default_resources()
    id2label = getattr(model.config, "id2label", {0: "NEGATIVE", 1: "POSITIVE"})
    results = []

    for i in range(0, len(texts), batch_size):
        batch_texts = [str(t).strip() for t in texts[i:i + batch_size]]
        # Handle empty elements
        cleaned_batch = [t if t else "N/A" for t in batch_texts]

        inputs = tokenizer(
            cleaned_batch,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probs = F.softmax(logits, dim=-1)
            pred_indices = torch.argmax(logits, dim=-1).tolist()

        for j, pred_idx in enumerate(pred_indices):
            label = id2label.get(pred_idx, "POSITIVE" if pred_idx == 1 else "NEGATIVE").upper()
            row_probs = probs[j].tolist()
            conf = row_probs[pred_idx] * 100.0
            results.append({
                "sentiment": label,
                "confidence": round(conf, 2),
                "probabilities": {
                    "negative": round(row_probs[0] * 100.0, 2),
                    "positive": round(row_probs[1] * 100.0, 2)
                }
            })

    return results
