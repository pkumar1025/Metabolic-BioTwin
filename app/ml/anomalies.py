import pandas as pd
import numpy as np

def rolling_median_mad(s: pd.Series, window: int = 14):
    med = s.rolling(window, min_periods=7).median()
    mad = s.rolling(window, min_periods=7).apply(lambda x: np.median(np.abs(x - np.median(x))), raw=True)
    z = (s - med) / (1.4826 * (mad + 1e-6))
    return z, med

def anomaly_runs(dates: pd.Series, series: pd.Series, k: float = 2.5, min_run: int = 3):
    z, med = rolling_median_mad(series)
    flags = (z > k).astype(int)
    runs = []
    start = None
    for i, v in enumerate(flags):
        if v and start is None:
            start = i
        if not v and start is not None:
            if i - start >= min_run:
                runs.append((dates.iloc[start], dates.iloc[i-1], float(series.iloc[start:i].mean()), float(med.iloc[i-1])))
            start = None
    if start is not None and len(series) - start >= min_run:
        runs.append((dates.iloc[start], dates.iloc[-1], float(series.iloc[start:].mean()), float(med.iloc[-1])))
    return runs
