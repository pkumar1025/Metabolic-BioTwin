from fastapi import APIRouter
import pandas as pd
from app.api.features import load_daily, load_meals
from app.ml.glycemic import add_meal_features
from app.ml.causal import doubly_robust_ate
from app.ml.anomalies import anomaly_runs
from app.ml.correlations import corr_with_p
from app.config import LOW_SLEEP_THRESHOLD, MIN_SAMPLES

router = APIRouter()

@router.get("/timeline")
def timeline(session_id: str):
    df = load_daily(session_id)
    return {
        "dates": pd.to_datetime(df["date"]).astype(str).tolist(),
        "sleep_hours": df.get("sleep_hours", pd.Series()).fillna(0).tolist(),
        "hrv": df.get("hrv", pd.Series()).fillna(0).tolist(),
        "rhr": df.get("rhr", pd.Series()).fillna(0).tolist(),
        "fg_fast_mgdl": df.get("fg_fast_mgdl", pd.Series()).fillna(0).tolist(),
    }

@router.get("/meals")
def meals(session_id: str):
    m = add_meal_features(load_meals(session_id)).sort_values(["date","time"])
    cols = ["date","time","carbs_g","protein_g","fat_g","fiber_g","carbs_pct",
            "late_meal","post_meal_walk10","meal_auc","meal_peak","ttpeak_min"]
    return {"meals": m[cols].astype(str).to_dict(orient="records")}

@router.get("/insights")
def insights(session_id: str):
    daily = load_daily(session_id)
    meals = add_meal_features(load_meals(session_id))

    # Map previous-night sleep to meals (next day)
    d = daily[["date","sleep_hours","hrv","rhr"]].copy()
    d["date"] = pd.to_datetime(d["date"])
    meals["date"] = pd.to_datetime(meals["date"])
    d["sleep_prev"] = d["sleep_hours"].shift(1)
    d_prev = d[["date","sleep_prev"]]
    m = meals.merge(d_prev, on="date", how="left")
    m["sleep_low"] = (m["sleep_prev"] < LOW_SLEEP_THRESHOLD).astype(int)

    cards = []

    # 1) DR uplift: short sleep -> next-day meal AUC
    confs = ["carbs_pct","fiber_g","late_meal","post_meal_walk10"]
    res = doubly_robust_ate(m, "sleep_low", "meal_auc", confs)
    if res:
        base = max(1e-6, m["meal_auc"].mean())
        cards.append({
            "id":"sleep_auc",
            "type":"causal_uplift",
            "title":"Short sleep → higher post‑meal glucose tomorrow",
            "driver":f"sleep_prev < {LOW_SLEEP_THRESHOLD}h",
            "target":"meal AUC (next day)",
            "effect_pct": round(res["ate"]/base, 3),
            "ci": [round(res["ci"][0]/base,3), round(res["ci"][1]/base,3)],
            "n": res["n"],
            "confidence": "high" if res["n"]>=100 else "moderate" if res["n"]>=50 else "low",
            "counterfactual": {"scenario":"set sleep=7.5h", "delta_pct": -0.10},
            "suggested_experiment": {
                "duration_days":5,
                "intervention":"Target 7.5h sleep; avoid late dinner; 10‑min post‑dinner walk",
                "metrics":["dinner meal AUC","meal_peak"],
                "success":"AUC −10% vs baseline (p<0.1)"
            }
        })

    # 2) DR uplift: 10‑min walk -> lower AUC
    res2 = doubly_robust_ate(m, "post_meal_walk10", "meal_auc", ["carbs_pct","fiber_g","late_meal","sleep_low"])
    if res2:
        base = max(1e-6, m["meal_auc"].mean())
        cards.append({
            "id":"walk_auc",
            "type":"causal_uplift",
            "title":"10‑min post‑meal walk reduces AUC",
            "driver":"post_meal_walk10",
            "target":"meal AUC",
            "effect_pct": round(res2["ate"]/base, 3),
            "ci": [round(res2["ci"][0]/base,3), round(res2["ci"][1]/base,3)],
            "n": res2["n"],
            "confidence": "moderate" if res2["n"]>=50 else "low",
        })

    # 3) Correlation: late meals -> higher peak
    r, p, n = corr_with_p(m["late_meal"].astype(float), m["meal_peak"], method="spearman")
    if r is not None and n >= MIN_SAMPLES:
        cards.append({
            "id":"late_peak",
            "type":"correlation",
            "title":"Late dinners are linked to higher glucose peaks",
            "driver":"late_meal",
            "target":"meal_peak",
            "r": round(r,2),
            "p": round(p,3),
            "n": n,
            "note":"Association only; see walk card for an actionable lever."
        })

    # 4) Anomaly: fasting glucose multi‑day run
    runs = anomaly_runs(pd.to_datetime(daily["date"]), daily["fg_fast_mgdl"])
    if runs:
        start, end, curr, base = runs[-1]
        cards.append({
            "id":"fg_anomaly",
            "type":"anomaly",
            "title":"Fasting glucose above baseline for multiple days",
            "baseline": round(base,1),
            "current": round(curr,1),
            "run_days": (pd.to_datetime(end)-pd.to_datetime(start)).days+1,
            "context":"historically co‑occurs with short sleep & lower HRV",
            "suggested_experiment":{
                "duration_days":5,
                "intervention":"Earlier dinner; 10‑min post‑dinner walk; 7.5h sleep target",
                "metrics":["fg_fast_mgdl","sleep_hours","hrv"],
                "success":"fg_fast −5 mg/dL vs baseline"
            }
        })

    return {"cards": cards}
