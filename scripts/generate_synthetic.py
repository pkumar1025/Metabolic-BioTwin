import pandas as pd, numpy as np
from pathlib import Path
from datetime import datetime, timedelta

DEMO = Path(__file__).resolve().parents[1] / "app" / "data" / "demo"
DEMO.mkdir(parents=True, exist_ok=True)

np.random.seed(42)

days = 90
start = datetime.today().date() - timedelta(days=days)
dates = [start + timedelta(days=i) for i in range(days)]

# Sleep / HRV / RHR
sleep_hours = np.clip(np.random.normal(7.1, 1.0, days), 4.0, 9.5)
hrv = np.clip(np.random.normal(45, 8, days) + 0.6*(sleep_hours-7), 20, 80)
rhr = np.clip(np.random.normal(60, 4, days) - 0.5*(sleep_hours-7), 50, 80)

sleep_df = pd.DataFrame({"date": dates, "sleep_hours": sleep_hours.round(2), "hrv": hrv.round(1), "rhr": rhr.round(1)})
sleep_df.to_csv(DEMO / "sleep.csv", index=False)

# Activity
steps = np.clip(np.random.normal(8500, 2500, days), 1500, 18000)
workout_min = np.clip(np.random.normal(25, 20, days), 0, 120)
hydration_l = np.clip(np.random.normal(2.2, 0.6, days), 0.8, 4.0)
activity_df = pd.DataFrame({"date": dates, "steps": steps.astype(int), "workout_min": workout_min.astype(int), "hydration_l": hydration_l.round(2)})
activity_df.to_csv(DEMO / "activity.csv", index=False)

# Vitals — fasting glucose, with a mild sickness window
fg = np.clip(np.random.normal(95, 5, days), 80, 115)
sick_start = np.random.randint(20, 60)
fg[sick_start:sick_start+4] += 6
vitals_df = pd.DataFrame({"date": dates, "fg_fast_mgdl": fg.round(1)})
vitals_df.to_csv(DEMO / "vitals.csv", index=False)

# Meals — 2-3 per day
rows = []
for d in dates:
    n = np.random.choice([2,3], p=[0.4,0.6])
    for i in range(n):
        hour = np.random.choice([8,12,19,21], p=[0.3,0.35,0.25,0.10])
        minute = np.random.choice([0,15,30,45])
        time = f"{hour:02d}:{minute:02d}"
        late_meal = 1 if hour >= 21 else 0
        carbs = np.clip(np.random.normal(60, 25), 10, 140)
        protein = np.clip(np.random.normal(25, 12), 5, 70)
        fat = np.clip(np.random.normal(20, 10), 3, 60)
        fiber = np.clip(np.random.normal(7, 3), 1, 20)
        # behavior: 10-min post-meal walk more likely on lunch/dinner
        post_walk = np.random.choice([0,1], p=[0.6,0.4]) if hour in [12,19] else np.random.choice([0,1], p=[0.8,0.2])

        # glycemic response (AUC/peak) — simple generative rules
        total = carbs + protein + fat
        carbs_pct = carbs / max(total, 1e-6)

        # base
        auc = 60 + 0.6*carbs + 0.2*(carbs_pct*100) - 1.5*fiber
        peak = 105 + 0.25*carbs - 1.0*fiber

        # penalties / benefits
        # previous night sleep effect will be applied downstream; add mild noise here
        if late_meal: 
            auc *= 1.10
            peak += 10
        if post_walk:
            auc *= 0.88
            peak -= 8

        # noise
        auc += np.random.normal(0, 8)
        peak += np.random.normal(0, 6)

        ttpeak = int(np.clip(np.random.normal(55, 10), 30, 90))

        rows.append({
            "date": d, "time": time, "carbs_g": round(carbs,1), "protein_g": round(protein,1), "fat_g": round(fat,1),
            "fiber_g": round(fiber,1), "late_meal": late_meal, "post_meal_walk10": post_walk,
            "meal_auc": round(max(20, auc),1), "meal_peak": round(max(85, peak),1), "ttpeak_min": ttpeak
        })

meals_df = pd.DataFrame(rows).sort_values(["date","time"])
meals_df.to_csv(DEMO / "meals.csv", index=False)

print("Synthetic CSVs written to", DEMO)
