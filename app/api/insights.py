from fastapi import APIRouter
import pandas as pd
from app.api.features import load_daily, load_meals
from app.ml.glycemic import add_meal_features
from app.ml.causal import doubly_robust_ate
from app.ml.anomalies import anomaly_runs
from app.ml.correlations import corr_with_p, discover_hidden_correlations, find_lag_correlations
from app.ml.predictive import predict_glucose_response, predict_sleep_impact, generate_health_forecast
from app.ml.health_score import calculate_metabolic_health_score, generate_personalized_recommendations
from app.ml.llm_insights import generate_intervention_text
from app.config import LOW_SLEEP_THRESHOLD, MIN_SAMPLES

router = APIRouter()

@router.get("/timeline")
def timeline(session_id: str):
    try:
        df = load_daily(session_id)
        return {
            "dates": pd.to_datetime(df["date"]).astype(str).tolist(),
            "sleep_hours": df.get("sleep_hours", pd.Series()).fillna(0).tolist(),
            "hrv": df.get("hrv", pd.Series()).fillna(0).tolist(),
            "rhr": df.get("rhr", pd.Series()).fillna(0).tolist(),
            "fg_fast_mgdl": df.get("fg_fast_mgdl", pd.Series()).fillna(0).tolist(),
        }
    except KeyError:
        # Session data not found, return empty data
        return {
            "dates": [],
            "sleep_hours": [],
            "hrv": [],
            "rhr": [],
            "fg_fast_mgdl": [],
        }

@router.get("/meals")
def meals(session_id: str):
    try:
        m = add_meal_features(load_meals(session_id))
        sort_cols = [c for c in ["date", "time"] if c in m.columns]
        if sort_cols:
            m = m.sort_values(sort_cols)
        base_cols = ["date", "time", "carbs_g", "protein_g", "fat_g", "fiber_g", "carbs_pct"]
        optional_cols = ["late_meal", "post_meal_walk10", "meal_auc", "meal_peak", "ttpeak_min"]
        cols = [c for c in base_cols if c in m.columns] + [c for c in optional_cols if c in m.columns]
        if not cols:
            return {"meals": []}
        return {"meals": m[cols].astype(str).to_dict(orient="records")}
    except KeyError:
        return {"meals": []}

# Columns required for causal/correlation meal-based insights; missing = alert user, no placeholders
INSIGHTS_MEAL_COLS = {"date", "meal_auc", "meal_peak", "late_meal", "post_meal_walk10"}
INSIGHTS_DAILY_COLS = {"date", "sleep_hours", "hrv", "rhr", "fg_fast_mgdl"}


@router.get("/insights")
def insights(session_id: str):
    try:
        daily = load_daily(session_id)
        meals = add_meal_features(load_meals(session_id))
    except KeyError:
        return {
            "cards": [],
            "data_quality": {
                "total_data_points": 0,
                "data_completeness": {"sleep_data": 0, "glucose_data": 0, "meal_data": 0, "activity_data": 0},
                "data_span_days": 0,
                "processing_status": "no_data"
            },
            "ai_metrics": {"correlations_discovered": 0, "causal_effects_found": 0, "anomalies_detected": 0, "model_confidence": "no_data"},
            "insufficient_data": True,
            "insufficient_data_message": "No session data. Load demo data or upload your files first.",
        }

    # Data quality (defensive: only use columns that exist)
    def _pct_notna(df, col, default=0):
        if col not in df.columns or len(df) == 0:
            return default
        return float((df[col].notna().sum() / len(df)) * 100)

    data_quality = {
        "total_data_points": len(daily) + len(meals),
        "data_completeness": {
            "sleep_data": _pct_notna(daily, "sleep_hours"),
            "glucose_data": _pct_notna(daily, "fg_fast_mgdl"),
            "meal_data": _pct_notna(meals, "carbs_g") if "carbs_g" in meals.columns else 0,
            "activity_data": _pct_notna(daily, "rhr"),
        },
        "data_span_days": int((pd.to_datetime(daily["date"]).max() - pd.to_datetime(daily["date"]).min()).days) + 1 if "date" in daily.columns and len(daily) > 0 else 0,
        "processing_status": "completed",
    }

    cards = []
    has_meal_cols = INSIGHTS_MEAL_COLS.issubset(meals.columns)
    has_daily_cols = INSIGHTS_DAILY_COLS.issubset(daily.columns)

    if not has_meal_cols:
        missing = sorted(INSIGHTS_MEAL_COLS - set(meals.columns))
        cards.append({
            "id": "data_requirement",
            "type": "data_requirement",
            "title": "More data needed for AI insights",
            "message": "Meals are missing required columns: " + ", ".join(missing) + ". Upload a meals file with glucose metrics (e.g. meal_auc, meal_peak from CGM) or use demo data to see causal insights and predictions.",
        })

    if not has_meal_cols or not has_daily_cols:
        # Still run anomaly if we have daily glucose
        if "date" in daily.columns and "fg_fast_mgdl" in daily.columns:
            try:
                runs = anomaly_runs(pd.to_datetime(daily["date"]), daily["fg_fast_mgdl"])
                if runs:
                    start, end, curr, base = runs[-1]
                    target_drop = max(3, round(curr - base))
                    base_r, curr_r = round(base, 1), round(curr, 1)
                    run_days = (pd.to_datetime(end) - pd.to_datetime(start)).days + 1
                    fallback_i = f"Aim for fg_fast −{target_drop} mg/dL vs baseline ({base_r}→{curr_r} over {run_days} days). Track fg_fast_mgdl, sleep_hours, hrv to see what helps."
                    fallback_s = f"fg_fast −{target_drop} mg/dL vs baseline (from your data)"
                    llm_out = generate_intervention_text({
                        "card_type": "anomaly",
                        "baseline_mgdl": base_r,
                        "current_mgdl": curr_r,
                        "run_days": run_days,
                        "target_drop_mgdl": target_drop,
                        "other_levers": [],
                    })
                    cards.append({
                        "id": "fg_anomaly",
                        "type": "anomaly",
                        "title": "Fasting glucose above baseline for multiple days",
                        "baseline": base_r,
                        "current": curr_r,
                        "run_days": run_days,
                        "context": "Historically co-occurs with short sleep & lower HRV",
                        "suggested_experiment": {
                            "duration_days": 5,
                            "intervention": llm_out["intervention"] if llm_out else fallback_i,
                            "metrics": ["fg_fast_mgdl", "sleep_hours", "hrv"],
                            "success": llm_out["success"] if llm_out else fallback_s,
                        },
                    })
            except Exception:
                pass
        return {
            "cards": cards,
            "data_quality": data_quality,
            "ai_metrics": {
                "correlations_discovered": 0,
                "causal_effects_found": 0,
                "anomalies_detected": len([c for c in cards if c.get("type") == "anomaly"]),
                "model_confidence": "low",
            },
            "insufficient_data": True,
            "insufficient_data_message": cards[0]["message"] if cards and cards[0].get("type") == "data_requirement" else "Daily or meal data is incomplete for full insights.",
        }

    # Map previous-night sleep to meals (next day)
    d = daily[["date", "sleep_hours", "hrv", "rhr"]].copy()
    d["date"] = pd.to_datetime(d["date"])
    meals["date"] = pd.to_datetime(meals["date"])
    d["sleep_prev"] = d["sleep_hours"].shift(1)
    d_prev = d[["date", "sleep_prev"]]
    m = meals.merge(d_prev, on="date", how="left")
    m["sleep_low"] = (m["sleep_prev"] < LOW_SLEEP_THRESHOLD).astype(int)

    # 1) DR uplift: short sleep -> next-day meal AUC
    confs = [c for c in ["carbs_pct", "fiber_g", "late_meal", "post_meal_walk10"] if c in m.columns]
    if len(confs) < 2:
        confs = ["late_meal", "post_meal_walk10"]
    res = doubly_robust_ate(m, "sleep_low", "meal_auc", confs)
    if res:
        base = max(1e-6, m["meal_auc"].mean())
        effect_pct = round(res["ate"] / base, 3)
        # Counterfactual: improving sleep (sleep_low=0) → expected AUC reduction from DR estimate
        delta_pct = -effect_pct
        confidence = "high" if res["n"] >= 100 else "moderate" if res["n"] >= 50 else "low"
        fallback_intervention = f"Target 7.5h sleep (estimated {delta_pct * 100:.0f}% lower meal AUC from your data). Avoid late dinner; add 10‑min post‑dinner walk."
        fallback_success = f"AUC {delta_pct * 100:.0f}% vs baseline (from your data)"
        llm_out = generate_intervention_text({
            "card_type": "sleep_auc",
            "driver": f"sleep_prev < {LOW_SLEEP_THRESHOLD}h",
            "target": "meal AUC (next day)",
            "effect_pct": effect_pct,
            "estimated_delta_pct": round(delta_pct * 100, 1),
            "n": res["n"],
            "confidence": confidence,
        })
        intervention = (llm_out["intervention"] if llm_out else fallback_intervention)
        success = (llm_out["success"] if llm_out else fallback_success)
        cards.append({
            "id": "sleep_auc",
            "type": "causal_uplift",
            "title": "Short sleep → higher post‑meal glucose tomorrow",
            "driver": f"sleep_prev < {LOW_SLEEP_THRESHOLD}h",
            "target": "meal AUC (next day)",
            "effect_pct": effect_pct,
            "ci": [round(res["ci"][0] / base, 3), round(res["ci"][1] / base, 3)],
            "n": res["n"],
            "confidence": confidence,
            "counterfactual": {"scenario": "set sleep=7.5h", "delta_pct": delta_pct},
            "suggested_experiment": {
                "duration_days": 5,
                "intervention": intervention,
                "metrics": ["dinner meal AUC", "meal_peak"],
                "success": success,
            },
        })

    # 2) DR uplift: 10‑min walk -> lower AUC
    res2 = doubly_robust_ate(m, "post_meal_walk10", "meal_auc", ["carbs_pct","fiber_g","late_meal","sleep_low"])
    if res2:
        base = max(1e-6, m["meal_auc"].mean())
        walk_effect_pct = round(res2["ate"] / base, 3)
        walk_delta = -walk_effect_pct
        confidence_w = "moderate" if res2["n"] >= 50 else "low"
        fallback_i = f"Add 10‑min post‑meal walk (estimated {walk_delta * 100:.0f}% lower AUC from your data, n={res2['n']} meals)."
        fallback_s = f"AUC {walk_delta * 100:.0f}% vs baseline (from your data)"
        llm_out = generate_intervention_text({
            "card_type": "walk_auc",
            "driver": "post_meal_walk10",
            "target": "meal AUC",
            "effect_pct": walk_effect_pct,
            "estimated_delta_pct": round(walk_delta * 100, 1),
            "n": res2["n"],
            "confidence": confidence_w,
        })
        cards.append({
            "id": "walk_auc",
            "type": "causal_uplift",
            "title": "10‑min post‑meal walk reduces AUC",
            "driver": "post_meal_walk10",
            "target": "meal AUC",
            "effect_pct": walk_effect_pct,
            "ci": [round(res2["ci"][0] / base, 3), round(res2["ci"][1] / base, 3)],
            "n": res2["n"],
            "confidence": confidence_w,
            "suggested_experiment": {
                "duration_days": 5,
                "intervention": llm_out["intervention"] if llm_out else fallback_i,
                "metrics": ["meal_auc", "meal_peak"],
                "success": llm_out["success"] if llm_out else fallback_s,
            },
        })

    # 3) Correlation: late meals -> higher peak
    r, p, n = corr_with_p(m["late_meal"].astype(float), m["meal_peak"], method="spearman")
    if r is not None and n >= MIN_SAMPLES:
        r_round = round(r, 2)
        fallback_i = f"Earlier dinner (late meals linked to higher glucose peaks in your data, r={r_round}, n={n})."
        fallback_s = "Lower meal_peak on days with earlier dinner (from your data)"
        llm_out = generate_intervention_text({
            "card_type": "late_peak",
            "driver": "late_meal",
            "target": "meal_peak",
            "r": r_round,
            "p": round(p, 3),
            "n": n,
        })
        cards.append({
            "id": "late_peak",
            "type": "correlation",
            "title": "Late dinners are linked to higher glucose peaks",
            "driver": "late_meal",
            "target": "meal_peak",
            "r": r_round,
            "p": round(p, 3),
            "n": n,
            "note": "Association only; see walk card for an actionable lever.",
            "suggested_experiment": {
                "duration_days": 5,
                "intervention": llm_out["intervention"] if llm_out else fallback_i,
                "metrics": ["meal_peak", "late_meal"],
                "success": llm_out["success"] if llm_out else fallback_s,
            },
        })

    # 4) Anomaly: fasting glucose multi‑day run
    runs = anomaly_runs(pd.to_datetime(daily["date"]), daily["fg_fast_mgdl"])
    if runs:
        start, end, curr, base = runs[-1]
        target_drop = max(3, round(curr - base))
        base_r, curr_r = round(base, 1), round(curr, 1)
        run_days = (pd.to_datetime(end) - pd.to_datetime(start)).days + 1
        other_levers = [
            {"name": "sleep", "estimated_delta_pct": round(-c.get("effect_pct", 0) * 100, 1)}
            for c in cards if c.get("type") == "causal_uplift" and c.get("id") == "sleep_auc"
        ] + [
            {"name": "post_meal_walk", "estimated_delta_pct": round(-c.get("effect_pct", 0) * 100, 1)}
            for c in cards if c.get("type") == "causal_uplift" and c.get("id") == "walk_auc"
        ]
        fallback_i = f"Aim for fg_fast −{target_drop} mg/dL vs your baseline ({base_r}→{curr_r} over {run_days} days). Your data suggests improving sleep and post‑dinner walk; track metrics below."
        fallback_s = f"fg_fast −{target_drop} mg/dL vs baseline (from your data)"
        llm_out = generate_intervention_text({
            "card_type": "anomaly",
            "baseline_mgdl": base_r,
            "current_mgdl": curr_r,
            "run_days": run_days,
            "target_drop_mgdl": target_drop,
            "other_levers": other_levers,
        })
        cards.append({
            "id": "fg_anomaly",
            "type": "anomaly",
            "title": "Fasting glucose above baseline for multiple days",
            "baseline": base_r,
            "current": curr_r,
            "run_days": run_days,
            "context": "historically co‑occurs with short sleep & lower HRV",
            "suggested_experiment": {
                "duration_days": 5,
                "intervention": llm_out["intervention"] if llm_out else fallback_i,
                "metrics": ["fg_fast_mgdl", "sleep_hours", "hrv"],
                "success": llm_out["success"] if llm_out else fallback_s,
            },
        })

    return {
        "cards": cards,
        "data_quality": data_quality,
        "ai_metrics": {
            "correlations_discovered": len([c for c in cards if c.get("type") == "correlation"]),
            "causal_effects_found": len([c for c in cards if c.get("type") == "causal_uplift"]),
            "anomalies_detected": len([c for c in cards if c.get("type") == "anomaly"]),
            "model_confidence": "high" if data_quality["data_span_days"] >= 30 else "moderate" if data_quality["data_span_days"] >= 14 else "low",
        },
        "insufficient_data": False,
    }

@router.get("/health-score")
def health_score(session_id: str):
    try:
        daily = load_daily(session_id)
        meals = add_meal_features(load_meals(session_id))
    except KeyError:
        return {
            "error": "No session data",
            "message": "Load demo data or upload your files first.",
            "scores": {},
            "recommendations": [],
        }
    scores = calculate_metabolic_health_score(daily, meals)
    if isinstance(scores.get("nutrition"), dict) and scores["nutrition"].get("error"):
        # Don't fail; overall score excludes failed nutrition component
        pass
    recommendations = generate_personalized_recommendations(scores, daily, meals)
    return {
        "scores": scores,
        "recommendations": recommendations,
    }

@router.get("/predictions")
def predictions(session_id: str):
    try:
        daily = load_daily(session_id)
        meals = add_meal_features(load_meals(session_id))
    except KeyError:
        return {
            "glucose_prediction": {"error": "No session data", "message": "Load demo data or upload your files first."},
            "sleep_impact": {"error": "No session data"},
            "health_forecast": {"error": "No session data"},
        }
    glucose_pred = predict_glucose_response(meals, daily)
    sleep_pred = predict_sleep_impact(daily)
    forecast = generate_health_forecast(daily)
    return {
        "glucose_prediction": glucose_pred,
        "sleep_impact": sleep_pred,
        "health_forecast": forecast,
    }

@router.get("/correlations")
def correlations(session_id: str):
    try:
        daily = load_daily(session_id)
        meals = add_meal_features(load_meals(session_id))
    except KeyError:
        return {
            "hidden_correlations": [],
            "lag_correlations": [],
            "error": "No session data",
            "message": "Load demo data or upload your files first.",
        }
    hidden_correlations = discover_hidden_correlations(daily, meals)
    lag_correlations = find_lag_correlations(daily)
    return {
        "hidden_correlations": hidden_correlations,
        "lag_correlations": lag_correlations,
    }

