from src.recommend_actions import make_recommendation

def test_high_stockout_requires_human_review():
    result = make_recommendation(stockout_risk=0.9, service_level=0.75)
    assert result["human_review_required"] is True

def test_low_risk_good_service_no_action():
    result = make_recommendation(stockout_risk=0.1, service_level=0.98)
    assert result["human_review_required"] is False
