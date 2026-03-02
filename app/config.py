import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DEMO_DIR = DATA_DIR / "demo"
STORE_DIR = DATA_DIR / "store"
STORE_DIR.mkdir(parents=True, exist_ok=True)
DEMO_DIR.mkdir(parents=True, exist_ok=True)

# Business / data thresholds (single source; used by ingest, insights, predictive, UI)
LOW_SLEEP_THRESHOLD = 6.0  # hours
MIN_SAMPLES = 30            # for correlations
MIN_DAILY_DAYS = 14         # minimum days for predictions, forecast, and trend confidence
MIN_MEALS_FOR_PREDICTION = 20  # minimum meals with meal_auc for glucose prediction model
CONFIDENCE_DAYS_HIGH = 30   # data_span_days >= this -> "high" model confidence
CONFIDENCE_DAYS_MODERATE = 14  # data_span_days >= this -> "moderate", else "low"

# Columns required for full AI insights (causal + meal glucose); single source for ingest + insights
INSIGHTS_MEAL_COLS = frozenset({"date", "meal_auc", "meal_peak", "late_meal", "post_meal_walk10"})

# Demo data: allowed filenames for download / validation (single source for ingest)
ALLOWED_DEMO_FILES = frozenset({"meals.csv", "sleep.csv", "activity.csv", "vitals.csv"})

# API base URL for server-side dashboard requests (e.g. same process); override via env in production
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000").strip()

# Optional: set OPENAI_API_KEY in env to enable LLM-generated intervention text
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
