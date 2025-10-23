# Step-by-Step Guide: One-Crop-At-A-Time Variety Extraction

## Overview
This guide follows the successful maize extraction approach to systematically extract varieties from all crops in Chapter 3 of the Guide to Agriculture Production in Malawi 2021.

## Prerequisites
- ✅ Database schema updated with additional columns (originator, grain_color, grain_texture, ecology, table_source)
- ✅ Maize extraction completed successfully (59 varieties)
- ✅ PDF file: "Guide to Agriculture Production in Malawi 2021.pdf"

## Step-by-Step Process

### Phase 1: Preparation
1. **Clear varieties table** (if needed)
2. **Identify crop sections** in Chapter 3
3. **Create crop-specific extractor** template

### Phase 2: For Each Crop (Repeat Process)

#### Step 1: Analyze Crop Section
```bash
# Run analysis script to find variety tables
python scripts/analyze_crop_section.py --crop <crop_name>
```

**What to look for:**
- Table numbers (e.g., "Table 23", "Table 30")
- Variety subheadings
- Page ranges containing crop content
- Table structure (columns: Variety, Originator, Type, etc.)

#### Step 2: Create Crop-Specific Extractor
```bash
# Copy and modify the maize extractor template
cp scripts/structured_maize_extractor.py scripts/structured_<crop>_extractor.py
```

**Modify these sections:**
- Crop name and page ranges
- Table identification logic
- Column mapping (if different from maize)
- Validation rules (if needed)

#### Step 3: Test Extraction (Preview Mode)
```bash
# Run extractor in preview mode (no database insertion)
python scripts/structured_<crop>_extractor.py --preview
```

**Verify:**
- Correct variety names extracted
- Proper originator information
- Accurate days to maturity
- Correct yield information
- No garbage data

#### Step 4: Execute Full Extraction
```bash
# Run full extraction with database insertion
python scripts/structured_<crop>_extractor.py
```

#### Step 5: Verify Results
```bash
# Check for duplicates and data quality
python scripts/check_duplicates.py --crop <crop_name>
```

#### Step 6: Document Results
- Record number of varieties extracted
- Note any issues or special cases
- Update crop completion status

## Crop Priority List

### High Priority (Known Variety Tables)
1. **Rice** - Table 23 (Page 170)
2. **Groundnut** - Table 30 (Page 192)  
3. **Cassava** - Table 42 (Page 220)
4. **Potato** - Table 46 (Page 227)
5. **Tobacco** - Variety tables (Page 242)

### Medium Priority (Likely Variety Tables)
6. **Soybean** - Check pages 195-210
7. **Sweet Potato** - Check pages 224-235
8. **Sunflower** - Check pages 214-225
9. **Sesame** - Check pages 216-225

### Lower Priority (Text-Based Varieties)
10. **Sorghum** - Pages 175-180
11. **Wheat** - Pages 181-185
12. **Beans** - Pages 184-195
13. **Cowpea** - Pages 204-215
14. **Cotton** - Pages 265-280
15. **Tomato** - Pages 322-330

## Template Files to Create

### 1. Crop Analysis Script
```python
# scripts/analyze_crop_section.py
# Analyzes a specific crop section to find variety tables
```

### 2. Crop-Specific Extractor Template
```python
# scripts/structured_crop_extractor_template.py
# Template for creating crop-specific extractors
```

### 3. Batch Verification Script
```python
# scripts/verify_all_crops.py
# Verifies all extracted crops for duplicates and quality
```

## Quality Standards

### Data Validation Rules
- ✅ Variety names: 2-50 characters, contains letters
- ✅ Originator: Company/organization name
- ✅ Type: Hybrid, OPV, etc.
- ✅ Days to maturity: Numeric value
- ✅ Yield: Contains "t/ha" or similar unit
- ❌ Reject: Measurements, locations, chemical names

### Success Criteria
- **Accuracy**: 95%+ of extracted varieties are genuine
- **Completeness**: All varieties from tables extracted
- **Uniqueness**: No duplicate varieties
- **Structure**: All required fields populated

## Troubleshooting Guide

### Common Issues
1. **No varieties found**
   - Check page ranges
   - Verify table structure
   - Look for different table formats

2. **Garbage data extracted**
   - Tighten validation rules
   - Check column mapping
   - Review table structure

3. **Missing varieties**
   - Check for multi-variety cells
   - Look for text-based variety lists
   - Verify table boundaries

4. **Database insertion errors**
   - Check column names
   - Verify data types
   - Handle special characters

## Progress Tracking

### Completion Checklist
- [ ] Rice varieties extracted
- [ ] Groundnut varieties extracted  
- [ ] Cassava varieties extracted
- [ ] Potato varieties extracted
- [ ] Tobacco varieties extracted
- [ ] Soybean varieties extracted
- [ ] Sweet Potato varieties extracted
- [ ] Sunflower varieties extracted
- [ ] Sesame varieties extracted
- [ ] All crops verified for duplicates
- [ ] Final quality report generated

## Next Steps

1. **Start with Rice** (highest priority)
2. **Follow the step-by-step process**
3. **Document each crop's results**
4. **Maintain quality standards**
5. **Complete all crops systematically**

## Success Metrics
- **Target**: 200+ total varieties across all crops
- **Quality**: 95%+ accuracy rate
- **Coverage**: All major crops in Chapter 3
- **Structure**: Complete variety information for each crop

---

**Ready to begin with Rice extraction!**
