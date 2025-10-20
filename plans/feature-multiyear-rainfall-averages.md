# Feature Plan – Multi‑Year Rainfall Averages with Year Accordions

## 1) One‑Paragraph Brief
We will enable users to view rainfall across multiple years with correct averaging. When more than one year is requested, annual rainfall will be the average (mean) of selected years, not a sum, and monthly values will reflect per‑year totals with a multi‑year monthly average for context. The UI will show the most recent year expanded by default with older years collapsed as accordions, each mirroring the monthly rainfall table. Success is a clear, accurate view of yearly breakdowns and straightforward comparison across years, with additive backend contracts and no regressions to existing consumers.

## 2) Clarify Intent & Scope (Q&A)
1. Problem & Goal: Current multi‑year totals imply summation; users need averages for better comparability. Goal: provide per‑year breakdowns and averaged multi‑year metrics.
2. Actors & Personas: Human end‑users via web UI; backend API consumable by the frontend. No special roles.
3. Primary Use Cases:
   - Select N years (1–10) and see per‑year sections with monthly totals and annual total.
   - See multi‑year annual average and monthly averages across years.
   - Quickly compare years, with latest expanded by default.
4. Out‑of‑Scope: New data providers, anomaly detection, trend modeling, seasonal clustering.
5. Definition of Success: For N>1, “annual” figures shown are averages; per‑year accordions render correctly; existing `monthly_averages` consumers remain unaffected.
6. Dependencies: Open‑Meteo Archive; existing `/api/weather/<lat,lon>/historical?years=N` endpoint; on‑disk cache.
7. Constraints: Free provider limits, local network reliability, UI performance on low‑end devices.
8. Environment Impact: Local/dev/prod identical logic; secrets unchanged; cache file at `data/weather_cache.json`.
9. Backward Compatibility: Additive response; no removals; old clients still work.
10. Risks/Unknowns: Partial months, provider outages, timezone boundary effects, inconsistent month keys, Windows console encoding issues in logs.

## 3) Map the Workflow
- Happy Path:
  1. User selects N years and clicks Generate.
  2. Backend fetches daily data for the date range (last N years), aggregates per year and per month.
  3. Backend returns: `per_year[]`, `multi_year.annual_average`, `multi_year.monthly_average`, and existing `monthly_averages`.
  4. UI renders multi‑year averages summary and year accordions (latest expanded).
- Variants:
  - Variant A: N=1 → single year, no accordions.
  - Variant B: Missing months → render 0 with subtle indicator.
  - Variant C: Cache hit → faster response.
- Edge Cases:
  - Timeouts/retries; partial year; invalid N (<=0 or >10); leap year dates; duplicate days; zero rainfall months; network split; provider schema change.
- State Changes & Invariants:
  - Cache key includes lat, lon, start, end; invariant: monthly keys are the 12 month names.
- Error UX:
  - Clear message on fetch failure; suggest retry; log correlation ID client‑side for support.

## 4) Data & Interfaces
- Entities:
  - HistoricalYear: year (int), monthly {Month: number}, annual_rainfall (number)
  - MultiYearSummary: annual_average (number), monthly_average {Month: number}
- API Contract (additive):
  - Request: `GET /api/weather/<lat>,<lon>/historical?years=N` with N ∈ [1,10]
  - Response:
    - `years_analyzed: number`
    - `per_year: Array<{ year: number, monthly: { [Month]: number }, annual_rainfall: number }>`
    - `monthly_averages: { [Month]: { average_rainfall: number } }` (existing)
    - `multi_year: { annual_average: number, monthly_average: { [Month]: number } }`
  - Errors: 400 for invalid N; 502/504 for upstream issues; 500 with safe message.
- Auth: none (public weather data).
- Events/Storage: none; on‑disk cache retained; no PII.
- Migrations: none.

## 5) Non‑Functional Requirements (NFRs)
- Performance: ≤ 800 ms for 1–5 years; ≤ 1.5 s for 10 years when cached.
- Reliability: 10 s timeout; 2 retries with backoff; idempotent reads.
- Security: Validate inputs; sanitize logs; least privilege on filesystem.
- Privacy/Compliance: No personal data stored.
- Observability: Structured logs with lat/lon/years; counters for cache hit/miss and multi‑year usage; trace spans around provider call and aggregation.
- Accessibility & i18n: Preserve current semantics; ensure accordions are keyboard accessible; keep labels externalizable for future locales.

## 6) Validation Plan (Before Coding)
- Spikes: Verify provider returns stable daily rainfall across multi‑year windows for Lilongwe coordinates; confirm monthly name mapping.
- Test Vectors:
  - Good: N=1,3,5 for lat −13.9833, lon 33.7833; months with nonzero rainfall.
  - Bad: N=0, N=11, non‑numeric; extreme lat/lon.
  - Boundary: February in leap year; months with zero rainfall.
- Manual QA:
  1. N=3, verify latest year expanded; toggle older years; numbers consistent.
  2. N=1, ensure no accordion.
  3. Offline/network failure shows error notice.
- Automated Tests:
  - Backend unit/integration: verify mean calculations and schema.
  - Frontend unit: accordion rendering, toggle behavior, numeric formatting.
  - E2E: path from selection to rendered accordions and average labeling.

## 7) Technical Implementation Plan
- Milestones & Tasks:
  1. Add backend averaging and extend response with `per_year` and `multi_year`.
  2. Implement UI with year accordions; show multi‑year summary; default expand latest.
  3. Tests: backend unit/integration and frontend unit/E2E.
  4. Documentation updates (runbook, API sections).
- Acceptance Criteria:
  - Given N=3, Then annual figure is average, not sum; per‑year accordions appear; latest expanded.
  - Existing `monthly_averages` remains present and correct.
- Owner & Reviewers: Owner – you; Reviewer – AI assistant.
- Estimates & Risks: Low‑moderate complexity; risks include provider outages, edge month mapping.

## 8) Best Practices Block
- Security: Validate/normalize inputs; enforce numeric limits; avoid secrets in logs.
- Performance & Reliability: Caching, timeouts, retries; avoid re‑computation across identical windows.
- Code Quality: Small functions for grouping/averaging; keep response building isolated; guard clauses.
- Observability: Contextual logs with correlation IDs; metrics for request counts and durations.
- Accessibility & UX: Semantically correct accordions; clear labels and states.

## 9) Rollout, Monitoring & Revert
- Feature Flag: `WEATHER_MULTIYEAR_UI` (frontend); backend is additive.
- Dashboards/Alerts: Error rate of historical endpoint > 2%; latency p95 > 1.5 s.
- Runbooks: If provider fails, serve cached data where available; surface partial data.
- Revert Plan: Disable UI flag to hide accordions; backend remains backward compatible.

## 10) Definition of Done (DoD)
- ≥ 80% relevant test coverage for new logic; all tests green.
- Observability added; no sensitive info in logs.
- Docs updated (this plan, API notes, QA steps).
- Feature flag documented; follow‑up cleanup ticket created.

---

## API Examples

### Explicit Years Request
- Request:
```
GET /api/weather/-13.9833,33.7833/historical?years_list=2025,2024,2023
```
- Response (shape):
```json
{
  "years_analyzed": 3,
  "per_year": [
    {"year": 2025, "annual_rainfall": 608.0, "monthly": {"January": 517.3}, "months_covered": 10, "coverage": "partial"},
    {"year": 2024, "annual_rainfall": 606.0, "monthly": {"January": 277.8}, "months_covered": 12, "coverage": "full"},
    {"year": 2023, "annual_rainfall": 132.0, "monthly": {"January": 0.0}, "months_covered": 3, "coverage": "partial"}
  ],
  "monthly_averages": {"January": {"average_rainfall": 265.0}},
  "multi_year": {
    "annual_average": 448.7,
    "monthly_average": {"January": 265.0}
  },
  "meta": {"failed_years": []}
}
```

### Debug Endpoint (Dev Only)
- Request:
```
GET /api/_debug/openmeteo-sum?lat=-13.9833&lon=33.7833&year=2024
```
- Response:
```json
{
  "year": 2024,
  "lat": -13.9833,
  "lon": 33.7833,
  "daily_count": 366,
  "total_rainfall_mm": 606.0,
  "source": "Open-Meteo Archive (ERA5)",
  "note": "Dev-only debug endpoint for data integrity checks"
}
```

## E2E Tests (Playwright)
```ts
// tests/e2e/weather-multiyear.spec.ts
import { test, expect } from '@playwright/test'

async function openHistoricalTab(page) {
  await page.getByText('Historical').click()
}

test('multi-year selection shows latest year expanded and correct averages', async ({ page }) => {
  await page.goto('http://localhost:5173')
  await openHistoricalTab(page)

  await page.getByLabel('Years to Analyze').click()
  await page.getByRole('option', { name: '3 Years' }).click()
  await page.getByRole('button', { name: 'Generate Results' }).click()

  await expect(page.getByText('Visual Trends')).toBeVisible()

  const currentYear = new Date().getFullYear()
  await expect(page.getByRole('button', { name: String(currentYear) })).toHaveAttribute('aria-expanded', 'true')
  await expect(page.getByRole('button', { name: String(currentYear - 1) })).toHaveAttribute('aria-expanded', 'false')
  await expect(page.getByRole('button', { name: String(currentYear - 2) })).toHaveAttribute('aria-expanded', 'false')

  await expect(page.getByText(/Annual Rainfall.*average/i)).toBeVisible()
})

test('single-year selection shows no accordions', async ({ page }) => {
  await page.goto('http://localhost:5173')
  await openHistoricalTab(page)

  await page.getByLabel('Years to Analyze').click()
  await page.getByRole('option', { name: '1 Year' }).click()
  await page.getByRole('button', { name: 'Generate Results' }).click()

  await expect(page.getByText('Monthly Rainfall Breakdown')).toBeVisible()
  const prevYear = String(new Date().getFullYear() - 1)
  await expect(page.getByRole('button', { name: prevYear })).toHaveCount(0)
})
```

## Backend Unit Tests (Sketch)
```python
# tests/test_historical_averaging.py
import math

def mean(values):
    return sum(values) / len(values)

def test_multi_year_annual_average_is_mean(client):
    resp = client.get('/api/weather/-13.9833,33.7833/historical?years=3')
    data = resp.get_json()
    per_year = data['per_year']
    expected = mean([y['annual_rainfall'] for y in per_year])
    assert math.isclose(data['multi_year']['annual_average'], expected, rel_tol=1e-6)

def test_multi_year_monthly_average_is_mean(client):
    resp = client.get('/api/weather/-13.9833,33.7833/historical?years=3')
    data = resp.get_json()
    months = ['January','February','March','April','May','June','July','August','September','October','November','December']
    for m in months:
        per_year_vals = [y['monthly'].get(m, 0) for y in data['per_year']]
        expected = mean(per_year_vals)
        assert m in data['multi_year']['monthly_average']
        assert math.isclose(data['multi_year']['monthly_average'][m], expected, rel_tol=1e-6)
```

## Cleanup & Follow‑Ups
- Remove any legacy sum‑based UI labels once fully rolled out.
- Consolidate duplicated month name utilities if found.
- Ensure Windows console logging avoids unsupported emojis (seen in `api_server.py` load_config print).
