import pandas as pd

def add_meal_features(meals: pd.DataFrame) -> pd.DataFrame:
    m = meals.copy()
    total = (m["carbs_g"] + m["protein_g"] + m["fat_g"]).replace(0, 1e-6)
    m["carbs_pct"] = m["carbs_g"] / total
    return m
