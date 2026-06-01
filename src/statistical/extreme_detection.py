"""
CLIMAIA – Extreme Event Detection Engine
Implements statistical methods for detecting extreme weather events.
"""

import numpy as np
import pandas as pd
from scipy import stats


def detect_extremes(df: pd.DataFrame, column: str, method: str, threshold_pct: float, date_col: str = None) -> pd.Series:
    """
    Detect extreme events in a time series using various statistical methods.
    
    Parameters:
        df: Pandas DataFrame containing the data.
        column: Column name to analyze.
        method: Method name, e.g., 'Percentil Adaptativo (P95/P99)', 'Teoria de Valores Extremos (EVT)',
                'Distribuição de Gumbel', 'Z-Score (Desvio Padrão)', 'IQR (Interquartil Range)', 'Todos os Métodos'.
        threshold_pct: Sensitivity threshold percentage (e.g., 95 or 99).
        date_col: Optional column name containing date/time index.
        
    Returns:
        A boolean Pandas Series where True indicates an extreme event.
    """
    if df is None or column not in df.columns:
        return pd.Series(False, index=df.index if df is not None else [])
    
    series = pd.to_numeric(df[column], errors='coerce').ffill().bfill()
    
    # Check if we have valid numeric values
    if series.dropna().empty:
        return pd.Series(False, index=df.index)

    # 1. Adapt percentile to probability
    alpha = threshold_pct / 100.0
    
    if "Percentil" in method:
        # Simple percentile thresholding
        limit = np.percentile(series.dropna(), threshold_pct)
        return series > limit

    elif "Z-Score" in method:
        # Standardize and check standard deviation threshold
        # Map 95% -> 1.96, 99% -> 2.58, etc.
        z_scores = np.abs(stats.zscore(series))
        # Find critical z value for given two-tailed or one-tailed percentile
        critical_z = stats.norm.ppf(alpha)
        return z_scores > critical_z

    elif "IQR" in method:
        # Interquartile Range method
        q25, q75 = np.percentile(series.dropna(), [25, 75])
        iqr = q75 - q25
        # Sensitivity adjustment: map threshold to multiplier
        # 95% threshold -> standard 1.5 * IQR. 99% -> 3.0 * IQR
        multiplier = 1.5 if threshold_pct <= 95 else 3.0
        limit = q75 + multiplier * iqr
        return series > limit

    elif "Gumbel" in method:
        # Fit Gumbel distribution (right-skewed extreme value)
        try:
            params = stats.gumbel_r.fit(series.dropna())
            # Find the threshold value corresponding to alpha probability
            limit = stats.gumbel_r.ppf(alpha, *params)
            return series > limit
        except Exception:
            # Fallback to percentile if fit fails
            limit = np.percentile(series.dropna(), threshold_pct)
            return series > limit

    elif "Teoria de Valores Extremos" in method or "EVT" in method:
        # Fit Generalized Extreme Value (GEV) distribution
        try:
            params = stats.genextreme.fit(series.dropna())
            limit = stats.genextreme.ppf(alpha, *params)
            return series > limit
        except Exception:
            # Fallback to Gumbel/percentile if fit fails
            limit = np.percentile(series.dropna(), threshold_pct)
            return series > limit

    elif "Todos" in method:
        # Voting system: returns True if at least 2 methods agree
        m1 = detect_extremes(df, column, "Percentil Adaptativo (P95/P99)", threshold_pct)
        m2 = detect_extremes(df, column, "Z-Score (Desvio Padrão)", threshold_pct)
        m3 = detect_extremes(df, column, "IQR (Interquartil Range)", threshold_pct)
        m4 = detect_extremes(df, column, "Distribuição de Gumbel", threshold_pct)
        
        votes = m1.astype(int) + m2.astype(int) + m3.astype(int) + m4.astype(int)
        return votes >= 2

    else:
        # Fallback
        limit = np.percentile(series.dropna(), threshold_pct)
        return series > limit
