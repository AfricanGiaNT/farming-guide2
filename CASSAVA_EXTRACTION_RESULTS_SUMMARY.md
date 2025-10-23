# Cassava Variety Extraction Results Summary

## Overview
Successfully extracted cassava varieties from the Guide to Agriculture Production in Malawi 2021, following the same successful approach used for groundnut, soybean, and sunflower extraction.

## Extraction Sources
- **Table 42**: 17 varieties with detailed descriptions, taste, special attributes, maturity periods, and yield potential
- **Section 3.4.2.1**: Improved yields section with variety lists
- **Section 3.4.2.2.4**: Seed rate information
- **Section 3.4.2.2.5**: Time of planting
- **Section 3.4.2.2.6**: Plant population
- **Section 3.4.2.3**: Pest control
- **Section 3.4.2.3.1**: Weed control
- **Section 3.4.2.3.3**: Disease control

## Results
- **Total varieties extracted**: 19 unique varieties
- **Successfully inserted**: 19 varieties
- **Failed**: 0 varieties

## Varieties Successfully Inserted
### Sweet Varieties (6):
1. **Chamandanda** - Yellow colour, 12-15 months maturity, 26 tonnes/ha yield
2. **Chinangwa 1** - White, 12-18 months maturity, 37 tonnes/ha yield
3. **Chinangwa 2** - White, 12-15 months maturity, 38 tonnes/ha yield
4. **Mpale** - White, 12-15 months maturity, 30 tonnes/ha yield
5. **Kalawe** - White, 12-15 months maturity, 28 tonnes/ha yield
6. **Mbundumali/Manyokola** - White, 9-15 months maturity, 25 tonnes/ha yield

### Bitter Varieties (11):
7. **Gomani** - White, 9-15 months maturity, 25 tonnes/ha yield
8. **Chitembwere** - White, 9-18 months maturity, 18 tonnes/ha yield
9. **Silira** - White, 9-15 months maturity, 25 tonnes/ha yield
10. **Maunjili** - White, 9-12 months maturity, 35 tonnes/ha yield
11. **Mkondezi** - White, 9-15 months maturity, 40 tonnes/ha yield
12. **Sauti** - White, 12-15 months maturity, 25 tonnes/ha yield
13. **Yizaso** - White, 12-15 months maturity, 25 tonnes/ha yield
14. **Phoso** - White, 12-15 months maturity, 35 tonnes/ha yield
15. **Mulola** - White, 12-15 months maturity, 40 tonnes/ha yield
16. **Sagonja** - White, 9-12 months maturity, 35 tonnes/ha yield
17. **Chiombola** - White, 9-12 months maturity, 45 tonnes/ha yield

## Information Extracted
- **Variety names** from Table 42 and section 3.4.2.1
- **Taste classification** (Sweet vs Bitter)
- **Special attributes** (Yellow colour, White)
- **Maturity periods** (9-18 months range)
- **Yield potential** (18-45 tonnes/ha)
- **Management information** (seed rate, planting time, plant population)
- **Pest control** (mealy bug, white flies, scales, green mite)
- **Weed control** (early weeding, critical first 3 months)
- **Disease control** (mosaic disease, bacterial blight, brown streak disease)

## Database Fields Used
- `crop_id`: 1 (cassava)
- `crop_name`: 'cassava'
- `variety_name`: Variety name
- `yield_potential`: Yield information
- `table_source`: 'Table 42' or 'Section 3.4.2.1'
- `source_document`: 'Guide to Agriculture Production in Malawi 2021'
- `extraction_confidence`: 0.9
- `harvesting_guidelines`: Maturity periods, taste, special attributes
- `fertilizer_requirements`: Management information (seed rate, planting, population, pest, weed, disease control)

## Key Features
- **Comprehensive extraction** from Table 42 and detailed text sections
- **Detailed variety information** including taste classification, maturity periods, yield potential
- **Management guidance** for seed rate, planting time, plant population
- **Pest and disease control** information
- **Proper deduplication** to avoid duplicate entries

## Management Information Extracted
### Seed Rate:
- About 65 to 80 bundles of 50 one meter long stems required to plant one hectare
- For root production

### Planting Time:
- Plant with the first planting rains
- Farmers should not plant cassava late
- Cassava does well on well drained soils

### Plant Population:
- To obtain optimum plant population, plant cassava on ridges at 90cm apart and 90cm between plants
- This gives plant population of about 12,000 plants per hectare
- For slender roots to be sold fresh on the market, spacing of 90cm x 75cm or 90cm x 60cm can be used
- Will give plant population of about 15,000 and 18,000 plants per hectare respectively

### Pest Control:
- Cassava mealy bug (Phenacoccus manihot) - serious pest, symptoms include leaf curl, shortened internodes, bunchy tops, stunted growth
- White flies (Bemisia spp) - transmit cassava mosaic and brown streak virus diseases
- Cassava scales (Aonidomytilus albus) - sucking insect pests, cause yellowing and defoliation
- Cassava green mite (CGM) - feeds on young leaves and tender shoots, causes yellow speckles, leaf size reduction

### Weed Control:
- Weed early particularly during the critical first 3 months of establishment
- Delay in weeding results in low yields

### Disease Control:
- Cassava Mosaic Disease (CMD) - caused by cassava mosaic virus, characterized by mottled and curled leaves
- Cassava Bacterial Blight (Xanthomonas campestris pv. Manhot) - characterized by wilting tips and die back
- Cassava Brown Streak Disease (CBSD) - caused by virus, transmitted by white flies, causes discoloration and necrosis

## Variety Characteristics
- **Sweet varieties**: Generally have longer maturity periods (12-18 months), moderate to high yield potential (25-38 tonnes/ha)
- **Bitter varieties**: Range from early to late maturity (9-18 months), variable yield potential (18-45 tonnes/ha)
- **Highest yielding**: Chiombola (45 tonnes/ha), Mkondezi and Mulola (40 tonnes/ha)
- **Early maturing**: Maunjili, Sagonja, Chiombola (9-12 months)

## Next Steps
The cassava variety extraction is complete and successful. The database now contains comprehensive cassava variety information that can be used for:
- Crop recommendations based on taste preference and maturity groups
- Management guidance for different varieties
- Yield expectations and potential
- Pest and disease control information
- Planting and population management
- Processing guidance (sweet vs bitter varieties)

## Files Created
- `scripts/structured_cassava_extractor.py`: Main extraction script
- `scripts/check_and_add_cassava_crop.py`: Crop verification script
- `scripts/analyze_cassava_section_detailed.py`: Section analysis script
- `scripts/find_cassava_specific_sections.py`: Section locator
- `scripts/find_cassava_section_3_4_2_1_and_table_42.py`: Specific section and table locator
