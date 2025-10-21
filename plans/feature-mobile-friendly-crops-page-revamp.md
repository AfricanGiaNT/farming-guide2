# Feature Plan – Mobile-Friendly Crops Page Revamp

**Status:** In Progress  
**Created:** 2025-10-21  
**Priority:** High  
**Target:** Mobile users (primary), Desktop (minor responsive tweaks)

---

## Brief

The crops page currently suffers from mobile usability issues: oversized headers, complex coordinate inputs, inconsistent text sizing, and excessive scrolling. We're redesigning it to prioritize mobile users with a focus on the rainy season, immediate access to top 3 crop recommendations, integrated historical rainfall data, and simplified navigation. Success means users can quickly find crop recommendations and variety information with minimal scrolling and clear, attractive presentation.

---

## Scope

### Use Cases
- User opens crops page on mobile → sees top 3 recommendations immediately with rainfall context
- User changes location using simplified location picker (like Weather page)
- User searches for specific crop → gets detailed info including common varieties
- User views historical rainfall for previous farm season
- User clicks crop card → navigates to varieties page with context
- Advanced users expand menu for season comparison and filters

### Out of Scope
- Desktop redesign (only minor responsive tweaks)
- Adding new crop recommendation algorithms
- Backend API changes (use existing)
- Multi-language support (future phase)

### Dependencies
- Weather data API (historical rainfall)
- Existing location picker component from Weather page
- Crop recommendations API
- Varieties page routing

---

## Workflow

### Happy Path
1. User opens crops page on mobile
2. Page loads with user's location (or default Lilongwe)
3. Top section shows: compact location badge + historical rainfall summary for previous rainy season
4. Immediately below: 3 best crop cards (large, attractive, with emoji icons)
5. Each card shows: crop name, suitability score, top 3 varieties, "View Details" button
6. User taps a crop card → navigates to varieties page with pre-filled crop & location
7. User scrolls down to see "View All Recommendations" expandable section
8. User can tap "Advanced Options" menu for season comparison, filters, search

### Variants
- **Variant A (Location Change):** User taps location badge → simplified location picker modal opens (like Weather) → selects location → page refreshes with new data
- **Variant B (Crop Search):** User taps search icon in header → search modal opens → enters crop name → sees filtered results
- **Variant C (Season Switch):** User taps "Advanced Options" → season tabs appear → switches season → recommendations update

### Edge Cases
1. No GPS permission → use default Lilongwe coordinates
2. API failure fetching rainfall data → show cached data or hide rainfall section
3. No recommendations for location → show empty state with suggestion to try different location
4. Slow network → show skeleton loaders for cards
5. Search returns no results → show "No crops found" with suggestions
6. Historical rainfall unavailable → show message "Historical data unavailable for this location"
7. Too many recommendations (>20) → paginate with "Load More" button instead of showing all

### State Changes
- `location`: { lat, lon } - updates trigger data refetch
- `selectedSeason`: 'rainy' (default) | 'dry' | 'current' | 'all'
- `showAdvancedOptions`: boolean - toggles advanced menu
- `recommendations`: array - filtered based on search/season
- `historicalRainfall`: object - previous season rainfall data
- `loading`: boolean - shows skeleton loaders
- `error`: string | null - shows error alert

### Error UX
- Network errors → "Unable to load recommendations. Check your connection." + Retry button
- Location errors → "Location unavailable. Using default Lilongwe."
- Rainfall data errors → Hide rainfall section gracefully (no error shown)
- Search errors → "Search unavailable. Try again later."

---

## Data & Interfaces

### Entities & Fields

**HistoricalRainfall:**
```typescript
{
  season_start: string        // ISO date
  season_end: string          // ISO date
  total_rainfall: number      // mm
  monthly_breakdown: Array<{
    month: string
    rainfall: number
  }>
  years_analyzed: number
}
```

**SimplifiedCropCard:**
```typescript
{
  crop_name: string           // required
  suitability_score: number   // 0-100, required
  top_varieties: string[]     // max 3
  crop_emoji: string
  quick_description: string   // max 100 chars
  link_to_varieties: string   // URL
}
```

### API Contracts

**GET /api/recommendations/top-crops**
- Query params: `lat`, `lon`, `season` (default: 'rainy'), `limit` (default: 3)
- Response: 200
  ```json
  {
    "recommendations": [
      {
        "crop_name": "Maize",
        "score": 85,
        "top_varieties": ["SC627", "DK8031", "PHB30G19"],
        "description": "High yield potential with good drought tolerance"
      }
    ]
  }
  ```
- Errors: 500 (server error), 404 (no recommendations)

**GET /api/weather/historical-rainfall**
- Query params: `lat`, `lon`, `season_year` (e.g., '2024-rainy')
- Response: 200
  ```json
  {
    "season": "2024 Rainy Season",
    "total_rainfall": 850,
    "period": "Nov 2024 - Apr 2025",
    "years_analyzed": 5
  }
  ```

**Events:** None

**Migrations:** None (using existing APIs)

---

## NFRs

### Performance
- Page load: < 2s on 3G
- Top 3 cards render: < 1s
- Location change: < 1.5s to show new recommendations
- Image/emoji rendering: instant (use Unicode emojis, no images)

### Reliability
- Retry failed API calls 2x with exponential backoff
- Cache recommendations for 5 minutes (reduce API calls)
- Graceful degradation if rainfall data unavailable

### Security
- Sanitize location inputs (prevent injection)
- Validate coordinates are within Malawi bounds (-9° to -17° lat, 32° to 36° lon)
- Rate limit: max 60 requests/minute per IP

### Observability
- Log location changes with coordinates
- Track which crops users click most (analytics)
- Monitor API failure rates
- Log search queries for improvement insights

### Accessibility
- ARIA labels on all interactive elements
- Keyboard navigation for modals and cards
- High contrast text (WCAG AA minimum)
- Touch targets ≥ 44x44px

### i18n
- Keep all text in English for now
- Use locale-aware number formatting (e.g., 850mm)

---

## Validation & Tests

### Manual QA Scenarios
1. Open page on iPhone SE → verify top 3 cards visible without scrolling
2. Change location via modal → verify recommendations update
3. Tap crop card → verify navigates to varieties page with correct params
4. Search for "maize" → verify results filter correctly
5. Toggle advanced options → verify season tabs appear/hide smoothly
6. Disable network → verify error state shows with retry button
7. Test on slow 3G → verify skeleton loaders show appropriately

### Automated Tests
- **Unit:** Component rendering (cards, modals, headers)
- **Integration:** API data fetching and state updates
- **E2E:** Full user flow (location change → view crops → navigate to varieties)

---

## Technical Implementation Plan

### Milestone 1: Simplify Page Header & Location Input
**Duration:** 2-3 hours  
**Status:** Pending

**Tasks:**
- [ ] Task 1.1: Replace large header with compact version (Typography variant="h5")
- [ ] Task 1.2: Extract LocationPicker from Weather page into shared component
- [ ] Task 1.3: Create location badge with tap-to-edit functionality
- [ ] Task 1.4: Add location modal with simplified coordinate input
- [ ] Task 1.5: Wire up location changes to refetch recommendations

**Acceptance Criteria:**
- User can tap location badge → modal opens → enter coordinates → recommendations update

---

### Milestone 2: Historical Rainfall Integration
**Duration:** 3-4 hours  
**Status:** Pending

**Tasks:**
- [ ] Task 2.1: Create API endpoint/hook for historical rainfall data
- [ ] Task 2.2: Design compact rainfall summary card (mobile-optimized)
- [ ] Task 2.3: Integrate weather service for previous rainy season data
- [ ] Task 2.4: Add error handling and caching for rainfall data
- [ ] Task 2.5: Position rainfall card below location, above crop cards

**Acceptance Criteria:**
- Page shows previous rainy season rainfall (e.g., "2024 Rainy Season: 850mm") with graceful fallback if unavailable

---

### Milestone 3: Redesign Top 3 Crop Cards
**Duration:** 2-3 hours  
**Status:** Pending

**Tasks:**
- [ ] Task 3.1: Create `SimplifiedCropCard` component (mobile-first)
- [ ] Task 3.2: Add large emoji icons for visual appeal
- [ ] Task 3.3: Show suitability score prominently (large number + progress bar)
- [ ] Task 3.4: Display top 3 varieties as chips below crop name
- [ ] Task 3.5: Add "View Details" button that navigates to varieties page
- [ ] Task 3.6: Implement card animations (subtle hover/tap effects)

**Acceptance Criteria:**
- Top 3 cards are visually attractive, show key info, and navigate to varieties page on tap

---

### Milestone 4: Consolidate Advanced Options
**Duration:** 2 hours  
**Status:** Pending

**Tasks:**
- [ ] Task 4.1: Create collapsible "Advanced Options" section
- [ ] Task 4.2: Move season tabs into advanced section
- [ ] Task 4.3: Move crop search into advanced section
- [ ] Task 4.4: Move risk assessment, management tips into expandable sections
- [ ] Task 4.5: Add "View All Recommendations" expandable list

**Acceptance Criteria:**
- Main page shows only top 3 cards by default; advanced options hidden behind menu

---

### Milestone 5: Improve Search & Filters
**Duration:** 1-2 hours  
**Status:** Pending

**Tasks:**
- [ ] Task 5.1: Redesign search input (single field with icon)
- [ ] Task 5.2: Simplify button layout (use icon buttons where possible)
- [ ] Task 5.3: Add search modal for mobile (full-screen overlay)
- [ ] Task 5.4: Implement instant search filtering

**Acceptance Criteria:**
- Search is clean, intuitive, and works smoothly on mobile

---

### Milestone 6: Text Consistency & Mobile Polish
**Duration:** 1-2 hours  
**Status:** Pending

**Tasks:**
- [ ] Task 6.1: Standardize font sizes (use theme typography variants consistently)
- [ ] Task 6.2: Reduce vertical spacing on mobile (remove excessive padding)
- [ ] Task 6.3: Ensure all touch targets are ≥ 44px
- [ ] Task 6.4: Test on multiple mobile devices (iPhone SE, Android mid-range)
- [ ] Task 6.5: Fix any layout bugs or overflow issues

**Acceptance Criteria:**
- Page has consistent text sizing, minimal scrolling, and works well on all mobile devices

---

### Milestone 7: Testing & Refinement
**Duration:** 1-2 hours  
**Status:** Pending

**Tasks:**
- [ ] Task 7.1: Write component tests for new components
- [ ] Task 7.2: Update integration tests
- [ ] Task 7.3: Perform manual QA on mobile devices
- [ ] Task 7.4: Fix any bugs found during testing
- [ ] Task 7.5: Update documentation

**Acceptance Criteria:**
- All tests pass; page works smoothly on mobile; documentation updated

---

## Best Practices

### Security
- Validate location coordinates on both client and server
- Sanitize all user inputs (search queries, coordinates)
- Use environment variables for API keys

### Performance
- Lazy load "View All" recommendations list
- Debounce search input (300ms delay)
- Cache API responses for 5 minutes
- Use React.memo for crop cards to prevent unnecessary re-renders

### Code Quality
- Extract reusable components (LocationBadge, SimplifiedCropCard, RainfallSummary)
- Use TypeScript interfaces for all data structures
- Keep components single-purpose and under 300 lines
- Use MUI theme for consistent spacing/colors

### Observability
- Log location changes and search queries
- Track click events on crop cards (which crops are most popular)
- Monitor API response times and failure rates

### Accessibility
- Add ARIA labels to all buttons and interactive elements
- Ensure keyboard navigation works for modals
- Test with screen reader (at least basic manual test)

---

## Rollout & Revert

### Feature Flag Strategy
- No feature flag needed (small UI change, low risk)
- Deploy to staging first for internal testing
- If issues arise, can quickly revert via git

### Monitoring
- Watch error rates in logs after deployment
- Monitor user engagement (click-through rates to varieties page)
- Check mobile analytics for bounce rates

### Revert Plan
- Git revert if critical issues arise
- Fallback: temporarily redirect /crops to old version (if needed)

---

## Definition of Done

- [ ] Top 3 crop cards render immediately on mobile without scrolling
- [ ] Location input simplified (uses Weather page approach)
- [ ] Historical rainfall data integrated and displayed
- [ ] All crop cards link to varieties page with correct parameters
- [ ] Advanced options hidden behind collapsible menu
- [ ] Text sizing is consistent across page
- [ ] Search functionality redesigned and simplified
- [ ] All tests passing (unit, integration, manual mobile QA)
- [ ] Page loads in < 2s on 3G
- [ ] Desktop version still works (minor responsive tweaks only)
- [ ] Documentation updated
- [ ] Code reviewed and approved

---

## Cleanup (post-merge)

- [ ] Remove old complex coordinate input component (if not used elsewhere)
- [ ] Delete unused state variables
- [ ] Clean up any commented-out code
- [ ] Consolidate duplicate styling
- [ ] Update README if needed

---

## Post-Implementation Review

**Will be completed after implementation...**

**Feature/Change:** Mobile-friendly crops page revamp

**Initial Solution Plan:** Simplify mobile UI, integrate historical rainfall, prioritize top 3 recommendations

**What We Implemented:** _[To be filled in]_

**Issues Faced:** _[To be filled in]_

**Potential Side Effects / Unknowns:** _[To be filled in]_

**Follow-ups/Tickets:** _[To be filled in]_

---

## Investigation Results ✅

### 1. Weather Location Picker Reusability ✅
**Status:** ✅ **CAN BE REUSED**

**Findings:**
- `SimplifiedLocationInput` component exists in `src/components/Weather/SimplifiedLocationInput.tsx`
- Already mobile-optimized with responsive design
- Supports GPS location and Google Maps URL parsing
- Has proper error handling and loading states
- **Action:** Extract to `src/components/Location/SimplifiedLocationInput.tsx` for reuse

### 2. Historical Rainfall Endpoint ✅
**Status:** ✅ **EXISTS**

**Findings:**
- `weatherAPI.getHistoricalWeather()` exists in `src/services/api.ts`
- `useHistoricalWeather()` hook available in `src/hooks/useWeatherData.ts`
- Supports multiple years: `getHistoricalWeather(lat, lon, yearsOrList)`
- Returns monthly averages and historical data
- **Action:** Use existing endpoint, no new API needed

### 3. Varieties Page Routing ✅
**Status:** ✅ **CONFIRMED**

**Findings:**
- Varieties page expects URL params: `?crop={cropName}&lat={lat}&lon={lon}`
- Uses `useSearchParams()` to parse parameters
- Current crops page already uses this format: `window.location.href = \`/varieties?crop=${crop.crop_name}&lat=${currentLocation.lat}&lon=${currentLocation.lon}\``
- **Action:** Use existing navigation pattern

### 4. Previous Farm Season Definition ✅
**Status:** ✅ **CLARIFIED**

**User Confirmation:** "last completed season"

**Implementation:**
- For 2025: Use 2024 rainy season data (Nov 2024 - Apr 2025)
- Calculate previous season: Current year - 1 for rainy season
- **Action:** Use `getHistoricalWeather(lat, lon, [2024])` for previous season data

---

## Updated Technical Implementation

### Milestone 1: Simplify Page Header & Location Input
**Duration:** 2-3 hours  
**Status:** Ready to Start

**Updated Tasks:**
- [ ] Task 1.1: Replace large header with compact version (Typography variant="h5")
- [ ] Task 1.2: Move `SimplifiedLocationInput` from Weather to shared Location folder
- [ ] Task 1.3: Create location badge with tap-to-edit functionality
- [ ] Task 1.4: Add location modal using existing `SimplifiedLocationInput` component
- [ ] Task 1.5: Wire up location changes to refetch recommendations

**Acceptance Criteria:**
- User can tap location badge → modal opens → enter coordinates/GPS → recommendations update

### Milestone 2: Historical Rainfall Integration
**Duration:** 2-3 hours (reduced from 3-4 hours)
**Status:** Ready to Start

**Updated Tasks:**
- [ ] Task 2.1: Use existing `useHistoricalWeather(lat, lon, [previousYear])` hook
- [ ] Task 2.2: Design compact rainfall summary card (mobile-optimized)
- [ ] Task 2.3: Calculate previous rainy season year (current year - 1)
- [ ] Task 2.4: Add error handling for historical data (graceful fallback)
- [ ] Task 2.5: Position rainfall card below location, above crop cards

**Acceptance Criteria:**
- Page shows "2024 Rainy Season: 850mm" with graceful fallback if unavailable

### Milestone 3: Redesign Top 3 Crop Cards
**Duration:** 2-3 hours  
**Status:** Ready to Start

**Updated Tasks:**
- [ ] Task 3.1: Create `SimplifiedCropCard` component (mobile-first)
- [ ] Task 3.2: Add large emoji icons for visual appeal
- [ ] Task 3.3: Show suitability score prominently (large number + progress bar)
- [ ] Task 3.4: Display top 3 varieties as chips below crop name
- [ ] Task 3.5: Add "View Details" button that navigates to `/varieties?crop=${cropName}&lat=${lat}&lon=${lon}`
- [ ] Task 3.6: Implement card animations (subtle hover/tap effects)

**Acceptance Criteria:**
- Top 3 cards are visually attractive, show key info, and navigate to varieties page on tap

---

## Plan Critique (Updated)

### Strengths
- ✅ All dependencies confirmed and available
- ✅ No new API endpoints needed
- ✅ Existing components can be reused
- ✅ Clear navigation pattern established
- ✅ Mobile-first design approach

### Resolved Issues
- ✅ Weather location picker confirmed reusable
- ✅ Historical rainfall API exists and works
- ✅ Varieties page routing format confirmed
- ✅ Previous farm season definition clarified

### Ready to Proceed
All investigation gaps resolved. Implementation can begin immediately with Milestone 1.

