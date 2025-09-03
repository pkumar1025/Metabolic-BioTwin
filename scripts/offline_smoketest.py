# Quick offline smoke test (no server). Generates demo data and prints sample insights.
import json, pandas as pd, numpy as np
from pathlib import Path
from generate_synthetic import DEMO  # ensures DEMO path exists
from app.api.ingest import ingest
from types import SimpleNamespace

# Mock UploadFile-less call
import asyncio

async def go():
    res = await ingest(use_demo=True, meals_csv=None, sleep_csv=None, activity_csv=None, vitals_csv=None)
    print("Ingest:", res)
    sid = res["session_id"]

    # Call insights via FastAPI router function directly
    from app.api.insights import insights
    cards = insights(sid)["cards"]
    print("\nSample insight cards:")
    print(json.dumps(cards[:3], indent=2))

if __name__ == "__main__":
    asyncio.run(go())
