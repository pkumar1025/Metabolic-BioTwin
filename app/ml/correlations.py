import pandas as pd
from scipy.stats import spearmanr, pearsonr

def corr_with_p(x: pd.Series, y: pd.Series, method: str = "spearman"):
    mask = ~(x.isna() | y.isna())
    if mask.sum() < 14:
        return None, None, 0
    if method == "pearson":
        r, p = pearsonr(x[mask], y[mask])
    else:
        r, p = spearmanr(x[mask], y[mask])
    return float(r), float(p), int(mask.sum())
