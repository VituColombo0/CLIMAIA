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
            agreement_pct: Overlap agreement percentage (Jaccard-like index or simple overlap ratio)
    """
    # Ensure they are boolean and aligned
    # If index alignment is possible, align them. Otherwise, slice to same length.
    if len(raw_mask) != len(treated_mask):
        min_len = min(len(raw_mask), len(treated_mask))
        r_arr = raw_mask.values[:min_len]
        t_arr = treated_mask.values[:min_len]
    else:
        # Align by index if they are pandas Series
        combined = pd.DataFrame({'raw': raw_mask, 'treated': treated_mask}).dropna()
        r_arr = combined['raw'].values
        t_arr = combined['treated'].values
        
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
