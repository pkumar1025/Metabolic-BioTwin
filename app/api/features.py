import pandas as pd
from app.api.ingest import session_data

def load_daily(session_id: str) -> pd.DataFrame:
    return session_data[session_id]["daily"]

def load_meals(session_id: str) -> pd.DataFrame:
    return session_data[session_id]["meals"]
