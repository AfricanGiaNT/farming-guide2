-- Migration: Update varieties table schema
-- 1. Change VARCHAR columns to TEXT
-- 2. Add UNIQUE constraint on (crop_id, variety_name)
-- Date: 2024-10-28

-- Step 1: Change VARCHAR columns to TEXT
-- Note: In PostgreSQL/Supabase, TEXT is preferred over VARCHAR for variable-length strings

ALTER TABLE varieties 
  ALTER COLUMN variety_name TYPE TEXT,
  ALTER COLUMN type TYPE TEXT,
  ALTER COLUMN yield_potential TYPE TEXT,
  ALTER COLUMN drought_tolerance TYPE TEXT,
  ALTER COLUMN disease_resistance TYPE TEXT,
  ALTER COLUMN planting_months TYPE TEXT,
  ALTER COLUMN harvest_months TYPE TEXT,
  ALTER COLUMN soil_requirements TYPE TEXT,
  ALTER COLUMN spacing_requirements TYPE TEXT,
  ALTER COLUMN fertilizer_requirements TYPE TEXT,
  ALTER COLUMN pest_management TYPE TEXT,
  ALTER COLUMN disease_management TYPE TEXT,
  ALTER COLUMN harvesting_guidelines TYPE TEXT,
  ALTER COLUMN storage_requirements TYPE TEXT,
  ALTER COLUMN market_preference TYPE TEXT,
  ALTER COLUMN seed_availability TYPE TEXT,
  ALTER COLUMN source_document TYPE TEXT,
  ALTER COLUMN description TYPE TEXT;

-- Step 2: Add UNIQUE constraint on (crop_id, variety_name)
-- This ensures no duplicate variety names within the same crop
-- Drop the constraint first if it exists (idempotent)
ALTER TABLE varieties DROP CONSTRAINT IF EXISTS unique_variety_per_crop;

-- Add the constraint
ALTER TABLE varieties 
  ADD CONSTRAINT unique_variety_per_crop UNIQUE (crop_id, variety_name);

-- Create an index to speed up lookups by crop_id and variety_name
CREATE INDEX IF NOT EXISTS idx_varieties_crop_name ON varieties(crop_id, variety_name);

-- Add comment to document the constraint
COMMENT ON CONSTRAINT unique_variety_per_crop ON varieties IS 
  'Ensures each variety name is unique within a crop. Different crops can have varieties with the same name.';


