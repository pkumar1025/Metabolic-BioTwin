import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression, LinearRegression

def _bootstrap_ci(vals: np.ndarray, iters: int = 300, alpha: float = 0.05):
    idx = np.random.randint(0, len(vals), (iters, len(vals)))
    boots = vals[idx].mean(axis=1)
    lo = float(np.percentile(boots, 100*alpha/2))
    hi = float(np.percentile(boots, 100*(1-alpha/2)))
    return lo, hi

def doubly_robust_ate(df: pd.DataFrame, treat_col: str, outcome_col: str, confounders: list[str]):
    use = df[[treat_col, outcome_col] + confounders].dropna()
    if len(use) < 30:
        return None
    X = use[confounders].values
    T = use[treat_col].values.astype(int)
    Y = use[outcome_col].values.astype(float)

    lr = LogisticRegression(max_iter=1000)
    lr.fit(X, T)
    p = lr.predict_proba(X)[:, 1]
    eps = 1e-6

    m0 = LinearRegression().fit(X[T==0], Y[T==0]) if (T==0).any() else None
    m1 = LinearRegression().fit(X[T==1], Y[T==1]) if (T==1).any() else None
    mu0 = m0.predict(X) if m0 else np.full_like(Y, Y.mean())
    mu1 = m1.predict(X) if m1 else np.full_like(Y, Y.mean())

    dr = (T*(Y - mu1))/(p+eps) - ((1-T)*(Y - mu0))/(1-p+eps) + (mu1 - mu0)
    ate = float(np.mean(dr))
    lo, hi = _bootstrap_ci(dr)
    return {"ate": ate, "ci": (lo, hi), "n": int(len(use))}
