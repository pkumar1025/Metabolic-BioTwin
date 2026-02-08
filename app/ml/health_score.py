import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

def calculate_metabolic_health_score(daily: pd.DataFrame, meals: pd.DataFrame) -> Dict:
    """
    Calculate comprehensive metabolic health score based on multiple factors
    """
    if len(daily) == 0:
        return {"error": "No data available"}
    
    # Get recent data (last 30 days or all available)
    recent_daily = daily.tail(30)
    recent_meals = meals.tail(100) if len(meals) > 0 else pd.DataFrame()
    
    scores = {}
    
    # 1. Glucose Control Score (0-100)
    if 'fg_fast_mgdl' in recent_daily.columns:
        fg_values = recent_daily['fg_fast_mgdl'].dropna()
        if len(fg_values) > 0:
            avg_fg = fg_values.mean()
            fg_score = max(0, min(100, 100 - (avg_fg - 85) * 2))  # Optimal: 85 mg/dL
            scores['glucose_control'] = {
                'score': round(fg_score, 1),
                'average_fg': round(avg_fg, 1),
                'trend': _calculate_trend(fg_values),
                'interpretation': _interpret_glucose_score(fg_score)
            }
    
    # 2. Sleep Quality Score (0-100)
    if 'sleep_hours' in recent_daily.columns:
        sleep_values = recent_daily['sleep_hours'].dropna()
        if len(sleep_values) > 0:
            avg_sleep = sleep_values.mean()
            sleep_score = max(0, min(100, avg_sleep / 8 * 100))  # Optimal: 8 hours
            scores['sleep_quality'] = {
                'score': round(sleep_score, 1),
                'average_sleep': round(avg_sleep, 1),
                'trend': _calculate_trend(sleep_values),
                'interpretation': _interpret_sleep_score(sleep_score)
            }
    
    # 3. Recovery Score (HRV-based)
    if 'hrv' in recent_daily.columns:
        hrv_values = recent_daily['hrv'].dropna()
        if len(hrv_values) > 0:
            avg_hrv = hrv_values.mean()
            hrv_score = max(0, min(100, (avg_hrv - 30) / 20 * 100))  # Scale 30-50 to 0-100
            scores['recovery'] = {
                'score': round(hrv_score, 1),
                'average_hrv': round(avg_hrv, 1),
                'trend': _calculate_trend(hrv_values),
                'interpretation': _interpret_hrv_score(hrv_score)
            }
    
    # 4. Nutrition Score
    if len(recent_meals) > 0:
        nutrition_score = _calculate_nutrition_score(recent_meals)
        scores['nutrition'] = nutrition_score
    
    # 5. Activity Score
    if 'steps' in recent_daily.columns:
        steps_values = recent_daily['steps'].dropna()
        if len(steps_values) > 0:
            avg_steps = steps_values.mean()
            activity_score = max(0, min(100, avg_steps / 10000 * 100))  # Target: 10k steps
            scores['activity'] = {
                'score': round(activity_score, 1),
                'average_steps': int(avg_steps),
                'trend': _calculate_trend(steps_values),
                'interpretation': _interpret_activity_score(activity_score)
            }
    
    # Calculate overall health score
    if scores:
        overall_score = np.mean([s['score'] for s in scores.values() if 'score' in s])
        scores['overall'] = {
            'score': round(overall_score, 1),
            'grade': _get_health_grade(overall_score),
            'interpretation': _interpret_overall_score(overall_score),
            'components': len(scores) - 1  # Exclude overall itself
        }
    
    return scores

def _calculate_trend(values: pd.Series) -> str:
    """Calculate trend direction"""
    if len(values) < 7:
        return "insufficient_data"
    
    first_half = values.head(len(values)//2).mean()
    second_half = values.tail(len(values)//2).mean()
    
    if second_half > first_half * 1.05:
        return "improving"
    elif second_half < first_half * 0.95:
        return "declining"
    else:
        return "stable"

def _interpret_glucose_score(score: float) -> str:
    if score >= 90:
        return "Excellent glucose control"
    elif score >= 75:
        return "Good glucose control"
    elif score >= 60:
        return "Moderate glucose control - room for improvement"
    else:
        return "Poor glucose control - needs attention"

def _interpret_sleep_score(score: float) -> str:
    if score >= 90:
        return "Excellent sleep quality"
    elif score >= 75:
        return "Good sleep quality"
    elif score >= 60:
        return "Moderate sleep quality - could be better"
    else:
        return "Poor sleep quality - needs improvement"

def _interpret_hrv_score(score: float) -> str:
    if score >= 80:
        return "Excellent recovery and stress resilience"
    elif score >= 60:
        return "Good recovery"
    elif score >= 40:
        return "Moderate recovery - consider stress management"
    else:
        return "Poor recovery - high stress levels"

def _interpret_activity_score(score: float) -> str:
    if score >= 90:
        return "Excellent activity level"
    elif score >= 75:
        return "Good activity level"
    elif score >= 60:
        return "Moderate activity - could be more active"
    else:
        return "Low activity - needs more movement"

def _interpret_overall_score(score: float) -> str:
    if score >= 85:
        return "Outstanding metabolic health"
    elif score >= 70:
        return "Good metabolic health"
    elif score >= 55:
        return "Moderate metabolic health - some areas need attention"
    else:
        return "Poor metabolic health - significant improvements needed"

def _get_health_grade(score: float) -> str:
    if score >= 90:
        return "A+"
    elif score >= 85:
        return "A"
    elif score >= 80:
        return "A-"
    elif score >= 75:
        return "B+"
    elif score >= 70:
        return "B"
    elif score >= 65:
        return "B-"
    elif score >= 60:
        return "C+"
    elif score >= 55:
        return "C"
    elif score >= 50:
        return "C-"
    else:
        return "D"

def _calculate_nutrition_score(meals: pd.DataFrame) -> Dict:
    """Calculate nutrition quality score. Uses only columns that exist; no placeholders."""
    if len(meals) == 0:
        return {"error": "No meal data"}
    if "date" not in meals.columns:
        return {"error": "Meals must have a date column for nutrition score"}

    agg_map = {}
    for col in ["carbs_g", "protein_g", "fat_g", "fiber_g", "late_meal", "post_meal_walk10"]:
        if col in meals.columns:
            agg_map[col] = "sum"
    if not agg_map:
        return {"error": "Meals need at least one of: carbs_g, protein_g, fat_g, fiber_g, late_meal, post_meal_walk10"}

    daily_nutrition = meals.groupby("date").agg(agg_map).reset_index()
    components = []
    out = {}

    if "fiber_g" in daily_nutrition.columns:
        avg_fiber = daily_nutrition["fiber_g"].mean()
        fiber_score = max(0, min(100, avg_fiber / 25 * 100))
        components.append(fiber_score)
        out["fiber_score"] = round(fiber_score, 1)
    if "late_meal" in daily_nutrition.columns:
        late_meals_pct = (daily_nutrition["late_meal"] > 0).mean()
        timing_score = max(0, 100 - late_meals_pct * 100)
        components.append(timing_score)
        out["timing_score"] = round(timing_score, 1)
    if "post_meal_walk10" in daily_nutrition.columns:
        post_meal_walks_pct = (daily_nutrition["post_meal_walk10"] > 0).mean()
        activity_score = post_meal_walks_pct * 100
        components.append(activity_score)
        out["activity_score"] = round(activity_score, 1)

    if not components:
        return {"error": "Insufficient meal columns for nutrition score"}
    overall_nutrition_score = sum(components) / len(components)
    out["score"] = round(overall_nutrition_score, 1)
    out["interpretation"] = _interpret_nutrition_score(overall_nutrition_score)
    return out

def _interpret_nutrition_score(score: float) -> str:
    if score >= 80:
        return "Excellent nutrition habits"
    elif score >= 65:
        return "Good nutrition habits"
    elif score >= 50:
        return "Moderate nutrition - some improvements needed"
    else:
        return "Poor nutrition habits - needs significant improvement"

def generate_personalized_recommendations(health_scores: Dict, daily: pd.DataFrame, meals: pd.DataFrame) -> List[Dict]:
    """
    Generate personalized recommendations based on health scores
    """
    recommendations = []
    
    if 'overall' not in health_scores:
        return recommendations
    
    overall_score = health_scores['overall']['score']
    
    # Priority-based recommendations
    if 'glucose_control' in health_scores and health_scores['glucose_control']['score'] < 70:
        recommendations.append({
            'priority': 'high',
            'category': 'glucose_control',
            'title': 'Improve Glucose Control',
            'description': 'Your fasting glucose levels need attention',
            'actions': [
                'Increase fiber intake to 25g+ daily',
                'Take 10-minute walks after meals',
                'Avoid late dinners (before 7 PM)',
                'Target 7-8 hours of sleep nightly'
            ],
            'expected_impact': 'Could improve glucose score by 15-20 points in 2 weeks'
        })
    
    if 'sleep_quality' in health_scores and health_scores['sleep_quality']['score'] < 75:
        recommendations.append({
            'priority': 'high',
            'category': 'sleep',
            'title': 'Optimize Sleep Quality',
            'description': 'Sleep quality is impacting your metabolic health',
            'actions': [
                'Maintain consistent sleep schedule',
                'Avoid screens 1 hour before bed',
                'Keep bedroom cool (65-68°F)',
                'Limit caffeine after 2 PM'
            ],
            'expected_impact': 'Could improve sleep score by 10-15 points in 1 week'
        })
    
    if 'recovery' in health_scores and health_scores['recovery']['score'] < 60:
        recommendations.append({
            'priority': 'medium',
            'category': 'recovery',
            'title': 'Enhance Recovery',
            'description': 'Your HRV indicates high stress levels',
            'actions': [
                'Practice 10 minutes of meditation daily',
                'Take regular breaks during work',
                'Engage in light exercise (walking, yoga)',
                'Consider stress management techniques'
            ],
            'expected_impact': 'Could improve recovery score by 10-20 points in 2-3 weeks'
        })
    
    if 'nutrition' in health_scores and health_scores['nutrition']['score'] < 65:
        recommendations.append({
            'priority': 'medium',
            'category': 'nutrition',
            'title': 'Improve Nutrition Habits',
            'description': 'Nutrition patterns need optimization',
            'actions': [
                'Increase fiber-rich foods (vegetables, whole grains)',
                'Eat dinner before 7 PM',
                'Take short walks after meals',
                'Focus on balanced macronutrients'
            ],
            'expected_impact': 'Could improve nutrition score by 15-25 points in 2 weeks'
        })
    
    # Add positive reinforcement for good scores
    if overall_score >= 80:
        recommendations.append({
            'priority': 'low',
            'category': 'maintenance',
            'title': 'Maintain Excellent Health',
            'description': 'You\'re doing great! Keep up the good work',
            'actions': [
                'Continue current healthy habits',
                'Monitor trends regularly',
                'Consider adding new challenges',
                'Share your success with others'
            ],
            'expected_impact': 'Maintain current excellent health status'
        })
    
    return recommendations
