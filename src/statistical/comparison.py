"""
CLIMAIA – Event Comparison Engine
Computes comparative metrics between raw and treated extreme event masks.
"""

import pandas as pd
import numpy as np


def compare_event_masks(raw_mask: pd.Series, treated_mask: pd.Series) -> dict:
    """
    Compare two boolean event masks to calculate overlap, creation, and suppression rates.
    
    Parameters:
        raw_mask: Boolean Series for raw data events.
        treated_mask: Boolean Series for treated data events.
        
    Returns:
        A dictionary containing:
            total_raw: Total raw events
            total_treated: Total treated events
            coincident: Overlapping events
            created: Events created by treatment
            suppressed: Real events suppressed by treatment
            agreement_pct: Overlap agreement percentage (Jaccard-like index)
    """
    # Convert to boolean numpy arrays, handling type issues
    try:
        r_vals = np.asarray(raw_mask, dtype=bool)
        t_vals = np.asarray(treated_mask, dtype=bool)
    except (ValueError, TypeError):
        r_vals = np.asarray(raw_mask.fillna(False), dtype=bool)
        t_vals = np.asarray(treated_mask.fillna(False), dtype=bool)
    
    # Align to same length if different
    if len(r_vals) != len(t_vals):
        min_len = min(len(r_vals), len(t_vals))
        r_arr = r_vals[:min_len]
        t_arr = t_vals[:min_len]
    else:
        r_arr = r_vals
        t_arr = t_vals
        
    total_raw = int(np.sum(r_arr))
    total_treated = int(np.sum(t_arr))
    
    coincident = int(np.sum(r_arr & t_arr))
    created = int(np.sum((~r_arr) & t_arr))
    suppressed = int(np.sum(r_arr & (~t_arr)))
    
    union = coincident + created + suppressed
    agreement_pct = (coincident / union * 100.0) if union > 0 else 100.0
    
    return {
        "total_raw": total_raw,
        "total_treated": total_treated,
        "coincident": coincident,
        "created": created,
        "suppressed": suppressed,
        "agreement_pct": agreement_pct
    }
