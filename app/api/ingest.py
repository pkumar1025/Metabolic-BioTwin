from fastapi import APIRouter, UploadFile, File, Form
import pandas as pd
import uuid
from app.config import STORE_DIR, DEMO_DIR

router = APIRouter()

# In-memory storage for demo sessions (no file persistence needed)
session_data = {}

@router.post("/ingest")
async def ingest(
    use_demo: bool = Form(False),
    meals_csv: UploadFile | None = File(None),
    sleep_csv: UploadFile | None = File(None),
    activity_csv: UploadFile | None = File(None),
    vitals_csv: UploadFile | None = File(None),
):
    sid = str(uuid.uuid4())

    def _read(f: UploadFile | None, demo_name: str) -> pd.DataFrame:
        if f:
            return pd.read_csv(f.file)
        return pd.read_csv(DEMO_DIR / demo_name)

    if use_demo:
        meals = pd.read_csv(DEMO_DIR / "meals.csv")
        sleep = pd.read_csv(DEMO_DIR / "sleep.csv")
        activity = pd.read_csv(DEMO_DIR / "activity.csv")
        vitals = pd.read_csv(DEMO_DIR / "vitals.csv")
    else:
        meals = _read(meals_csv, "meals.csv")
        sleep = _read(sleep_csv, "sleep.csv")
        activity = _read(activity_csv, "activity.csv")
        vitals = _read(vitals_csv, "vitals.csv")

    # Normalize dates
    for df in (meals, sleep, activity, vitals):
        df["date"] = pd.to_datetime(df["date"]).dt.date

    # Precompute daily joined table for timeline endpoints
    daily = (sleep.merge(activity, on="date", how="outer")
                  .merge(vitals, on="date", how="outer")
                  .sort_values("date"))
    # Interpolate numeric columns
    num_cols = [c for c in daily.columns if c != "date"]
    if num_cols:
        daily[num_cols] = daily[num_cols].interpolate(limit_direction="both")
    
    # Store in memory instead of files (no persistence needed for demo)
    session_data[sid] = {
        "meals": meals,
        "sleep": sleep,
        "activity": activity,
        "vitals": vitals,
        "daily": daily
    }

    return {"session_id": sid, "rows_daily": int(len(daily)), "rows_meals": int(len(meals))}
