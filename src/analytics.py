import re
from typing import List, Tuple, Dict, Any
import pandas as pd

# Thematic keyword dictionaries for negative customer feedback categorization
COMPLAINT_THEMES = {
    "Shipping & Delivery Delays": ["shipping", "delivery", "late", "delayed", "delay", "arrived late", "tracking", "lost package", "wait"],
    "Product Damage & Packaging": ["broken", "damaged", "packaging", "torn", "cracked", "scratched", "destroyed", "box was", "dent", "smashed"],
    "Battery & Power Issues": ["battery", "charge", "charging", "dies", "died", "power", "drain", "drains", "dead battery", "battery life"],
    "Customer Support & Refunds": ["customer service", "support", "refund", "return", "unhelpful", "no response", "agent", "ticket", "rude", "replied"],
    "Quality & Durability": ["cheap", "quality", "broke", "stopped working", "poor quality", "useless", "flimsy", "terrible", "faulty", "waste"],
    "Pricing & Value Concerns": ["expensive", "overpriced", "not worth", "waste of money", "rip off", "scam", "pricey", "hidden fees"],
    "Software & Usability Bugs": ["crash", "crashes", "bug", "glitch", "freeze", "freezing", "login", "update", "confusing", "error", "setup"]
}

def clean_review_text(text: Any) -> str:
    """Cleans and standardizes raw review text."""
    if text is None or pd.isna(text):
        return ""
    text_str = str(text).strip()
    # Remove excessive whitespace and control characters
    text_str = re.sub(r"\s+", " ", text_str)
    return text_str

def calculate_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculates sentiment distribution statistics and averages."""
    total = len(df)
    if total == 0:
        return {
            "total_reviews": 0,
            "positive_reviews": 0,
            "negative_reviews": 0,
            "positive_percentage": 0.0,
            "negative_percentage": 0.0,
            "average_confidence": 0.0,
            "confidence_distribution": []
        }

    sentiment_col = df["sentiment"]
    if isinstance(sentiment_col, pd.DataFrame):
        sentiment_col = sentiment_col.iloc[:, 0]

    sentiments = sentiment_col.astype(str).str.upper()
    positive_count = int((sentiments == "POSITIVE").sum())
    negative_count = int((sentiments == "NEGATIVE").sum())

    pos_pct = round((positive_count / total) * 100.0, 2)
    neg_pct = round((negative_count / total) * 100.0, 2)

    conf_series = df["confidence"] if "confidence" in df.columns else pd.Series([], dtype=float)
    if isinstance(conf_series, pd.DataFrame):
        conf_series = conf_series.iloc[:, 0]

    avg_conf = round(float(conf_series.mean()), 2) if not conf_series.empty else 0.0

    # Build confidence bins
    bins = [0, 50, 60, 70, 80, 90, 100]
    labels = ["<50%", "50-60%", "60-70%", "70-80%", "80-90%", "90-100%"]
    binned = pd.cut(conf_series, bins=bins, labels=labels, right=True)
    conf_dist = binned.value_counts().reindex(labels, fill_value=0).to_dict()


    return {
        "total_reviews": total,
        "positive_reviews": positive_count,
        "negative_reviews": negative_count,
        "positive_percentage": pos_pct,
        "negative_percentage": neg_pct,
        "average_confidence": avg_conf,
        "confidence_distribution": conf_dist
    }

def detect_negative_themes(negative_reviews: List[str]) -> List[Tuple[str, int]]:
    """Detects recurring themes in negative reviews based on domain keywords."""
    if not negative_reviews:
        return []

    theme_counts: Dict[str, int] = {theme: 0 for theme in COMPLAINT_THEMES}

    for review in negative_reviews:
        review_lower = str(review).lower()
        for theme, keywords in COMPLAINT_THEMES.items():
            if any(re.search(r"\b" + re.escape(kw) + r"\b", review_lower) for kw in keywords):
                theme_counts[theme] += 1

    # Filter themes with > 0 mentions and sort by frequency descending
    sorted_themes = sorted(
        [(theme, count) for theme, count in theme_counts.items() if count > 0],
        key=lambda x: x[1],
        reverse=True
    )
    return sorted_themes

def extract_sample_negative_reviews(df: pd.DataFrame, max_samples: int = 5) -> List[str]:
    """Extracts up to max_samples representative negative reviews."""
    if df.empty or "sentiment" not in df.columns or "review" not in df.columns:
        return []
    
    neg_mask = df["sentiment"].astype(str).str.upper() == "NEGATIVE"
    neg_df = df[neg_mask]
    if neg_df.empty:
        return []
    
    review_col = neg_df["review"]
    # If duplicate column names exist, review_col can be a DataFrame
    if isinstance(review_col, pd.DataFrame):
        review_col = review_col.iloc[:, 0]

    raw_samples = review_col.dropna().astype(str).tolist()
    
    seen = set()
    unique_samples = []
    for s in raw_samples:
        clean_s = s.strip()
        if clean_s and clean_s not in seen:
            seen.add(clean_s)
            unique_samples.append(clean_s)
        if len(unique_samples) >= max_samples:
            break
    return unique_samples

