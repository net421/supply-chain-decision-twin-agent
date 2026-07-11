def make_recommendation(stockout_risk: float, service_level: float) -> dict:
    if stockout_risk >= 0.70:
        return {
            "recommended_action": "Review expedited replenishment",
            "human_review_required": True,
            "reason": "Stockout risk exceeds governed threshold."
        }

    if service_level < 0.80:
        return {
            "recommended_action": "Review service-level risk",
            "human_review_required": True,
            "reason": "Service level is below minimum expected threshold."
        }

    return {
        "recommended_action": "No action required",
        "human_review_required": False,
        "reason": "KPIs are within governed thresholds."
    }
