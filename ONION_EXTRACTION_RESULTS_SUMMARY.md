# Onion Variety Extraction Results Summary

## Overview
Successfully extracted onion varieties from the Guide to Agriculture Production in Malawi 2021, following the same successful approach used for groundnut, soybean, sunflower, cassava, and tomato extraction.

## Extraction Sources
- **Section 3.10.5.1**: Recommended varieties section
- **Section 3.10.5.1.2**: Field preparation
- **Section 3.10.5.1.3**: Transplanting
- **Section 3.10.5.1.4**: Fertilizer application
- **Section 3.10.5.1.5.1**: Weed control
- **Section 3.10.5.1.5.2**: Insect pest control
- **Section 3.10.5.1.5.3**: Disease control

## Results
- **Total varieties extracted**: 4 unique varieties
- **Successfully inserted**: 4 varieties
- **Failed**: 0 varieties

## Varieties Successfully Inserted
1. **Early Texas Grano** - Recommended variety
2. **De Wildt** - Recommended variety
3. **pyramid** - Recommended variety
4. **Red Creole** - Recommended variety

## Information Extracted
- **Variety names** from section 3.10.5.1
- **Management information** (field preparation, transplanting, fertilizer)
- **Pest control** (thrips control)
- **Weed control** (keep field weed free)
- **Disease control** (purple blotch disease)

## Database Fields Used
- `crop_id`: 60 (onion)
- `crop_name`: 'onion'
- `variety_name`: Variety name
- `table_source`: 'Section 3.10.5.1'
- `source_document`: 'Guide to Agriculture Production in Malawi 2021'
- `extraction_confidence`: 0.9
- `harvesting_guidelines`: Variety notes
- `fertilizer_requirements`: Management information (field preparation, transplanting, fertilizer, pest, weed, disease control)

## Key Features
- **Comprehensive extraction** from recommended varieties section
- **Detailed management information** including field preparation, transplanting, fertilizer
- **Pest and disease control** information
- **Proper deduplication** to avoid duplicate entries

## Management Information Extracted
### Field Preparation:
- Plough deeply and incorporate well decomposed compost or khola manure at the rate of 3 to 5kg per square meter
- Make beds 120cm wide and to a convenient length
- The beds should be 20 to 25cm high
- Pathways should be 50cm between beds

### Transplanting:
- Transplant seedlings when their bases are of pencil thickness, 6 to 8 weeks after sowing
- Spacing should be 30 cm by 10 cm
- Water regularly as required
- Stop watering in the 5th month to allow bulbs to dry

### Fertilizer Application:
- Apply 60g of 'S' Compound fertilizer per square meter as a basal application using 2 cupfuls of cup No.22
- Top dress with 30g of CAN or Sulphate of Ammonia per square metre using one cupful of cup No.30 only when there is slow growth of seedlings

### Pest Control:
- **Thrips (Thrips tabaci)**: Controlled by spraying with Pirimiphos-methyl (Actellic) 50EC at the rate of 1ml in 14 liters of water for knapsack or 1ml in 1litre of water for ULV sprayer

### Weed Control:
- Keep the field weed free at all times

### Disease Control:
- **Purple blotch (Alternaria porri)**: Controlled by spraying with Mancozeb (Dithane M45) at the rate of 20g in 10litres of water or Captan 50WP at the rate of 20g in 10litres of water or alternatively 28g in 1litre of water for ULV

## Additional Information
- **Seed rate**: 3 - 3.5kg/ha
- **Potential yield range**: 22,000kg to 24,000kg per hectare
- **Growing conditions**: Require cool to warm seasons for good bulb formation
- **Soil requirements**: Rich in organic matter and free draining
- **Planting time**: Should be sown from mid-February to April
- **Harvesting**: About six months after sowing, when bulbs mature and neck of stem shrivels and falls over

## Variety Characteristics
- **All varieties**: Recommended varieties suitable for Malawi conditions
- **Early Texas Grano**: Traditional recommended variety
- **De Wildt**: Traditional recommended variety
- **pyramid**: Traditional recommended variety
- **Red Creole**: Traditional recommended variety

## Next Steps
The onion variety extraction is complete and successful. The database now contains comprehensive onion variety information that can be used for:
- Crop recommendations based on variety suitability
- Management guidance for different varieties
- Yield expectations and potential
- Pest and disease control information
- Fertilizer application recommendations
- Transplanting and spacing guidance

## Files Created
- `scripts/structured_onion_extractor.py`: Main extraction script
- `scripts/check_and_add_onion_crop.py`: Crop verification script
- `scripts/analyze_onion_section_detailed.py`: Section analysis script
- `scripts/find_onion_specific_sections.py`: Specific section locator
