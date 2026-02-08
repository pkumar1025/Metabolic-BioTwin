import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DEMO_DIR = DATA_DIR / "demo"
STORE_DIR = DATA_DIR / "store"
STORE_DIR.mkdir(parents=True, exist_ok=True)
DEMO_DIR.mkdir(parents=True, exist_ok=True)

LOW_SLEEP_THRESHOLD = 6.0  # hours
MIN_SAMPLES = 30           # for correlations

# Optional: set GEMINI_API_KEY in env to enable LLM-generated intervention text
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
