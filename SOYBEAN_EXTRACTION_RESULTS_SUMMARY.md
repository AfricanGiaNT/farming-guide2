# Soybean Variety Extraction Results Summary

## Overview
Successfully extracted soybean varieties from the Guide to Agriculture Production in Malawi 2021, following the same successful approach used for groundnut extraction.

## Extraction Sources
- **Table 32**: 10 varieties with detailed descriptions, maturity periods, agro-ecologies, and special attributes
- **Section 3.2.4.2**: Improved varieties with detailed descriptions (2 additional varieties)
- **Section 3.2.4.7**: Fertilizer recommendations and application methods

## Results
- **Total varieties extracted**: 11 unique varieties
- **Successfully inserted**: 10 varieties
- **Failed**: 1 duplicate ("Ocepara 4" already existed)

## Varieties Successfully Inserted
1. **Ocepara-4** - Indeterminate, medium to late maturity (120-140 days), resistant to root-knot nematodes
2. **Nasoko** - Determinate, medium to late maturity (120-140 days), widely adapted
3. **Makwacha** - Indeterminate, medium to late maturity (120-140 days), strong logging resistance
4. **Solitaire** - Medium to late maturity (120-140 days), tolerant to frogeye disease
5. **Soprano** - Early to medium maturity (110-120 days), large seeded
6. **Tikolore** - Early maturity (90-110 days), promiscuous (may not require inoculation)
7. **SC Serenade** - Early to medium maturity (110-120 days), indeterminate growth
8. **PAN 1867** - Early maturing (110-120 days), indeterminate growth
9. **SC Squire** - Medium to late maturity (120-140 days), tolerant to Soya Bean Rust
10. **SC Sequel** - Medium to late maturity (120-140 days), high yielding, tolerant to Soya Bean Rust

## Information Extracted
- **Variety names** from Table 32 and detailed sections
- **Growth habits** (Indeterminate vs Determinate)
- **Maturity periods** (90-140 days range)
- **Yield potential** (2500-4000 kg/ha)
- **Agro-ecological adaptations** (low to high altitude areas)
- **Special attributes** (disease resistance, seed characteristics)
- **Fertilizer recommendations** from section 3.2.4.7

## Database Fields Used
- `crop_id`: 58 (soybean)
- `crop_name`: 'soybean'
- `variety_name`: Variety name
- `originator`: Source material (DARS, SeedCo, Pannar Seeds, etc.)
- `type`: Growth habit (Indeterminate/Determinate)
- `yield_potential`: Yield information
- `table_source`: Source table/section
- `source_document`: 'Guide to Agriculture Production in Malawi 2021'
- `extraction_confidence`: 0.9
- `harvesting_guidelines`: Maturity periods and special attributes
- `fertilizer_requirements`: Fertilizer application information

## Key Features
- **Comprehensive extraction** from Table 32 and detailed text sections
- **Detailed variety information** including growth habits, maturity periods, yield potential
- **Agro-ecological information** for proper variety selection
- **Disease resistance information** (root-knot nematodes, Soya Bean Rust, frogeye disease)
- **Fertilizer management** including rhizobium inoculation options
- **Proper deduplication** to avoid duplicate entries

## Fertilizer Information Extracted
- **Three application options**: Rhizobium only, fertilizer only, or both
- **Rhizobium inoculants**: Nitrofix, Biofix, Histick
- **Fertilizer rates**: 200 kg of 23:10:5+6S+1.0Zn per hectare
- **Application methods**: Banding, timing recommendations
- **High yield targets**: 3000-4000 kg per hectare

## Next Steps
The soybean variety extraction is complete and successful. The database now contains comprehensive soybean variety information that can be used for:
- Crop recommendations based on agro-ecological zones
- Management guidance for different maturity groups
- Yield expectations and potential
- Disease resistance information
- Fertilizer application recommendations
- Rhizobium inoculation guidance

## Files Created
- `scripts/structured_soybean_extractor.py`: Main extraction script
- `scripts/check_and_add_soybean_crop.py`: Crop verification script
- `scripts/analyze_soybean_section_detailed.py`: Section analysis script
- `scripts/find_soybean_table_32_and_sections.py`: Table and section locator
