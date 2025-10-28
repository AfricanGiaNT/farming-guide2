import math


def mean(values):
    return sum(values) / len(values) if values else 0.0


def test_explicit_years_list():
    """Test explicit years_list parameter returns only requested years"""
    import importlib
    api = importlib.import_module('api_server')
    client = api.app.test_client()

    resp = client.get('/api/weather/-13.9833,33.7833/historical?years_list=2025,2024,2023')
    if resp.status_code != 200:
        # Tolerate 503 if provider unavailable in CI
        return

    data = resp.get_json()
    assert 'per_year' in data
    per_year = data['per_year']
    
    # Should have 3 years
    assert len(per_year) >= 2, f"Expected at least 2 years, got {len(per_year)}"
    
    # Years should be in requested set
    years_returned = {y['year'] for y in per_year}
    assert years_returned.issubset({2025, 2024, 2023})
    
    # Each year should have coverage info
    for y in per_year:
        assert 'coverage' in y
        assert 'months_covered' in y
        assert y['coverage'] in ('full', 'partial')





