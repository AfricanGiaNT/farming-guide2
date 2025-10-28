# Supabase Varieties Table Schema

## Updated Schema (2024-10-28)

### Changes Applied
1. **Changed VARCHAR to TEXT**: All string columns now use TEXT type for flexibility
2. **Added UNIQUE constraint**: `(crop_id, variety_name)` ensures no duplicates within a crop
3. **Created index**: Fast lookups by crop and variety name

### Current Schema

```sql
CREATE TABLE varieties (
    id BIGSERIAL PRIMARY KEY,
    crop_id BIGINT NOT NULL REFERENCES crops(id) ON DELETE CASCADE,
    variety_name TEXT NOT NULL,
    type TEXT,
    yield_potential TEXT,
    maturity_days INTEGER,
    drought_tolerance TEXT,
    disease_resistance TEXT,
    planting_months TEXT,
    harvest_months TEXT,
    min_rainfall_mm NUMERIC,
    max_rainfall_mm NUMERIC,
    optimal_temperature_min NUMERIC,
    optimal_temperature_max NUMERIC,
    soil_requirements TEXT,
    spacing_requirements TEXT,
    fertilizer_requirements TEXT,
    pest_management TEXT,
    disease_management TEXT,
    harvesting_guidelines TEXT,
    storage_requirements TEXT,
    seed_rate_per_hectare TEXT,
    expected_yield_per_hectare NUMERIC,
    market_preference TEXT,
    seed_availability TEXT,
    cost_per_kg NUMERIC,
    source_document TEXT,
    extraction_confidence INTEGER DEFAULT 80,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- UNIQUE constraint: Each variety name must be unique within a crop
    CONSTRAINT unique_variety_per_crop UNIQUE (crop_id, variety_name)
);

-- Index for fast lookups
CREATE INDEX idx_varieties_crop_name ON varieties(crop_id, variety_name);

-- Index for crop_id lookups
CREATE INDEX idx_varieties_crop_id ON varieties(crop_id);
```

### Key Points

1. **Primary Key**: `id` (BIGSERIAL) - auto-incrementing unique identifier
2. **Unique Constraint**: `(crop_id, variety_name)` - prevents duplicate variety names within the same crop
3. **Foreign Key**: `crop_id` references `crops(id)` with CASCADE delete
4. **TEXT vs VARCHAR**: TEXT is preferred in PostgreSQL/Supabase for variable-length strings

### Benefits

- **Flexibility**: TEXT columns can store strings of any length
- **Data Integrity**: UNIQUE constraint prevents accidental duplicates
- **Performance**: Indexes speed up queries by crop and variety name
- **Consistency**: Different crops can have varieties with the same name

### Migration Required

Run the SQL migration in `scripts/migrations/update_varieties_schema_text_and_unique.sql` via Supabase SQL Editor.


