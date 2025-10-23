# Varieties Database & Page Implementation Plan

## Overview
Create a comprehensive varieties database and detailed page that provides farmers with complete information about specific crop varieties, including farming processes, rainfall requirements, harvest timelines, and all essential agricultural knowledge extracted from available PDFs.

## Project Status
- **Current Phase**: Planning & Design
- **Start Date**: October 21, 2025
- **Target Completion**: 4 weeks
- **Progress**: 0% Complete

---

## Brief
Create a comprehensive varieties database and detailed page that provides farmers with complete information about specific crop varieties, including farming processes, rainfall requirements, harvest timelines, and all essential agricultural knowledge extracted from available PDFs. This will serve as the ultimate resource page when users click on recommended crops.

## Scope

### Use Cases (Ranked by Importance):
1. **Primary**: User clicks recommended crop → Redirects to varieties page with complete crop/variety information
2. **Secondary**: Direct navigation to varieties page via URL parameters
3. **Tertiary**: Search/filter varieties within a specific crop
4. **Quaternary**: Compare multiple varieties side-by-side
5. **Quinary**: Export variety information for offline reference

### Out of Scope:
- Real-time weather integration on varieties page (keep it focused on static knowledge)
- User reviews/ratings system
- Social sharing features
- Mobile app integration (web-first approach)

### Dependencies:
- Existing PDF documents (agriculture guide + additional PDFs)
- Current crop recommendation system
- Database infrastructure (SQLite/PostgreSQL)
- PDF parsing capabilities
- Vector search system for information extraction

### Constraints:
- Must work with existing database structure
- Should leverage current PDF processing pipeline
- Performance: Page load < 3 seconds
- Mobile-responsive design required

---

## Workflow

### Happy Path:
1. User views crop recommendations
2. User clicks on specific crop card
3. System redirects to `/varieties?crop={crop_name}&lat={lat}&lon={lon}`
4. Varieties page loads with:
   - Crop overview and general information
   - Available varieties for that crop
   - Detailed farming process for each variety
   - Rainfall requirements, harvest timelines, etc.
   - All information extracted from PDFs

### Variants:
- **Variant A**: Direct URL access to varieties page
- **Variant B**: Search within varieties page
- **Variant C**: Mobile-optimized view

### Edge Cases:
- Crop not found in database
- No varieties available for crop
- PDF extraction fails for specific crop
- Network timeout during data loading
- Invalid coordinates in URL
- Missing crop parameter
- PDFs contain conflicting information
- Large variety datasets causing slow loading

---

## Data & Interfaces

### Entities & Fields:

**Crops Table:**
- `id` (primary key)
- `crop_name` (string, required)
- `scientific_name` (string, optional)
- `local_name` (string, optional)
- `category` (string: grain, legume, tuber, etc.)
- `general_description` (text)
- `overview_image_url` (string, optional)

**Varieties Table:**
- `id` (primary key)
- `crop_id` (foreign key to crops)
- `variety_name` (string, required)
- `type` (string: hybrid, open_pollinated, etc.)
- `maturity_days` (integer)
- `drought_tolerance` (string: excellent, good, moderate, poor)
- `disease_resistance` (array of strings)
- `yield_potential` (string: high, medium, low)
- `planting_months` (array of strings)
- `harvest_months` (array of strings)
- `min_rainfall_mm` (integer)
- `max_rainfall_mm` (integer)
- `optimal_temperature_min` (float)
- `optimal_temperature_max` (float)
- `soil_requirements` (text)
- `spacing_requirements` (text)
- `fertilizer_requirements` (text)
- `pest_management` (text)
- `disease_management` (text)
- `harvesting_guidelines` (text)
- `storage_requirements` (text)
- `source_document` (string: PDF filename)
- `extraction_confidence` (float: 0-1)

**Farming Processes Table:**
- `id` (primary key)
- `variety_id` (foreign key to varieties)
- `process_type` (string: land_preparation, planting, maintenance, harvesting)
- `step_number` (integer)
- `step_description` (text)
- `timing` (string)
- `tools_required` (array of strings)
- `notes` (text)

### API Contracts:

**GET /api/varieties/{crop_name}**
- Request: `crop_name` (path param), `lat`, `lon` (query params)
- Response: Complete crop and varieties data
- Status codes: 200 (success), 404 (crop not found), 500 (server error)

**GET /api/varieties/{crop_name}/{variety_name}**
- Request: `crop_name`, `variety_name` (path params)
- Response: Detailed variety information
- Status codes: 200, 404, 500

---

## Non-Functional Requirements

### Performance:
- Page load time < 3 seconds
- Database queries < 500ms
- PDF extraction caching for 24 hours

### Reliability:
- Graceful fallback when PDF data unavailable
- Retry mechanism for failed extractions
- Data validation for extracted information

### Security:
- Input validation for crop/variety names
- SQL injection prevention
- Rate limiting on API endpoints

### Observability:
- Log extraction success/failure rates
- Monitor page load times
- Track user navigation patterns

---

## Validation Plan

### Proof of Concept:
1. Extract varieties data from agriculture guide PDF
2. Create basic database schema
3. Build simple varieties page
4. Test with 2-3 crops (maize, beans, cassava)

### Test Vectors:
- Valid crop names: "maize", "beans", "cassava"
- Invalid crop names: "invalid_crop", ""
- Edge cases: crops with no varieties, conflicting data

### Manual QA Scenarios:
1. Click maize recommendation → Verify varieties page loads
2. Check all variety information displays correctly
3. Verify mobile responsiveness
4. Test direct URL access

---

## Technical Implementation Plan

### Milestones & Tasks:

#### **Milestone 1: Data Extraction Pipeline (Week 1)**
- [x] Task 1.1: Enhance PDF parser to extract varieties data
- [x] Task 1.2: Create data extraction scripts for agriculture guide
- [x] Task 1.3: Design database schema for crops/varieties
- [x] Task 1.4: Implement data validation and cleaning

#### **Milestone 2: Database & API (Week 2)**
- [ ] Task 2.1: Create database tables and migrations
- [ ] Task 2.2: Implement varieties API endpoints
- [ ] Task 2.3: Add data seeding scripts
- [ ] Task 2.4: Create data quality validation

#### **Milestone 3: Varieties Page Frontend (Week 3)**
- [ ] Task 3.1: Design varieties page layout
- [ ] Task 3.2: Implement crop overview section
- [ ] Task 3.3: Build varieties listing component
- [ ] Task 3.4: Add detailed variety information display

#### **Milestone 4: Integration & Testing (Week 4)**
- [ ] Task 4.1: Integrate crop recommendations → varieties navigation
- [ ] Task 4.2: Implement mobile-responsive design
- [ ] Task 4.3: Add error handling and loading states
- [ ] Task 4.4: Performance optimization and testing

### Acceptance Criteria (per milestone):

**Milestone 1:**
- Given: Agriculture guide PDF
- When: Running extraction script
- Then: Should extract varieties data for at least 5 crops with >80% accuracy

**Milestone 2:**
- Given: Extracted varieties data
- When: API endpoints are called
- Then: Should return structured data in <500ms

**Milestone 3:**
- Given: Varieties page URL
- When: User navigates to page
- Then: Should display complete crop and variety information

**Milestone 4:**
- Given: Crop recommendation page
- When: User clicks crop card
- Then: Should redirect to varieties page with correct data

---

## Best Practices

### Security:
- Validate all crop/variety names before database queries
- Use parameterized queries to prevent SQL injection
- Implement rate limiting on extraction endpoints

### Performance:
- Cache extracted PDF data for 24 hours
- Use database indexes on crop_name and variety_name
- Implement pagination for crops with many varieties

### Code Quality:
- Modular extraction scripts for different PDF types
- Comprehensive error handling for PDF parsing failures
- Clear separation between data extraction and presentation layers

### Observability:
- Log extraction success rates by PDF source
- Monitor API response times
- Track user engagement with varieties page

---

## Rollout & Monitoring

### Feature Flag Strategy:
- Phase 1: Internal testing with 2-3 crops
- Phase 2: Beta release with agriculture guide data
- Phase 3: Full rollout with all PDF sources

### Dashboards/Alerts:
- Extraction success rate >90%
- Page load time <3 seconds
- API error rate <1%

### Revert Plan:
- Disable varieties page navigation
- Fallback to existing crop recommendation cards
- Maintain database integrity during rollback

---

## Definition of Done

- [ ] All acceptance criteria met and tests passing
- [ ] Varieties page loads in <3 seconds
- [ ] Mobile-responsive design implemented
- [ ] Error handling for missing/invalid data
- [ ] Documentation updated (API docs, user guide)
- [ ] Performance monitoring configured
- [ ] Demo recorded showing complete user journey

---

## Cleanup (Post-Merge)

- [ ] Remove temporary extraction scripts
- [ ] Consolidate duplicate PDF parsing logic
- [ ] Optimize database queries
- [ ] Update API documentation
- [ ] Close tracking issues

---

## Post-Implementation Review

### Implemented vs Planned:
- Will document actual implementation vs planned approach
- Note any deviations or compromises made

### Issues Faced:
- PDF parsing accuracy challenges
- Database performance optimization needs
- Mobile layout complexity

### Side Effects/Unknowns:
- Impact on existing crop recommendation performance
- Database storage requirements
- User adoption patterns

### Follow-ups:
- Additional PDF sources integration
- User feedback collection
- Performance optimization based on usage

---

## Progress Log

### Week 1 Progress:
- [x] Started planning and design phase
- [x] Created comprehensive implementation plan
- [x] Identified key dependencies and constraints
- [x] Created comprehensive varieties parser
- [x] Designed complete database schema
- [x] Implemented AI-powered extraction
- [x] Created test suite and validation
- [x] Set up extraction pipeline
- [x] **COMPLETED**: Targeted Chapter 3 extraction from agriculture guide
- [x] **COMPLETED**: Fixed database schema issues (variety_type column, category constraints)
- [x] **COMPLETED**: Successfully extracted 55 crops and 2,361 varieties from Chapter 3

### Extraction Results Summary:
- **Source**: Guide to Agriculture Production in Malawi 2021, Chapter 3
- **Crops Extracted**: 55 crops across all categories (cereals, legumes, tubers, vegetables, fruits, spices, etc.)
- **Varieties Extracted**: 2,361 variety entries
- **Database**: Fully functional SQLite database with proper schema
- **Status**: ✅ **COMPLETED** - Database ready, API endpoints functional, enhanced frontend components created

### Week 2 Progress:
- [x] **COMPLETED**: Enhanced variety display component with rich information format
- [x] **COMPLETED**: Created comprehensive variety detail cards showing production timelines, input requirements, and farming processes
- [x] **COMPLETED**: Updated varieties page with enhanced UI and better crop selection
- [x] **COMPLETED**: Integrated database with existing API endpoints
- [ ] **IN PROGRESS**: Testing and refinement of variety information display

### Week 3 Progress:
- [ ] TBD

### Week 4 Progress:
- [ ] TBD

---

## Notes & Decisions

### Key Decisions Made:
1. **Database Choice**: Continue with SQLite for simplicity, can migrate to PostgreSQL later
2. **PDF Processing**: Leverage existing PDF parsing infrastructure
3. **UI Framework**: Use existing Material-UI components for consistency

### Open Questions:
1. How to handle conflicting information from different PDF sources?
2. Should we implement variety comparison feature in Phase 1?
3. What's the optimal caching strategy for extracted data?

### Risks & Mitigation:
- **Risk**: PDF extraction accuracy may be low
- **Mitigation**: Manual validation and correction process
- **Risk**: Database performance with large variety datasets
- **Mitigation**: Implement proper indexing and pagination

---

**Last Updated**: October 21, 2025
**Next Review**: October 28, 2025
