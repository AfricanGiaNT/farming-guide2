# Feature Plan – Weather-Based Crop Recommendations

## 1) One‑Paragraph Brief

We will enable users to receive intelligent, data-driven crop recommendations based on analyzed historical weather patterns. After the system analyzes multi-year rainfall data, it will provide an "Agricultural Implications" section showing: suitable crops for wet and dry seasons, rainfall variability indicators, drought/flood risk assessment, and actionable planting advice. This replaces generic weather visualizations with practical farming guidance. Success means farmers can make informed crop selection decisions based on their region's actual weather patterns, leading to better yield outcomes and reduced climate risk.

## 2) Clarify Intent & Scope (Q&A)

1. **Problem & Goal**: Farmers see weather data but don't know what crops suit their conditions. Goal: translate weather patterns into actionable crop recommendations.
2. **Actors & Personas**: Smallholder farmers in Lilongwe, Malawi; agricultural extension workers; web UI users.
3. **Primary Use Cases**:
   - View suitable crops for identified wet/dry seasons
   - Understand rainfall reliability and what it means for crop choices
   - See drought/flood risk years and plan accordingly
   - Get specific planting month recommendations based on seasonal patterns
4. **Out‑of‑Scope**: Soil analysis integration, market prices, pest predictions, individual farm-level customization, real-time weather alerts.
5. **Definition of Success**: Users see clear crop recommendations after historical weather analysis; recommendations align with agricultural best practices for Malawi; farmers report actionable insights.
6. **Dependencies**: Historical weather API data; crop database with water requirements; existing weather analysis infrastructure.
7. **Constraints**: Limited to rainfall-based analysis initially; mobile-first UI; works offline after initial load.
8. **Environment Impact**: No new services; enhances existing weather page; cache recommendations with weather data.
9. **Backward Compatibility**: Additive feature; existing weather views remain functional.
10. **Risks/Unknowns**: Accuracy of crop-weather mappings; regional variations within Lilongwe district; user trust in automated recommendations; need for agronomist validation.

## 3) Map the Workflow

### Happy Path:
1. User generates historical weather analysis (1-10 years)
2. System calculates rainfall patterns: totals, variability, seasonal distribution, extreme events
3. System identifies wet season (>100mm/month average) and dry season months
4. System calculates rainfall variability percentage
5. System counts drought years (<400mm annual) and flood years (>1200mm annual)
6. Backend matches patterns to crop database and returns recommendations
7. UI renders "Agricultural Implications" section with:
   - Wet season suitable crops
   - Dry season suitable crops
   - Rainfall variability indicator (Low/Medium/High)
   - Extreme events summary (drought/flood years)
   - Actionable warnings/advice
8. User sees practical farming guidance based on their selected location and time period

### Variants:
- **Variant A**: High variability (>30%) → emphasize drought-resistant crops and risk warnings
- **Variant B**: Low variability (<20%) → emphasize reliable crops and season predictability
- **Variant C**: Multiple extreme events → highlight climate adaptation strategies
- **Variant D**: Single year analysis → show recommendations with "limited data" disclaimer

### Edge Cases:
- No clear wet/dry season distinction (semi-arid regions)
- All months below crop viability thresholds
- Insufficient historical data (<1 year)
- Extreme climate years skewing averages
- Missing crop database entries
- Network failure during crop matching
- User location outside Malawi region
- Conflicting crop requirements vs. available rainfall
- Leap year date handling
- Zero rainfall months affecting seasonal calculations

### State Changes & Invariants:
- Weather data fetched → analysis computed → crop recommendations generated
- Invariant: Wet season must have ≥3 consecutive months >100mm
- Invariant: Recommendations only shown when years_analyzed ≥ 1
- Cache key: lat,lon,years,analysis_version

### Error UX:
- Insufficient data: "Need at least 1 full year of data for crop recommendations"
- No suitable crops: "Rainfall patterns suggest consulting local extension officer for specialized advice"
- API failure: "Could not load crop recommendations. Weather data still available."
- Generic errors: Show weather data, hide recommendations section gracefully

## 4) Data & Interfaces

### Entities:
- **CropRecommendation**:
  - `crop_name` (string, required)
  - `local_name` (string, optional, Chichewa)
  - `water_requirement` (string: "low"|"medium"|"high")
  - `suitable_season` (string: "wet"|"dry"|"year-round")
  - `min_rainfall_mm` (number)
  - `max_rainfall_mm` (number)
  - `planting_months` (array of month names)
  - `days_to_harvest` (number)
  - `notes` (string, optional)

- **AgriculturalAnalysis**:
  - `wet_season_months` (array of month names)
  - `dry_season_months` (array of month names)
  - `rainfall_variability_pct` (number)
  - `variability_level` (string: "Low"|"Medium"|"High")
  - `drought_years` (number)
  - `flood_years` (number)
  - `recommended_wet_crops` (array of CropRecommendation)
  - `recommended_dry_crops` (array of CropRecommendation)
  - `warnings` (array of strings)
  - `advice` (array of strings)

### API Contract (Additive):

**Request**:
```
GET /api/weather/<lat>,<lon>/agricultural-recommendations?years=N
```

**Response**:
```json
{
  "years_analyzed": 3,
  "agricultural_implications": {
    "wet_season": {
      "months": ["November", "December", "January", "February", "March", "April"],
      "average_monthly_rainfall": 185.5,
      "suitable_crops": [
        {
          "crop_name": "Maize",
          "local_name": "Chimanga",
          "water_requirement": "medium",
          "planting_months": ["November", "December"],
          "days_to_harvest": 120,
          "notes": "Main staple crop for Malawi"
        },
        {
          "crop_name": "Beans",
          "local_name": "Nyemba",
          "water_requirement": "medium",
          "planting_months": ["December", "January"],
          "days_to_harvest": 90
        }
      ]
    },
    "dry_season": {
      "months": ["May", "June", "July", "August", "September", "October"],
      "average_monthly_rainfall": 8.3,
      "suitable_crops": [
        {
          "crop_name": "Sweet Potato",
          "local_name": "Mbatata",
          "water_requirement": "low",
          "planting_months": ["August", "September"],
          "days_to_harvest": 105
        }
      ]
    },
    "variability": {
      "percentage": 25.0,
      "level": "Low",
      "interpretation": "Rainfall is relatively predictable. Plan for both drought and excess water scenarios."
    },
    "extreme_events": {
      "drought_years": 2,
      "flood_years": 1,
      "total_years_analyzed": 3
    },
    "warnings": [
      "⚠️ High rainfall variability. Plan for both drought and excess water scenarios."
    ],
    "advice": [
      "Consider drought-resistant varieties",
      "Prepare water conservation strategies"
    ]
  }
}
```

**Errors**:
- 400: Invalid parameters (lat/lon/years)
- 404: Crop database not available
- 422: Insufficient weather data for recommendations
- 500: Internal analysis error
- 502/504: Upstream weather API issues

### Auth:
- None (public agricultural data)

### Events/Storage:
- Cache recommendations with weather data (TTL: 7 days)
- Log recommendation requests for analytics
- Track crop recommendation usage metrics

### Migrations:
- Add crop database table (if not exists)
- Seed initial Malawi crop data
- No changes to existing weather tables

## 5) Non‑Functional Requirements (NFRs)

- **Performance**: Crop analysis adds ≤200ms to weather endpoint; client-side rendering of recommendations ≤100ms
- **Reliability**: Recommendations fail gracefully; weather data always displays; retry crop matching once on failure
- **Security**: Validate crop database entries; sanitize user inputs; no injection via crop names
- **Privacy/Compliance**: No personal farming data collected; anonymous usage analytics only
- **Observability**: Log recommendation generation success/failure; track crop types requested; monitor analysis latency
- **Accessibility**: Screen-reader friendly crop lists; keyboard navigation for expandable sections; sufficient color contrast for warning indicators
- **Internationalization**: Support Chichewa crop names; externalize season labels; prepare for future language expansion

## 6) Validation Plan (Before Coding)

### Spikes:
- Validate crop-rainfall mappings with Malawi agricultural extension data
- Test seasonal detection algorithm with historical Lilongwe data
- Confirm variability calculation matches agronomist expectations

### Test Vectors:

**Good Inputs**:
- Lilongwe coords (-13.9833, 33.7833), 3 years → clear wet/dry seasons
- High rainfall year → includes flood-tolerant crop warnings
- Low rainfall year → drought-resistant crop emphasis

**Bad Inputs**:
- Invalid coordinates (extreme lat/lon)
- Years = 0 or negative
- Non-numeric parameters
- Location with no historical data

**Boundary Cases**:
- Exactly 100mm threshold months
- Zero rainfall dry season
- All months equal rainfall (no seasonality)
- Single year with partial data

### Manual QA Scenarios:

1. **Standard Flow**:
   - Generate 3-year analysis for Lilongwe
   - Verify wet season shows maize, beans, rice
   - Verify dry season shows sweet potato, cassava
   - Check variability indicator matches calculation
   - Confirm drought/flood years are counted correctly

2. **Edge Cases**:
   - Single year → verify "limited data" disclaimer
   - High variability (>30%) → verify enhanced warnings
   - Network failure → verify graceful degradation

3. **Mobile UX**:
   - Tap to expand crop details
   - Scroll through recommendations smoothly
   - Warning messages display clearly

### Automated Tests:

**Backend Unit**:
- Seasonal detection algorithm (wet vs dry)
- Variability calculation (coefficient of variation)
- Extreme event counting logic
- Crop matching by rainfall requirements
- Error handling for missing data

**Backend Integration**:
- Full API response shape validation
- Cache hit/miss scenarios
- Crop database queries
- Weather + crop data combination

**Frontend Unit**:
- Render agricultural implications section
- Display crops grouped by season
- Show variability indicators correctly
- Handle missing crop fields gracefully

**E2E**:
- Generate weather analysis → see crop recommendations
- Verify crop names and local names display
- Check planting months are highlighted
- Confirm warnings appear for extreme patterns

## 7) Technical Implementation Plan

### Milestones & Tasks:

**Milestone 1: Backend Analysis Engine**
- Task 1.1: Implement seasonal detection algorithm
  - Input: monthly rainfall averages
  - Output: wet_season_months, dry_season_months
  - Logic: consecutive months >100mm = wet season
- Task 1.2: Implement variability calculator
  - Formula: (std_dev / mean) * 100
  - Classify: <20% Low, 20-30% Medium, >30% High
- Task 1.3: Implement extreme event counter
  - Drought: annual <400mm
  - Flood: annual >1200mm (or >300mm single month)
- Task 1.4: Create crop matching logic
  - Match crop water requirements to seasonal rainfall
  - Filter by planting months within suitable seasons
- Task 1.5: Add `/api/weather/<lat>,<lon>/agricultural-recommendations?years=N` endpoint
- Task 1.6: Integrate with existing weather pipeline

**Acceptance Criteria (M1)**:
- Given 3 years data, endpoint returns wet/dry season months
- Variability calculation matches manual computation
- Crop recommendations include maize, beans for Lilongwe wet season
- Response time <500ms (including weather fetch)

**Milestone 2: Crop Database Setup**
- Task 2.1: Design crop schema (SQLite table)
- Task 2.2: Seed Malawi crop data (maize, beans, rice, cassava, sweet potato, groundnuts, sorghum, millet)
- Task 2.3: Add Chichewa translations
- Task 2.4: Validate with agricultural extension guidelines

**Acceptance Criteria (M2)**:
- Database contains ≥8 Malawi crops
- Each crop has water requirements and planting months
- Queries return crops in <50ms

**Milestone 3: UI Components**
- Task 3.1: Create `AgriculturalImplications.tsx` component
- Task 3.2: Build `SuitableCrops.tsx` subcomponent
- Task 3.3: Build `VariabilityIndicator.tsx` subcomponent
- Task 3.4: Build `ExtremeEvents.tsx` subcomponent
- Task 3.5: Integrate into Weather page after "Visual Trends"
- Task 3.6: Style for mobile-first responsiveness
- Task 3.7: Add loading and error states

**Acceptance Criteria (M3)**:
- UI renders after weather analysis completes
- Crops grouped by wet/dry season
- Variability shows color-coded badge
- Warnings display with warning icon
- Mobile: touches expand/collapse details

**Milestone 4: Testing & Validation**
- Task 4.1: Backend unit tests (>80% coverage)
- Task 4.2: Frontend unit tests
- Task 4.3: Integration tests
- Task 4.4: E2E Playwright tests
- Task 4.5: Manual QA with various locations/years
- Task 4.6: Agronomist review (if available)

**Acceptance Criteria (M4)**:
- All tests green
- No regressions in existing weather features
- Recommendations validated against known Malawi crops
- Performance benchmarks met

**Milestone 5: Documentation & Rollout**
- Task 5.1: API documentation
- Task 5.2: Update README with feature description
- Task 5.3: Create runbook for crop database updates
- Task 5.4: Add feature flag `ENABLE_CROP_RECOMMENDATIONS`
- Task 5.5: Deploy to dev/staging
- Task 5.6: Production rollout

**Acceptance Criteria (M5)**:
- Feature flag functional
- Docs complete
- Monitoring dashboards show recommendation usage
- Zero critical errors in production

### Owner & Reviewers:
- Owner: Development team
- Reviewers: AI assistant, agricultural advisor (optional)

### Estimates & Risks:

**Estimates**:
- M1: 3-4 days
- M2: 1-2 days
- M3: 2-3 days
- M4: 2-3 days
- M5: 1 day
- **Total: ~9-13 days**

**Risks**:
- Crop-weather mappings may not match real-world Malawi conditions → Mitigation: consult agricultural extension data
- Users may not trust automated recommendations → Mitigation: add disclaimers, show data sources
- Regional variations within Malawi → Mitigation: start with general Lilongwe area, plan for district-level refinement
- Crop database maintenance burden → Mitigation: design for easy CSV import/export

## 8) Best Practices Block

### Security:
- Validate all inputs (lat/lon bounds, year ranges)
- Sanitize crop names and notes from database
- Prevent SQL injection in crop queries
- No sensitive data in logs (crop choices are not personal)

### Performance & Reliability:
- Cache recommendations alongside weather data
- Async crop matching (don't block weather response)
- Timeout on crop queries (fallback to weather-only view)
- Lazy load crop details on UI

### Code Quality:
- Separate concerns: weather analysis, crop matching, UI rendering
- Pure functions for seasonal detection and variability
- Reusable crop query utilities
- Type-safe interfaces for CropRecommendation and AgriculturalAnalysis

### Observability:
- Log recommendation generation attempts and failures
- Metric: `crop_recommendations_generated` counter
- Metric: `crop_matching_latency` histogram
- Trace spans: seasonal_detection, crop_query, recommendation_build
- Track most frequently recommended crops

### Accessibility & UX:
- Semantic HTML (proper headings hierarchy)
- ARIA labels for expandable sections
- Color-blind friendly variability indicators
- Clear, jargon-free language
- Icons with text labels (not icons alone)
- Mobile: thumb-friendly tap targets

## 9) Rollout, Monitoring & Revert

### Feature Flag Strategy:
- `ENABLE_CROP_RECOMMENDATIONS` (default: false)
- Phase 1: Internal testing only
- Phase 2: Enable for 10% of users
- Phase 3: Full rollout if metrics are positive

### Dashboards/Alerts:
- Dashboard: Crop Recommendation Usage
  - Request count
  - Crops recommended (top 10)
  - Error rate
  - Latency p50/p95/p99
- Alert: Recommendation error rate >5% for 5 minutes
- Alert: Latency p95 >500ms for 10 minutes
- Alert: Crop database query failures >10/min

### Runbooks:
- **Issue**: Recommendations not appearing
  - Check: Feature flag enabled?
  - Check: Crop database accessible?
  - Check: Weather API returning data?
  - Action: Review logs for error messages
  
- **Issue**: Wrong crop recommendations
  - Check: Seasonal detection logic (wet/dry thresholds)
  - Check: Crop database water requirements
  - Action: Verify with agricultural data sources

- **Issue**: Slow response times
  - Check: Crop query performance
  - Check: Cache hit rate
  - Action: Add indexes, optimize queries

### Revert Plan:
- Quick: Disable feature flag (removes UI section)
- Medium: Remove recommendation API endpoint (keep weather working)
- Full: Roll back deployment (if database issues)
- No data migrations to reverse

## 10) Definition of Done (DoD)

- [ ] All milestones (1-5) complete with acceptance criteria met
- [ ] ≥80% test coverage for new backend logic
- [ ] ≥75% test coverage for new frontend components
- [ ] All tests passing in CI
- [ ] Observability: logs, metrics, traces added
- [ ] No sensitive data in logs or error messages
- [ ] Security review complete (input validation, query safety)
- [ ] Accessibility: keyboard navigation, screen reader tested
- [ ] Mobile UX verified on iOS and Android
- [ ] API documentation updated
- [ ] README updated with feature description
- [ ] Runbook created for common issues
- [ ] Feature flag documented and functional
- [ ] Deployed to staging and verified
- [ ] Performance benchmarks met (<500ms total)
- [ ] No regressions in existing weather features
- [ ] Agronomist review (optional but recommended)
- [ ] Demo recorded or screenshots captured
- [ ] Cleanup ticket created for post-rollout optimization

---

## API Response Example

```json
{
  "years_analyzed": 3,
  "agricultural_implications": {
    "wet_season": {
      "months": ["November", "December", "January", "February", "March", "April"],
      "average_monthly_rainfall_mm": 185.5,
      "total_season_rainfall_mm": 1113.0,
      "suitable_crops": [
        {
          "crop_name": "Maize",
          "local_name": "Chimanga",
          "water_requirement": "medium",
          "planting_months": ["November", "December"],
          "days_to_harvest": 120,
          "min_rainfall_mm": 500,
          "max_rainfall_mm": 1200,
          "notes": "Main staple crop. Choose drought-tolerant varieties in uncertain years."
        },
        {
          "crop_name": "Beans (Common)",
          "local_name": "Nyemba",
          "water_requirement": "medium",
          "planting_months": ["December", "January"],
          "days_to_harvest": 90,
          "min_rainfall_mm": 400,
          "max_rainfall_mm": 900
        },
        {
          "crop_name": "Rice",
          "local_name": "Mpunga",
          "water_requirement": "high",
          "planting_months": ["November", "December"],
          "days_to_harvest": 150,
          "min_rainfall_mm": 800,
          "max_rainfall_mm": 2000,
          "notes": "Requires consistent water. Best in low-lying areas."
        }
      ]
    },
    "dry_season": {
      "months": ["May", "June", "July", "August", "September", "October"],
      "average_monthly_rainfall_mm": 8.3,
      "total_season_rainfall_mm": 50.0,
      "suitable_crops": [
        {
          "crop_name": "Sweet Potato",
          "local_name": "Mbatata",
          "water_requirement": "low",
          "planting_months": ["August", "September"],
          "days_to_harvest": 105,
          "min_rainfall_mm": 250,
          "max_rainfall_mm": 750,
          "notes": "Excellent dry-season option. Stores well."
        },
        {
          "crop_name": "Cassava",
          "local_name": "Chinangwa",
          "water_requirement": "low",
          "planting_months": ["September", "October"],
          "days_to_harvest": 240,
          "min_rainfall_mm": 400,
          "max_rainfall_mm": 800,
          "notes": "Drought-tolerant. Long maturity but reliable."
        }
      ]
    },
    "variability": {
      "percentage": 25.0,
      "level": "Low",
      "interpretation": "Rainfall is relatively predictable across years.",
      "coefficient_of_variation": 0.25
    },
    "extreme_events": {
      "drought_years": 2,
      "flood_years": 1,
      "total_years_analyzed": 3,
      "drought_threshold_mm": 400,
      "flood_threshold_mm": 1200
    },
    "warnings": [
      "⚠️ High rainfall variability. Plan for both drought and excess water scenarios."
    ],
    "advice": [
      "Consider planting drought-resistant maize varieties",
      "Prepare water conservation strategies (mulching, ridging)",
      "Diversify crops to spread risk",
      "Monitor early-season rainfall before committing to water-intensive crops"
    ]
  }
}
```

## UI Component Structure

```
<AgriculturalImplications>
  <SectionHeader>Agricultural Implications</SectionHeader>
  
  <WetSeasonCrops season="wet" crops={...} />
    → List of crop cards with names, planting months, water needs
  
  <DrySeasonCrops season="dry" crops={...} />
    → List of crop cards
  
  <VariabilityIndicator level="Low" percentage={25} />
    → Badge with color coding + interpretation
  
  <ExtremeEvents droughtYears={2} floodYears={1} total={3} />
    → Visual indicator of climate risks
  
  <WarningsAndAdvice warnings={[...]} advice={[...]} />
    → Actionable guidance with icons
</AgriculturalImplications>
```

## Backend Seasonal Detection Algorithm

```python
def detect_seasons(monthly_averages: dict[str, float]) -> dict:
    """
    Identify wet and dry seasons based on monthly rainfall averages.
    
    Logic:
    - Wet season: consecutive months with >100mm average rainfall
    - Dry season: all other months
    """
    WET_THRESHOLD_MM = 100
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    wet_months = []
    dry_months = []
    
    for month in month_order:
        rainfall = monthly_averages.get(month, 0)
        if rainfall > WET_THRESHOLD_MM:
            wet_months.append(month)
        else:
            dry_months.append(month)
    
    return {
        'wet_season_months': wet_months,
        'dry_season_months': dry_months,
        'wet_season_avg_rainfall': sum(monthly_averages[m] for m in wet_months) / len(wet_months) if wet_months else 0,
        'dry_season_avg_rainfall': sum(monthly_averages[m] for m in dry_months) / len(dry_months) if dry_months else 0
    }
```

## Crop Database Schema

```sql
CREATE TABLE IF NOT EXISTS crops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crop_name TEXT NOT NULL,
    local_name_chichewa TEXT,
    water_requirement TEXT CHECK(water_requirement IN ('low', 'medium', 'high')),
    suitable_season TEXT CHECK(suitable_season IN ('wet', 'dry', 'year-round')),
    min_rainfall_mm INTEGER NOT NULL,
    max_rainfall_mm INTEGER NOT NULL,
    planting_months TEXT NOT NULL, -- JSON array of month names
    days_to_harvest INTEGER NOT NULL,
    notes TEXT,
    region TEXT DEFAULT 'malawi',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data
INSERT INTO crops (crop_name, local_name_chichewa, water_requirement, suitable_season, 
                   min_rainfall_mm, max_rainfall_mm, planting_months, days_to_harvest, notes)
VALUES 
    ('Maize', 'Chimanga', 'medium', 'wet', 500, 1200, 
     '["November", "December"]', 120, 'Main staple crop for Malawi'),
    ('Beans', 'Nyemba', 'medium', 'wet', 400, 900, 
     '["December", "January"]', 90, 'Good protein source'),
    ('Sweet Potato', 'Mbatata', 'low', 'dry', 250, 750, 
     '["August", "September"]', 105, 'Drought-tolerant, stores well'),
    ('Cassava', 'Chinangwa', 'low', 'year-round', 400, 800, 
     '["September", "October", "November"]', 240, 'Very drought-resistant'),
    ('Rice', 'Mpunga', 'high', 'wet', 800, 2000, 
     '["November", "December"]', 150, 'Requires consistent water'),
    ('Groundnuts', 'Mtedza', 'medium', 'wet', 500, 1000, 
     '["November", "December"]', 120, 'Nitrogen-fixing crop'),
    ('Sorghum', 'Mapira', 'low', 'wet', 400, 700, 
     '["November", "December"]', 110, 'More drought-tolerant than maize'),
    ('Millet', 'Mawere', 'low', 'wet', 350, 650, 
     '["November", "December"]', 90, 'Short season, drought-tolerant');
```

## E2E Test (Playwright)

```typescript
// tests/e2e/crop-recommendations.spec.ts
import { test, expect } from '@playwright/test'

test('displays agricultural implications after weather analysis', async ({ page }) => {
  await page.goto('http://localhost:5173')
  
  // Navigate to Historical weather
  await page.getByText('Historical').click()
  
  // Generate 3-year analysis
  await page.getByLabel('Years to Analyze').click()
  await page.getByRole('option', { name: '3 Years' }).click()
  await page.getByRole('button', { name: 'Generate Results' }).click()
  
  // Wait for results to load
  await expect(page.getByText('Agricultural Implications')).toBeVisible({ timeout: 10000 })
  
  // Verify wet season section
  await expect(page.getByText('Wet Season:')).toBeVisible()
  await expect(page.getByText(/November.*December.*January/)).toBeVisible()
  
  // Verify suitable crops appear
  await expect(page.getByText('Maize')).toBeVisible()
  await expect(page.getByText('Chimanga')).toBeVisible() // Local name
  
  // Verify dry season section
  await expect(page.getByText('Dry Season:')).toBeVisible()
  await expect(page.getByText('Sweet Potato')).toBeVisible()
  
  // Verify variability indicator
  await expect(page.getByText(/Variability/i)).toBeVisible()
  await expect(page.getByText(/Low|Medium|High/)).toBeVisible()
  
  // Verify extreme events
  await expect(page.getByText(/Drought Years/i)).toBeVisible()
  await expect(page.getByText(/Flood Years/i)).toBeVisible()
  
  // Verify warnings/advice section exists
  await expect(page.getByText(/⚠️|warnings|advice/i)).toBeVisible()
})

test('handles missing crop recommendations gracefully', async ({ page }) => {
  // Mock API to return weather data but no crops
  await page.route('**/api/weather/**/agricultural-recommendations*', route => {
    route.fulfill({
      status: 200,
      body: JSON.stringify({
        years_analyzed: 1,
        agricultural_implications: null,
        error: 'Insufficient data for crop recommendations'
      })
    })
  })
  
  await page.goto('http://localhost:5173')
  await page.getByText('Historical').click()
  await page.getByRole('button', { name: 'Generate Results' }).click()
  
  // Should still show weather data
  await expect(page.getByText('Visual Trends')).toBeVisible()
  
  // Should not crash
  await expect(page.getByText('Error')).not.toBeVisible()
})
```

## Backend Unit Tests

```python
# tests/test_crop_recommendations.py
import pytest
from scripts.crop_advisor.seasonal_detector import detect_seasons, calculate_variability
from scripts.crop_advisor.crop_matcher import match_crops_to_season

def test_seasonal_detection_identifies_wet_months():
    monthly_avg = {
        'January': 250, 'February': 200, 'March': 150,
        'April': 80, 'May': 20, 'June': 5,
        'July': 0, 'August': 0, 'September': 10,
        'October': 50, 'November': 150, 'December': 220
    }
    
    result = detect_seasons(monthly_avg)
    
    assert 'January' in result['wet_season_months']
    assert 'February' in result['wet_season_months']
    assert 'July' in result['dry_season_months']
    assert len(result['wet_season_months']) >= 4

def test_variability_calculation():
    annual_totals = [800, 750, 900, 700, 850]
    
    result = calculate_variability(annual_totals)
    
    assert 'percentage' in result
    assert 'level' in result
    assert 0 <= result['percentage'] <= 100
    assert result['level'] in ['Low', 'Medium', 'High']

def test_crop_matching_returns_appropriate_crops():
    season_data = {
        'average_rainfall_mm': 600,
        'season': 'wet'
    }
    
    crops = match_crops_to_season(season_data)
    
    assert len(crops) > 0
    assert all(c['suitable_season'] in ['wet', 'year-round'] for c in crops)
    assert all(c['min_rainfall_mm'] <= 600 <= c['max_rainfall_mm'] for c in crops)

def test_extreme_event_counting():
    annual_totals = [350, 800, 1300, 600, 380]  # 2 droughts, 1 flood
    
    result = count_extreme_events(annual_totals, drought_threshold=400, flood_threshold=1200)
    
    assert result['drought_years'] == 2
    assert result['flood_years'] == 1
    assert result['total_years'] == 5
```

## Cleanup & Follow‑Ups

### Post-Rollout Tasks:
- [ ] Monitor recommendation accuracy via user feedback
- [ ] Gather user testimonials on usefulness
- [ ] Expand crop database with more varieties
- [ ] Add district-level customization
- [ ] Integrate soil type data (Phase 2)
- [ ] Add market price integration (Phase 3)
- [ ] Localize fully to Chichewa
- [ ] Create offline-first PWA version
- [ ] Partner with agricultural extension for validation

### Code Cleanup:
- [ ] Remove any debug console logs
- [ ] Consolidate duplicate crop query utilities
- [ ] Optimize seasonal detection algorithm if needed
- [ ] Document crop database update procedures
- [ ] Create admin UI for crop management (future)

---

## Post‑Implementation Review (Template)

**Feature/Change**: Weather-Based Crop Recommendations

**Initial Solution Plan**: 
- Analyze historical rainfall to identify wet/dry seasons
- Match crop water requirements to seasonal patterns
- Display actionable recommendations in UI

**What We Implemented**:
- [To be filled after implementation]

**Issues Faced**:
- [To be filled after implementation]

**Potential Side Effects / Unknowns**:
- Users may over-rely on automated recommendations
- Regional variations may not be fully captured
- Crop database requires ongoing maintenance

**Follow‑ups/Tickets**:
- [To be created during implementation]

---

## Success Metrics

### Leading Indicators:
- Recommendation requests per day
- Average time viewing recommendations section
- Crop detail expansion rate

### User Outcomes:
- User report: "This helped me decide what to plant" (survey/feedback)
- Repeat usage of feature (weekly active users)
- Session duration on weather page increases

### Business/Impact KPIs:
- Farmer yield improvements (long-term, survey-based)
- Adoption rate among extension workers
- Reduction in crop failure due to unsuitable choices (anecdotal)

### Data Quality:
- Recommendation generation success rate (>95%)
- Crop database coverage (all major Malawi crops)
- API response time (<500ms p95)

