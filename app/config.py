from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DEMO_DIR = DATA_DIR / "demo"
STORE_DIR = DATA_DIR / "store"
STORE_DIR.mkdir(parents=True, exist_ok=True)
DEMO_DIR.mkdir(parents=True, exist_ok=True)

LOW_SLEEP_THRESHOLD = 6.0  # hours
MIN_SAMPLES = 30           # for correlations
