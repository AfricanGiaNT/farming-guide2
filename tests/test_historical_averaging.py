import math


def mean(values):
    return sum(values) / len(values) if values else 0.0


def test_multi_year_includes_per_year_and_multi_year():
    import importlib
    api = importlib.import_module('api_server')
    client = api.app.test_client()

    resp = client.get('/api/weather/-13.9833,33.7833/historical?years=3')
    assert resp.status_code in (200, 503)
    if resp.status_code != 200:
        return

    data = resp.get_json()
    assert 'per_year' in data
    assert 'multi_year' in data
    assert isinstance(data['per_year'], list)
    assert isinstance(data['multi_year'], dict)


def test_multi_year_annual_average_is_mean_when_available():
    import importlib
    api = importlib.import_module('api_server')
    client = api.app.test_client()

    resp = client.get('/api/weather/-13.9833,33.7833/historical?years=3')
    if resp.status_code != 200:
        return

    data = resp.get_json()
    per_year = data.get('per_year', [])
    if len(per_year) < 2:
        return

    expected = mean([y['annual_rainfall'] for y in per_year])
    actual = data['multi_year']['annual_average']
    assert math.isclose(actual, expected, rel_tol=1e-6)


def test_multi_year_monthly_average_is_mean_when_available():
    import importlib
    api = importlib.import_module('api_server')
    client = api.app.test_client()

    resp = client.get('/api/weather/-13.9833,33.7833/historical?years=3')
    if resp.status_code != 200:
        return

    data = resp.get_json()
    per_year = data.get('per_year', [])
    if len(per_year) < 2:
        return

    months = ['January','February','March','April','May','June','July','August','September','October','November','December']
    for m in months:
        vals = [y['monthly'].get(m, 0) for y in per_year]
        expected = mean(vals)
        actual = data['multi_year']['monthly_average'].get(m, 0)
        assert math.isclose(actual, expected, rel_tol=0.05)
