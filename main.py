import io
import os
from typing import List, Optional
import pandas as pd
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from src.model import load_model_and_tokenizer, ModelLoadError
from src.predictor import predict_sentiment, predict_sentiment_batch
from src.analytics import clean_review_text, calculate_summary, detect_negative_themes, extract_sample_negative_reviews
from src.agent import generate_business_insights

APP_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(APP_DIR, "static")

app = FastAPI(
    title="Customer Sentiment & Business Insights API",
    description="FastAPI backend for high-performance customer sentiment classification and business intelligence.",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize model on module load with lazy-safe getter
model_resources = None
model_load_status = {"status": "loading", "device": "CPU", "error": None}

def get_or_load_model():
    global model_resources, model_load_status
    if model_resources is None:
        try:
            model_resources = load_model_and_tokenizer()
            model_load_status = {"status": "ready", "device": "CPU", "error": None}
        except Exception as exc:
            model_load_status = {"status": "error", "device": "CPU", "error": str(exc)}
            raise exc
    return model_resources

# Preload model on startup
try:
    get_or_load_model()
except Exception as e:
    pass


PREFERRED_COLUMNS = ["review", "text", "review_text", "comment", "feedback"]
MAX_UPLOAD_ROWS = 50000
BATCH_SIZE = 32

MODEL_METRICS = {
    "Accuracy": 93.88,
    "Precision": 94.20,
    "Recall": 93.52,
    "F1 Score": 93.86,
    "Training Set Size": "20,000 reviews",
    "Test Set Size": "5,000 reviews",
    "Epochs": 2,
    "Architecture": "DistilBERT (Transformer sequence classifier)"
}

class SingleReviewRequest(BaseModel):
    review: str

class InsightsRequest(BaseModel):
    summary: dict
    themes: list
    samples: list

@app.get("/api/health")
def health_check():
    return {"status": "ok", "model_status": model_load_status}

@app.get("/api/model-info")
def get_model_info():
    return {
        "model_status": model_load_status,
        "metrics": MODEL_METRICS,
        "supported_columns": PREFERRED_COLUMNS,
        "max_rows": MAX_UPLOAD_ROWS,
        "batch_size": BATCH_SIZE
    }

@app.post("/api/predict/single")
def api_predict_single(payload: SingleReviewRequest):
    if not payload.review or not payload.review.strip():
        raise HTTPException(status_code=400, detail="Review text cannot be empty.")
    
    try:
        resources = get_or_load_model()
        result = predict_sentiment(payload.review, resources=resources)
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(exc)}")


@app.post("/api/predict/batch")
async def api_predict_batch(file: UploadFile = File(...), column: Optional[str] = Form(None)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files (.csv) are supported.")

    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="Uploaded file could not be parsed as a valid CSV.")

    if df.empty:
        raise HTTPException(status_code=400, detail="The uploaded CSV file is empty.")

    if len(df) > MAX_UPLOAD_ROWS:
        raise HTTPException(status_code=400, detail=f"File exceeds maximum allowed rows ({MAX_UPLOAD_ROWS:,}).")

    # Determine column
    selected_col = None
    if column and column in df.columns:
        selected_col = column
    else:
        for pref in PREFERRED_COLUMNS:
            if pref in df.columns:
                selected_col = pref
                break
        if not selected_col and len(df.columns) > 0:
            selected_col = df.columns[0]

    if not selected_col:
        raise HTTPException(status_code=400, detail="No suitable review column could be found in the CSV.")

    # Prepare review text
    working_df = df.copy()
    working_df["cleaned_review"] = working_df[selected_col].apply(clean_review_text)
    working_df = working_df[working_df["cleaned_review"] != ""].reset_index(drop=True)

    if working_df.empty:
        raise HTTPException(status_code=400, detail="Selected column contains no usable review text after cleaning.")

    try:
        resources = get_or_load_model()
        predictions = predict_sentiment_batch(working_df["cleaned_review"].tolist(), batch_size=BATCH_SIZE, resources=resources)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(exc)}")


    pred_df = pd.DataFrame(predictions)
    working_df["sentiment"] = pred_df["sentiment"]
    working_df["confidence"] = pred_df["confidence"]

    # Calculate analytics
    summary = calculate_summary(working_df.rename(columns={"cleaned_review": "review"}))
    negative_reviews = working_df[working_df["sentiment"] == "NEGATIVE"]["cleaned_review"].tolist()
    themes = detect_negative_themes(negative_reviews)
    sample_negatives = extract_sample_negative_reviews(working_df.rename(columns={"cleaned_review": "review"}))
    insights = generate_business_insights(summary, themes, sample_negatives)

    # Return top 100 preview rows for responsive frontend rendering
    preview_rows = working_df[[selected_col, "sentiment", "confidence"]].head(100).to_dict(orient="records")

    return {
        "selected_column": selected_col,
        "available_columns": list(df.columns),
        "total_analyzed": len(working_df),
        "summary": summary,
        "themes": themes,
        "sample_negatives": sample_negatives,
        "insights": insights,
        "preview_rows": preview_rows,
        "all_rows": working_df[[selected_col, "sentiment", "confidence"]].to_dict(orient="records")
    }

@app.post("/api/insights")
def api_generate_insights(payload: InsightsRequest):
    insights = generate_business_insights(payload.summary, payload.themes, payload.samples)
    return {"insights": insights}

@app.get("/api/download-sample")
def download_sample_csv():
    sample_path = os.path.join(APP_DIR, "sample_reviews.csv")
    if os.path.exists(sample_path):
        return FileResponse(sample_path, media_type="text/csv", filename="sample_reviews.csv")
    raise HTTPException(status_code=404, detail="Sample CSV not found.")

# Mount static folder and serve index.html at root
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_root():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Customer Sentiment API is running. Build frontend in /static/index.html"}
