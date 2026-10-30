from src.dashboard.metrics import calculate_unavailability_rate

def test_unavailability_rate():
    assert calculate_unavailability_rate(25, 100) == 25.0

def test_zero_bike_observations():
    assert calculate_unavailability_rate(0, 100) == 0.0

def test_no_eligible_observations():
    assert calculate_unavailability_rate(0, 0) == 0.0

def test_real_dashboard_values():
    rate = calculate_unavailability_rate(26439, 449619)
    assert round(rate, 2) == 5.88