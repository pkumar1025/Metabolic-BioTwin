import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from typing import Dict, List, Tuple

def predict_glucose_response(meals: pd.DataFrame, daily: pd.DataFrame) -> Dict:
    """
    Predict glucose response based on meal composition and recent health patterns
    """
    # Merge meal and daily data
    meals['date'] = pd.to_datetime(meals['date'])
    daily['date'] = pd.to_datetime(daily['date'])
    
    # Create features for prediction
    features = []
    targets = []
    
    for _, meal in meals.iterrows():
        if pd.isna(meal['meal_auc']):
            continue
            
        # Get recent health context (last 3 days)
        recent_daily = daily[daily['date'] <= meal['date']].tail(3)
        
        if len(recent_daily) == 0:
            continue
            
        # Meal features
        meal_features = [
            meal['carbs_g'],
            meal['protein_g'], 
            meal['fat_g'],
            meal['fiber_g'],
            meal['carbs_pct'],
            meal['late_meal'],
            meal['post_meal_walk10']
        ]
        
        # Recent health context
        health_features = [
            recent_daily['sleep_hours'].mean(),
            recent_daily['hrv'].mean(),
            recent_daily['rhr'].mean(),
            recent_daily['fg_fast_mgdl'].mean(),
            recent_daily['steps'].mean() if 'steps' in recent_daily.columns else 0,
            recent_daily['workout_min'].mean() if 'workout_min' in recent_daily.columns else 0
        ]
        
        # Time-based features
        time_features = [
            meal['time'].hour if pd.notna(meal['time']) else 12,
            meal['time'].minute if pd.notna(meal['time']) else 0
        ]
        
        features.append(meal_features + health_features + time_features)
        targets.append(meal['meal_auc'])
    
    if len(features) < 20:
        return {"error": "Insufficient data for prediction"}
    
    X = np.array(features)
    y = np.array(targets)
    
    # Train model
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    # Feature importance
    feature_names = [
        'carbs_g', 'protein_g', 'fat_g', 'fiber_g', 'carbs_pct', 'late_meal', 'post_meal_walk10',
        'avg_sleep', 'avg_hrv', 'avg_rhr', 'avg_fg', 'avg_steps', 'avg_workout',
        'meal_hour', 'meal_minute'
    ]
    
    importance = dict(zip(feature_names, model.feature_importances_))
    
    return {
        "model_performance": {
            "mae": float(mae),
            "r2_score": float(r2),
            "n_samples": len(features)
        },
        "feature_importance": importance,
        "predictions": {
            "test_actual": y_test.tolist(),
            "test_predicted": y_pred.tolist()
        }
    }

def predict_sleep_impact(daily: pd.DataFrame) -> Dict:
    """
    Predict how sleep quality will impact next-day metrics
    """
    if len(daily) < 14:
        return {"error": "Insufficient data for prediction"}
    
    # Create lagged features
    daily_sorted = daily.sort_values('date').copy()
    daily_sorted['sleep_prev'] = daily_sorted['sleep_hours'].shift(1)
    daily_sorted['hrv_prev'] = daily_sorted['hrv'].shift(1)
    daily_sorted['rhr_prev'] = daily_sorted['rhr'].shift(1)
    
    # Features: previous night's sleep metrics
    # Target: next day's fasting glucose
    features = daily_sorted[['sleep_prev', 'hrv_prev', 'rhr_prev']].dropna()
    targets = daily_sorted.loc[features.index, 'fg_fast_mgdl']
    
    if len(features) < 10:
        return {"error": "Insufficient data for prediction"}
    
    # Simple linear model for interpretability
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    model.fit(features, targets)
    
    # Predictions for different sleep scenarios
    scenarios = [
        {"sleep_hours": 6, "hrv": 40, "rhr": 65},
        {"sleep_hours": 7, "hrv": 45, "rhr": 60},
        {"sleep_hours": 8, "hrv": 50, "rhr": 55},
        {"sleep_hours": 9, "hrv": 55, "rhr": 50}
    ]
    
    predictions = []
    for scenario in scenarios:
        pred_fg = model.predict([[scenario['sleep_hours'], scenario['hrv'], scenario['rhr']]])[0]
        predictions.append({
            "scenario": f"{scenario['sleep_hours']}h sleep",
            "predicted_fg": float(pred_fg),
            "sleep_hours": scenario['sleep_hours'],
            "hrv": scenario['hrv'],
            "rhr": scenario['rhr']
        })
    
    return {
        "model_coefficients": {
            "sleep_hours": float(model.coef_[0]),
            "hrv": float(model.coef_[1]),
            "rhr": float(model.coef_[2]),
            "intercept": float(model.intercept_)
        },
        "scenario_predictions": predictions,
        "r2_score": float(model.score(features, targets))
    }

def generate_health_forecast(daily: pd.DataFrame, days_ahead: int = 7) -> Dict:
    """
    Generate health forecast based on current trends
    """
    if len(daily) < 14:
        return {"error": "Insufficient data for forecasting"}
    
    daily_sorted = daily.sort_values('date').copy()
    
    # Calculate trends for key metrics
    metrics = ['sleep_hours', 'hrv', 'rhr', 'fg_fast_mgdl']
    forecasts = {}
    
    for metric in metrics:
        if metric not in daily_sorted.columns:
            continue
            
        values = daily_sorted[metric].dropna()
        if len(values) < 7:
            continue
            
        # Simple trend analysis
        recent_trend = values.tail(7).mean() - values.head(7).mean()
        current_value = values.iloc[-1]
        
        # Forecast (simple linear projection)
        forecast_values = []
        for i in range(1, days_ahead + 1):
            forecast_val = current_value + (recent_trend / 7) * i
            forecast_values.append({
                "day": i,
                "predicted_value": float(forecast_val),
                "confidence": "high" if abs(recent_trend) < 2 else "moderate"
            })
        
        forecasts[metric] = {
            "current_value": float(current_value),
            "trend": float(recent_trend),
            "forecast": forecast_values
        }
    
    return forecasts
