# Crop Production Info Table

## Overview

The `crop_production_info` table stores general crop production information extracted from PDFs. This information applies to the crop in general, not specific varieties.

## Table Structure

```sql
CREATE TABLE crop_production_info (
    id BIGSERIAL PRIMARY KEY,
    crop_id BIGINT NOT NULL REFERENCES crops(id) ON DELETE CASCADE,
    
    -- Production Information Fields
    production_notes TEXT,              -- Things to take note in production
    land_preparation TEXT,              -- Land preparation information
    manure_application TEXT,           -- Manure application information
    planting_info TEXT,                 -- General planting information
    fertilizer_application TEXT,        -- Fertilizer application information
    weeding TEXT,                       -- Weeding information
    storing TEXT,                       -- Storage requirements
    
    -- Metadata
    source_document TEXT,               -- Source PDF or document name
    extraction_confidence INTEGER DEFAULT 80,  -- Confidence score (0-100)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_crop_production_info UNIQUE (crop_id)
);
```

## Field Descriptions

### production_notes
Things to take note in production: disease management, pest management, drought tolerance, and general production notes.

### land_preparation
Land preparation information including plowing, harrowing, soil preparation, and field preparation guidelines.

### manure_application
Manure application information including rates (e.g., 5-10 tons per hectare), timing, methods, and incorporation practices.

### planting_info
General planting information including:
- Planting time/seasons
- Spacing requirements
- Seed rate per hectare
- Planting depth and methods
- Planting guidelines

### fertilizer_application
Fertilizer application information including:
- Types of fertilizers (NPK ratios)
- Application rates (kg/ha)
- Timing (at planting, top-dressing)
- Application methods

### weeding
Weeding information including:
- Timing (weeks after planting)
- Frequency
- Methods (hand weeding, hoeing, herbicides)
- Best practices

### storing
Storage requirements and harvesting guidelines including:
- Storage conditions (temperature, humidity, ventilation)
- Drying requirements
- Container types
- Pest and moisture protection
- Harvest timing and methods

## Usage

### Example Insert Query

```sql
INSERT INTO crop_production_info (
    crop_id,
    production_notes,
    land_preparation,
    manure_application,
    planting_info,
    fertilizer_application,
    weeding,
    storing,
    source_document,
    extraction_confidence
) VALUES (
    1,  -- crop_id for maize
    'Monitor growth regularly. Ensure adequate water supply. Follow recommended spacing.',
    'Prepare land by plowing and harrowing to achieve fine tilth. Remove weeds and incorporate organic matter.',
    'Apply well-decomposed farmyard manure or compost at 5-10 tons per hectare before planting.',
    'Plant during rainy season. Maintain spacing of 75cm x 25cm. Seed rate: 20-25kg per hectare.',
    'Apply 100-150 kg/ha of compound fertilizer (23:21:0+4S) at planting. Top-dress with nitrogen 4-6 weeks after planting.',
    'Weed 2-3 weeks after planting and as needed. Keep field weed-free during first 6-8 weeks.',
    'Store in cool, dry, well-ventilated place. Ensure proper drying before storage. Protect from pests and moisture.',
    'Guide to Agriculture Production in Malawi 2021',
    85
);
```

### Query Production Info for a Crop

```sql
SELECT 
    c.crop_name,
    cpi.production_notes,
    cpi.land_preparation,
    cpi.manure_application,
    cpi.planting_info,
    cpi.fertilizer_application,
    cpi.weeding,
    cpi.storing,
    cpi.source_document
FROM crop_production_info cpi
JOIN crops c ON cpi.crop_id = c.id
WHERE c.crop_name = 'maize';
```

## Relationship with Other Tables

- **crops**: One-to-one relationship (one crop can have one production info record)
- **varieties**: Not directly related. Varieties table contains variety-specific information, while this table contains general crop information.

## Migration Details

- **Migration Name**: `create_crop_production_info_table`
- **Created**: 2025-01-28
- **Index**: `idx_crop_production_info_crop_id` on `crop_id` for fast lookups
- **Trigger**: Auto-updates `updated_at` timestamp on row updates

