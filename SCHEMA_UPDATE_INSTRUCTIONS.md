# Varieties Schema Update Instructions

## What's Being Changed

1. **VARCHAR → TEXT**: All string columns in the `varieties` table are being converted to TEXT
2. **UNIQUE Constraint**: Adding `(crop_id, variety_name)` unique constraint to prevent duplicate variety names within a crop
3. **Index**: Adding an index for faster lookups

## How to Apply

### Step 1: Open Supabase SQL Editor
1. Go to: https://app.supabase.com/project/itcsdacjopedjcyhqyki/sql
2. Log in if needed

### Step 2: Copy and Run Migration SQL
Copy the SQL from `scripts/migrations/update_varieties_schema_text_and_unique.sql` and paste it into the SQL editor, then click "Run".

### Step 3: Verify
Run this query to verify the changes:

```sql
-- Check the constraint was added
SELECT conname, contype 
FROM pg_constraint 
WHERE conrelid = 'varieties'::regclass;

-- Check the index was created
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'varieties';
```

You should see:
- `unique_variety_per_crop` constraint
- `idx_varieties_crop_name` index

## What This Fixes

### Before:
- Columns used VARCHAR with length limits
- No protection against duplicate variety names within a crop
- Possible data truncation

### After:
- TEXT columns can store strings of any length
- Database enforces uniqueness of variety names per crop
- Better data integrity

## Impact on Code

The code changes have been made to:
- Handle the unique constraint gracefully
- Add proper error handling for duplicate insertions
- Continue working seamlessly with the updated schema

## Rollback (if needed)

If you need to rollback:

```sql
-- Remove the constraint
ALTER TABLE varieties DROP CONSTRAINT IF EXISTS unique_variety_per_crop;

-- Remove the index
DROP INDEX IF EXISTS idx_varieties_crop_name;

-- Note: TEXT to VARCHAR conversion is not recommended
-- Keep TEXT as it's more flexible
```


