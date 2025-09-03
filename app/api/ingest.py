from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import pandas as pd
import uuid
import io
import base64
from typing import List, Dict
from app.config import STORE_DIR, DEMO_DIR
from app.api.data_processor import HealthDataProcessor

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

@router.post("/ingest/upload")
async def ingest_uploaded_files(files_data: List[Dict]):
    """
    Process uploaded files with flexible schema handling
    """
    try:
        sid = str(uuid.uuid4())
        processor = HealthDataProcessor()
        
        # Process uploaded files
        processed_data, quality_report = processor.process_uploaded_files(files_data)
        
        if not processed_data:
            raise HTTPException(status_code=400, detail="No valid data could be processed")
        
        # Create daily summary
        daily = processor.create_daily_summary()
        
        # Store processed data
        session_data[sid] = {
            **processed_data,
            "daily": daily,
            "quality_report": quality_report
        }
        
        return {
            "session_id": sid,
            "rows_daily": int(len(daily)),
            "data_types_processed": list(processed_data.keys()),
            "quality_report": quality_report,
            "validation_errors": processor.validation_errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing uploaded data: {str(e)}")

@router.get("/ingest/validate")
async def validate_file_format(file_content: str):
    """
    Validate file format before processing
    """
    try:
        # Decode base64 content
        decoded = base64.b64decode(file_content)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        
        # Basic validation
        validation_result = {
            "valid": True,
            "rows": len(df),
            "columns": list(df.columns),
            "data_types": df.dtypes.astype(str).to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "suggested_data_type": "unknown"
        }
        
        # Suggest data type
        processor = HealthDataProcessor()
        validation_result["suggested_data_type"] = processor._detect_data_type(df.columns)
        
        return validation_result
        
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }
