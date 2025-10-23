# Tomato Variety Extraction Results Summary

## Overview
Successfully extracted tomato varieties from the Guide to Agriculture Production in Malawi 2021, following the same successful approach used for groundnut, soybean, sunflower, and cassava extraction.

## Extraction Sources
- **Table 67**: 7 newly released varieties with yield information
- **Section 3.10.4.1**: Improved yields section with variety recommendations
- **Section 3.10.4.1.3**: Fertilizer application
- **Section 3.10.4.1.4**: Time of transplanting and spacing
- **Section 3.10.4.1.5.1**: Weed control
- **Section 3.10.4.1.5.2**: Insect pest control
- **Section 3.10.4.1.5.4**: Disease control

## Results
- **Total varieties extracted**: 7 unique varieties
- **Successfully inserted**: 7 varieties
- **Failed**: 0 varieties

## Varieties Successfully Inserted
1. **Rodade (Mpindulitsa)** - 26 mt/ha yield
2. **Mbambande** - 26 mt/ha yield
3. **Khama** - 26 mt/ha yield
4. **Lomittel (Changu)** - 26 mt/ha yield
5. **Phindu** - 50 mt/ha yield (highest yielding)
6. **Cheyenne** - 26.7 mt/ha yield
7. **Steel** - 27.3 mt/ha yield

## Information Extracted
- **Variety names** from Table 67
- **Yield potential** (26-50 mt/ha range)
- **Management information** (fertilizer, transplanting, spacing)
- **Pest control** (aphids, caterpillars, red spider mites)
- **Weed control** (regular weeding)
- **Disease control** (early blight, late blight, bacterial wilt)

## Database Fields Used
- `crop_id`: 59 (tomato)
- `crop_name`: 'tomato'
- `variety_name`: Variety name
- `yield_potential`: Yield information
- `table_source`: 'Table 67'
- `source_document`: 'Guide to Agriculture Production in Malawi 2021'
- `extraction_confidence`: 0.9
- `harvesting_guidelines`: Yield information and variety notes
- `fertilizer_requirements`: Management information (fertilizer, transplanting, pest, weed, disease control)

## Key Features
- **Comprehensive extraction** from Table 67 and detailed text sections
- **Detailed variety information** including yield potential
- **Management guidance** for fertilizer, transplanting, spacing
- **Pest and disease control** information
- **Proper deduplication** to avoid duplicate entries

## Management Information Extracted
### Fertilizer Application:
- Two to three days before planting, apply 100g of 'B' Compound fertilizer per square meter
- Top dress 5 weeks after transplanting with 20g of CAN per sq meter using one cupful of cup No. 22

### Time of Transplanting and Spacing:
- Transplant when seedlings are 10 to 15cm tall or 4 weeks after sowing
- Transplant seedlings at 90cm x 60cm
- Plants should be staked and side shoots may be removed to increase the fruit size and improve quality

### Pest Control:
- **Aphids (Aphididae)**: Controlled by spraying with Dimethoate 20WP at the rate of 34g in 14litres of water for knapsack sprayer or 34g in 1 litre of water for ULV sprayer
- **Caterpillars**: Controlled by spraying with carbaryl 85WP at 35g in 14 litres of water for knapsack sprayer or in 1litre of water for ULV sprayer
- **Red spider mites**: Controlled by tobacco, ash and soap concoction (handful of dark fire cured tobacco, a quarter tablet of soap (30g) and a handful of ordinary ash), mixed and boiled in five liters of water, cooled overnight, sprayed every two weeks
- **Intercropping**: Tomato with onions reduces red spider mite infestation compared to pure stand of tomato

### Weed Control:
- Weed regularly to reduce competition for plant nutrients and moisture

### Disease Control:
- **Early Blight (Alternaria solani) and Late Blight (Phytopthora infestans)**: Controlled by Kickback (generic fungicide mixture of Mancozeb and Matalaxyl) at 320ml per 100litres of water, Mancozeb (DithaneM45) 80WP at 28g in 14litres of water for knapsack sprayer, or Chlorothalonil (Daconil 2787W-75) 40g in 14litres of water for knapsack sprayer
- **Bacterial Wilt (Pseudomonas solanacearum)**: Controlled through crop rotation and roguing of infested plants and removal of plant debris
- **Plastic shelter**: Combined with dithane is effective in controlling late blight disease in tomato

## Variety Characteristics
- **Highest yielding**: Phindu (50 mt/ha)
- **High yielding**: Steel (27.3 mt/ha), Cheyenne (26.7 mt/ha)
- **Standard yielding**: Rodade, Mbambande, Khama, Lomittel (26 mt/ha each)
- **All varieties**: Newly released varieties suitable for Malawi conditions

## Additional Information
- **Seed rate**: 200g/ha
- **Potential yield range**: 18,000 to 50,000kg per hectare depending on variety
- **Growing conditions**: Can be grown all year round except in extremely hot dry conditions
- **Soil requirements**: Free draining and rich in organic matter
- **Traditional varieties mentioned**: Money Maker, Marglobe, Heinz, Homestead, Roma VF (suitable for processing industry)

## Next Steps
The tomato variety extraction is complete and successful. The database now contains comprehensive tomato variety information that can be used for:
- Crop recommendations based on yield potential
- Management guidance for different varieties
- Yield expectations and potential
- Pest and disease control information
- Fertilizer application recommendations
- Transplanting and spacing guidance

## Files Created
- `scripts/structured_tomato_extractor.py`: Main extraction script
- `scripts/check_and_add_tomato_crop.py`: Crop verification script
- `scripts/analyze_tomato_section_detailed.py`: Section analysis script
- `scripts/search_for_tomato_section.py`: Section locator
- `scripts/find_tomato_specific_sections.py`: Specific section locator
