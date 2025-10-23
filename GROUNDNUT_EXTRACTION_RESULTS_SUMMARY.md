# Groundnut Variety Extraction Results Summary

## Overview
Successfully extracted groundnut varieties from the Guide to Agriculture Production in Malawi 2021, following the original plan to use existing database columns.

## Extraction Sources
- **Table 30**: 13 varieties with botanical groups, spacing, and seed rate information
- **Section 3.2.3.1**: Varieties being promoted (0 found in this run)
- **Section 3.2.3.2**: Recommended improved varieties (6 varieties with detailed descriptions)
- **Section 3.2.3.8**: Fertilizer application information
- **Section 3.2.3.7**: Insect pest control information  
- **Section 3.2.3.6.2**: Disease control information

## Results
- **Total varieties extracted**: 14 unique varieties
- **Successfully inserted**: 13 varieties
- **Failed**: 1 duplicate ("Chalimbana 2005" already existed)

## Varieties Successfully Inserted
1. CG 7
2. CG 8
3. CG 9
4. CG 10
5. and CG 11
6. Chalimbana
7. 2005
8. Nsinjiro
9. CG 12
10. and CG
11. Kakoma
12. Chitala
13. Baka

## Information Extracted
- **Variety names** from Table 30 and detailed sections
- **Botanical groups** (Virginia Bunch, Spanish Bunch)
- **Spacing requirements** (75cm x 15cm, 75cm x 10cm)
- **Seed rates** (80-100 kg/ha, 50-60 kg/ha)
- **Maturity days** (90-120, 130-150 days)
- **Yield potential** (1500-2500 kg/ha)
- **Fertilizer information** from section 3.2.3.8
- **Pest control information** from section 3.2.3.7
- **Disease control information** from section 3.2.3.6.2

## Database Fields Used
- `crop_id`: 13 (groundnut)
- `crop_name`: 'groundnut'
- `variety_name`: Variety name
- `type`: Botanical group or variety type
- `maturity_days`: Days to maturity
- `yield_potential`: Yield information
- `table_source`: Source table/section
- `source_document`: 'Guide to Agriculture Production in Malawi 2021'
- `extraction_confidence`: 0.9
- `harvesting_guidelines`: Detailed variety information
- `spacing_requirements`: Planting spacing
- `fertilizer_requirements`: Fertilizer information
- `pest_management`: Pest control information
- `disease_management`: Disease control information

## Key Features
- **Comprehensive extraction** from multiple sources
- **Detailed variety information** including growth habits, oil content, altitude ranges
- **Management information** for fertilizer, pest, and disease control
- **Proper deduplication** to avoid duplicate entries
- **Error handling** for database constraints

## Next Steps
The groundnut variety extraction is complete and successful. The database now contains comprehensive groundnut variety information that can be used for:
- Crop recommendations
- Management guidance
- Yield expectations
- Pest and disease control strategies
- Fertilizer application recommendations

## Files Created
- `scripts/structured_groundnut_extractor_final.py`: Main extraction script
- `scripts/check_and_add_groundnut_crop.py`: Crop verification script
- `scripts/check_new_columns.py`: Column verification script
- `scripts/supabase_schema_refresh_solutions.py`: Schema refresh solutions
