def stockout_risk_label(stockout_risk: float) -> str:
    if stockout_risk >= 0.70:
        return "high"
    if stockout_risk >= 0.40:
        return "medium"
    return "low"
