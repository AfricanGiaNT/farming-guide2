# Ginger Variety Extraction Results Summary

## Overview
Successfully extracted ginger variety information from the Guide to Agriculture Production in Malawi 2021, following the same successful approach used for groundnut, soybean, sunflower, cassava, tomato, and onion extraction.

## Extraction Sources
- **Section 3.9.3.2.1**: Use of selected cultivars
- **Section 3.9.3.2.2**: Field preparation
- **Section 3.9.3.2.3**: Planting
- **Section 3.9.3.2.4**: Fertilizer application
- **Section 3.9.3.2.5**: Mulching
- **Section 3.9.3.3.1**: Weed control
- **Section 3.9.3.3.2**: Insect pest control
- **Section 3.9.3.3.3**: Disease control
- **Section 3.9.3.3.4**: Nematode control
- **Section 3.9.3.3.5**: Harvesting

## Results
- **Total varieties extracted**: 1 unique variety
- **Successfully inserted**: 1 variety
- **Failed**: 0 varieties

## Varieties Successfully Inserted
1. **Local Cultivars** - Currently there are no recommended ginger varieties. Farmers are encouraged to grow local cultivars.

## Information Extracted
- **Variety information** from section 3.9.3.2.1
- **Field preparation** (digging, bed preparation, organic manure)
- **Planting** (seed rate, spacing, timing)
- **Fertilizer application** (basal and top dressing)
- **Mulching** (grass mulching)
- **Pest control** (weed control, nematode control)
- **Disease control** (soft rot, rhizome rot, bacterial wilt)
- **Harvesting** (timing, method)
- **Potential yield** (up to 12,000 kg fresh weight per hectare)

## Database Fields Used
- `crop_id`: 42 (ginger)
- `crop_name`: 'ginger'
- `variety_name`: 'Local Cultivars'
- `table_source`: 'Section 3.9.3.2.1'
- `source_document`: 'Guide to Agriculture Production in Malawi 2021'
- `extraction_confidence`: 0.9
- `harvesting_guidelines`: Variety notes
- `fertilizer_requirements`: Management information (field preparation, planting, fertilizer, mulching, pest, disease control, harvesting, potential yield)

## Key Features
- **Comprehensive extraction** from improving yields section
- **Detailed management information** including field preparation, planting, fertilizer, mulching
- **Pest and disease control** information
- **Harvesting and yield information**

## Management Information Extracted
### Field Preparation:
- Fields should be dug and large clods broken to provide fine tilth
- The crop can be planted on beds or on ridges
- Beds are usually 120cm wide, 20 to 25cm high, and of any convenient length
- The path between beds should be 50 cm wide
- Well decomposed organic manure should be incorporated at the rate of 5 to 10kg per square metre of seedbed

### Planting:
- Plant ginger using fingers or setts
- Seed rate varies from 1,200 to 1,800kg per hectare
- Sow with the first rains in rows 30cm apart and 25cm between plants
- Planting with the first rains is very important as a delay of one week may result in yield losses of up to 1,000kg per hectare

### Fertilizer Application:
- Apply 75kg single super phosphate per hectare by applying 4.5g per 5m of row length using one cup No.5 at planting
- 40 to 60 days after planting, top dress with either CAN at the rate of 60kg per hectare, apply 5.4g per 3m of row length; or 35kg Urea, apply 4.2g per 4m of row length using 1 cupful of cup No.5
- Both CAN and Urea should be applied along with 50kg Muriate of Potash per hectare using the same cup for 2m of row length
- Three months after planting, the second dose of CAN should be applied at 60kg per hectare, or Urea at 35kg per hectare

### Mulching:
- Ginger should be kept mulched with grass preferably green grass or easily decomposed plant material

### Pest Control:
- **Weed Control**: The crop should be kept weed free
- **Insect Pest Control**: No insect pests of economic importance have been identified in Malawi
- **Nematode Control**: Nematodes can severely affect the growth of the crop and cause serious losses. Control is by treating the planting material with hot water at 48°C for 20 minutes. Fumigate the field with a nematicide where possible. Rotate ginger with other crops which are not susceptible to nematodes such as maize, cabbage and other brassicas and grass crops

### Disease Control:
- **Soft Rot (Pythium spp.)**: The leaves turn yellow and dry up. The shoots fall and cease to produce rhizomes. The inner tissue of the rhizomes become reduced to a soft, black, purifying mass. The disease is more prevalent in poorly drained soils. Control is by plant sanitation. It is important to select a well-drained site, practice crop rotation and use only healthy rhizomes for seed which should be treated with a fungicide
- **Rhizome Rot (Fusarium oxysporum)**: The disease causes severe rhizome rot and pseudostem collapse, sometimes it causes a brown streaking of the vascular tissue of the rhizomes and pseudostem. The disease spreads rapidly in the field with wet weather. The disease can be controlled by avoiding mechanical injury to the rhizomes when weeding and while carrying out other agronomic practices
- **Bacterial Wilt (Pseudomonas solanacearum)**: The first symptoms are yellowing and wilting of the lower leaves which quickly spread upwards. In advanced stages the base of the pseudostem becomes water-soaked, readily breaking away from the rhizomes. The vascular tissues become dark brown or black. If the pseudostem and rhizome are cut, they give a white, milky exudate. The disease can be controlled by crop rotation

### Harvesting:
- The crop is ready for lifting at about 7 to 9 months after planting when the lower leaves turn yellow
- When harvesting, care should be taken not to cut or bruise rhizomes and ensure that the whole clump is lifted
- The leafy tops should be cut off, all the adhering soil shaken or rubbed off and the rhizomes washed in water

### Potential Yield:
- Potential yields of up to 12,000 kg fresh weight can be achieved per hectare

## Additional Information
- **Growing conditions**: Thrives under hot and humid conditions
- **Altitude**: Grows in altitude of up to 1,500m above sea level
- **Rainfall**: High rainfall of 1,500 to 3,000 mm per year, well distributed over the 8 months growing period is ideal
- **Soil requirements**: Grows well in different soil types with free draining characteristics
- **Uses**: Mainly for food seasoning, in baking, brewing and in the wine industry
- **Seed storage**: Seed rhizomes should be stored in pits covered with sand under shade

## Variety Characteristics
- **Local Cultivars**: Currently there are no recommended ginger varieties. Farmers are encouraged to grow local cultivars

## Next Steps
The ginger variety extraction is complete and successful. The database now contains comprehensive ginger variety information that can be used for:
- Crop recommendations based on variety suitability
- Management guidance for different varieties
- Yield expectations and potential
- Pest and disease control information
- Fertilizer application recommendations
- Planting and spacing guidance
- Mulching requirements
- Harvesting timing and methods

## Files Created
- `scripts/structured_ginger_extractor.py`: Main extraction script
- `scripts/check_and_add_ginger_crop.py`: Crop verification script
- `scripts/analyze_ginger_section_detailed.py`: Section analysis script
- `scripts/search_for_ginger_section.py`: Broad search script
- `scripts/find_ginger_specific_sections.py`: Specific section locator
