import pandas as pd
import numpy as np
from scipy.stats import spearmanr, pearsonr
from itertools import combinations
from typing import List, Dict, Tuple

def corr_with_p(x: pd.Series, y: pd.Series, method: str = "spearman"):
    mask = ~(x.isna() | y.isna())
    if mask.sum() < 14:
        return None, None, 0
    if method == "pearson":
        r, p = pearsonr(x[mask], y[mask])
    else:
        r, p = spearmanr(x[mask], y[mask])
    return float(r), float(p), int(mask.sum())

def discover_hidden_correlations(daily: pd.DataFrame, meals: pd.DataFrame, min_correlation: float = 0.3) -> List[Dict]:
    """
    Discover non-obvious correlations between health metrics
    """
    correlations = []
    
    # Merge data for analysis
    meals['date'] = pd.to_datetime(meals['date'])
    daily['date'] = pd.to_datetime(daily['date'])
    
    if "date" not in meals.columns:
        return []
    agg_spec = {}
    for col in ["carbs_g", "protein_g", "fat_g", "fiber_g", "late_meal", "post_meal_walk10"]:
        if col in meals.columns:
            agg_spec[col] = "sum"
    for col in ["meal_auc", "meal_peak"]:
        if col in meals.columns:
            agg_spec[col] = "mean"
    if not agg_spec:
        return []
    daily_meals = meals.groupby("date").agg(agg_spec).reset_index()
    combined = daily.merge(daily_meals, on="date", how="inner")
    
    # Define metric groups for correlation analysis
    health_metrics = ['sleep_hours', 'hrv', 'rhr', 'fg_fast_mgdl', 'steps', 'workout_min']
    nutrition_metrics = ['carbs_g', 'protein_g', 'fat_g', 'fiber_g', 'late_meal', 'post_meal_walk10']
    metabolic_metrics = ['meal_auc', 'meal_peak']
    
    all_metrics = health_metrics + nutrition_metrics + metabolic_metrics
    available_metrics = [m for m in all_metrics if m in combined.columns]
    
    # Find all pairwise correlations
    for metric1, metric2 in combinations(available_metrics, 2):
        r, p, n = corr_with_p(combined[metric1], combined[metric2])
        
        if r is not None and abs(r) >= min_correlation and p < 0.05 and n >= 20:
            # Determine if this is a "hidden" correlation (not obvious)
            is_hidden = _is_hidden_correlation(metric1, metric2)
            
            correlations.append({
                "metric1": metric1,
                "metric2": metric2,
                "correlation": r,
                "p_value": p,
                "sample_size": n,
                "is_hidden": is_hidden,
                "interpretation": _interpret_correlation(metric1, metric2, r),
                "actionable": _is_actionable_correlation(metric1, metric2)
            })
    
    # Sort by correlation strength and prioritize hidden correlations
    correlations.sort(key=lambda x: (x['is_hidden'], abs(x['correlation'])), reverse=True)
    
    return correlations[:10]  # Return top 10

def _is_hidden_correlation(metric1: str, metric2: str) -> bool:
    """Determine if correlation is non-obvious"""
    obvious_pairs = [
        ('carbs_g', 'meal_auc'),
        ('carbs_g', 'meal_peak'),
        ('sleep_hours', 'hrv'),
        ('steps', 'workout_min'),
        ('protein_g', 'fat_g')
    ]
    
    pair = tuple(sorted([metric1, metric2]))
    return pair not in obvious_pairs

def _interpret_correlation(metric1: str, metric2: str, r: float) -> str:
    """Generate human-readable interpretation"""
    strength = "strong" if abs(r) > 0.7 else "moderate" if abs(r) > 0.5 else "weak"
    direction = "increases" if r > 0 else "decreases"
    
    interpretations = {
        ('sleep_hours', 'fg_fast_mgdl'): f"More sleep {direction} fasting glucose levels",
        ('hrv', 'meal_auc'): f"Higher HRV {direction} post-meal glucose response",
        ('late_meal', 'sleep_hours'): f"Late meals {direction} sleep duration",
        ('post_meal_walk10', 'meal_peak'): f"Post-meal walks {direction} glucose peaks",
        ('fiber_g', 'meal_auc'): f"Higher fiber intake {direction} glucose response",
        ('workout_min', 'hrv'): f"More exercise {direction} heart rate variability"
    }
    
    key = tuple(sorted([metric1, metric2]))
    return interpretations.get(key, f"{metric1} and {metric2} show {strength} correlation")

def _is_actionable_correlation(metric1: str, metric2: str) -> bool:
    """Determine if correlation suggests actionable interventions"""
    actionable_metrics = ['sleep_hours', 'late_meal', 'post_meal_walk10', 'fiber_g', 'workout_min']
    return any(m in actionable_metrics for m in [metric1, metric2])

def find_lag_correlations(daily: pd.DataFrame, max_lag: int = 3) -> List[Dict]:
    """
    Find correlations with time lags (e.g., sleep affects next day's glucose)
    """
    lag_correlations = []
    
    # Define lead-lag relationships to test
    relationships = [
        ('sleep_hours', 'fg_fast_mgdl', 'Sleep quality affects next day glucose'),
        ('hrv', 'fg_fast_mgdl', 'HRV affects next day glucose'),
        ('workout_min', 'sleep_hours', 'Exercise affects sleep quality'),
        ('steps', 'hrv', 'Activity affects next day HRV')
    ]
    
    for predictor, outcome, description in relationships:
        if predictor not in daily.columns or outcome not in daily.columns:
            continue
            
        daily_sorted = daily.sort_values('date').copy()
        
        for lag in range(1, max_lag + 1):
            # Create lagged predictor
            daily_sorted[f'{predictor}_lag{lag}'] = daily_sorted[predictor].shift(lag)
            
            # Calculate correlation
            r, p, n = corr_with_p(
                daily_sorted[f'{predictor}_lag{lag}'], 
                daily_sorted[outcome]
            )
            
            if r is not None and abs(r) >= 0.3 and p < 0.05 and n >= 15:
                lag_correlations.append({
                    "predictor": predictor,
                    "outcome": outcome,
                    "lag_days": lag,
                    "correlation": r,
                    "p_value": p,
                    "sample_size": n,
                    "description": description,
                    "interpretation": f"{predictor} from {lag} day(s) ago {description.lower()}"
                })
    
    return sorted(lag_correlations, key=lambda x: abs(x['correlation']), reverse=True)
