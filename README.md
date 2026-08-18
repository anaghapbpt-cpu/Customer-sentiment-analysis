<<<<<<< HEAD
# Customer-sentiment-analysis
=======
# AI Customer Sentiment & Business Insights Platform

A high-performance **FastAPI** web application with a modern **HTML5, CSS3, and JavaScript** dashboard. It uses a fine-tuned **DistilBERT** transformer model to classify customer sentiment, detect operational complaint themes, analyze batch CSV datasets, and synthesize actionable business intelligence.

---

## Key Features

- **Single Review Sentiment Prediction**: Real-time neural inference displaying predicted sentiment (Positive/Negative), confidence percentage, and class probability distributions.
- **Batch CSV Analysis**: Drag-and-drop CSV dataset uploader supporting up to 50,000 reviews with automatic review column detection.
- **Dynamic Data Visualizations**: Interactive sentiment doughnut distribution and confidence histogram powered by Chart.js.
- **Complaint Theme Detection**: Automated keyword clustering for top friction categories (Shipping, Packaging, Battery/Power, Quality, Support, Pricing).
- **Representative Negative Voice-of-Customer**: Direct sampling of critical negative feedback.
- **AI Business Insights Synthesis**: Executive summaries analyzing situation health, operational urgency, root-cause pain points, and department action recommendations.
- **CSV Data Export**: Instant download of classified datasets with model predictions and confidence scores.
- **Model Benchmark Dashboard**: Visualization of fine-tuned Colab metrics (93.88% Accuracy, 94.20% Precision, 93.52% Recall, 93.86% F1).
- **Interactive REST API**: Built-in Swagger/OpenAPI documentation at `/docs`.

---

## Architecture & Tech Stack

```text
customer-sentiment-ai/
├── src/
│   ├── __init__.py
│   ├── model.py         # DistilBERT model loader with local/HuggingFace fallback
│   ├── predictor.py     # Single & batch sequence classification inference
│   ├── analytics.py     # Statistics, confidence distribution, theme extraction
│   └── agent.py         # Rule-based business intelligence generator
├── static/
│   ├── index.html       # Single-page dashboard UI
│   ├── css/
│   │   └── styles.css   # Dark-mode glassmorphic design system
│   └── js/
│       └── app.js       # Asynchronous client, Chart.js graphs, file handling
├── main.py              # FastAPI server & API endpoints
├── sample_reviews.csv   # Demo reviews dataset
├── requirements.txt     # Python dependencies
└── README.md
```

### Backend
- **FastAPI** & **Uvicorn**
- **PyTorch** & **Hugging Face Transformers**
- **Pandas** & **NumPy**

### Frontend
- **HTML5** & **Vanilla CSS3** (Glassmorphism, CSS Custom Properties, Responsive Grid)
- **Vanilla JavaScript** (ES6+, Fetch API, FileReader API)
- **Chart.js** & **FontAwesome 6**

---

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. (Optional) Place Fine-Tuned Weights
If you trained custom weights in Google Colab, copy your model artifacts into `models/sentiment_model/`:
- `config.json`
- `model.safetensors`
- `tokenizer.json`
- `tokenizer_config.json`

*(Note: If no local weights are placed, the app automatically connects to the pre-trained SST-2 DistilBERT sentiment model with zero downtime.)*

---

## Running the Application

Start the FastAPI server:

```bash
uvicorn main:app --reload --port 8000
```

Open your browser and navigate to:
- **Web App**: [http://localhost:8000](http://localhost:8000)
- **Interactive API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/predict/single` | Classify a single review text string |
| `POST` | `/api/predict/batch` | Upload CSV and receive sentiment analysis, themes, & insights |
| `GET` | `/api/model-info` | Retrieve model status, benchmarks, and configuration |
| `GET` | `/api/download-sample` | Download the bundled `sample_reviews.csv` file |
| `GET` | `/api/health` | Service health status |
>>>>>>> 3c61e4d (feat: replace Streamlit with FastAPI + HTML/CSS/JS frontend)
