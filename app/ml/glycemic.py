import pandas as pd


def add_meal_features(meals: pd.DataFrame) -> pd.DataFrame:
    """Add derived meal features. Only adds carbs_pct when macros exist; otherwise returns unchanged."""
    m = meals.copy()
    required = {"carbs_g", "protein_g", "fat_g"}
    if not required.issubset(m.columns):
        return m
    total = (m["carbs_g"] + m["protein_g"] + m["fat_g"]).replace(0, 1e-6)
    m["carbs_pct"] = m["carbs_g"] / total
    return m
