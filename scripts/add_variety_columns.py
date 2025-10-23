#!/usr/bin/env python3
"""
Add Additional Columns to Varieties Table
Add columns for originator, grain_color, grain_texture, ecology
"""

import os
from supabase import create_client, Client

# Configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

def add_variety_columns():
    """Add additional columns to varieties table"""
    
    print("=" * 80)
    print("ADDING ADDITIONAL COLUMNS TO VARIETIES TABLE")
    print("=" * 80)
    
    # SQL commands to add new columns
    sql_commands = [
        # Add originator column
        "ALTER TABLE varieties ADD COLUMN IF NOT EXISTS originator TEXT;",
        
        # Add grain_color column
        "ALTER TABLE varieties ADD COLUMN IF NOT EXISTS grain_color TEXT;",
        
        # Add grain_texture column
        "ALTER TABLE varieties ADD COLUMN IF NOT EXISTS grain_texture TEXT;",
        
        # Add ecology column
        "ALTER TABLE varieties ADD COLUMN IF NOT EXISTS ecology TEXT;",
        
        # Add table_source column
        "ALTER TABLE varieties ADD COLUMN IF NOT EXISTS table_source TEXT;",
        
        # Add comments
        "COMMENT ON COLUMN varieties.originator IS 'Organization/company that developed the variety';",
        "COMMENT ON COLUMN varieties.grain_color IS 'Color of the grain (White, Yellow, Orange, etc.)';",
        "COMMENT ON COLUMN varieties.grain_texture IS 'Texture of the grain (Flint, Semi-Flint, Dent, etc.)';",
        "COMMENT ON COLUMN varieties.ecology IS 'Ecological zone/altitude suitability';",
        "COMMENT ON COLUMN varieties.table_source IS 'Source table from the PDF document';"
    ]
    
    try:
        # Note: We can't execute DDL directly through the Python client
        # We need to use the Supabase SQL editor or CLI
        print("SQL commands to execute in Supabase SQL Editor:")
        print("\n" + "="*60)
        
        for i, sql in enumerate(sql_commands, 1):
            print(f"-- Command {i}")
            print(sql)
            print()
        
        print("="*60)
        print("\nInstructions:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Copy and paste the above SQL commands")
        print("4. Execute them one by one or all together")
        print("5. Verify the columns were added successfully")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def verify_columns():
    """Verify that the columns were added successfully"""
    
    print("\n" + "=" * 80)
    print("VERIFYING NEW COLUMNS")
    print("=" * 80)
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Try to select from the new columns
        result = supabase.table("varieties").select("id, variety_name, originator, grain_color, grain_texture, ecology, table_source").limit(1).execute()
        
        if result.data:
            print("✅ SUCCESS: New columns are available!")
            print("Available columns:")
            print("- originator")
            print("- grain_color") 
            print("- grain_texture")
            print("- ecology")
            print("- table_source")
        else:
            print("❌ Columns not yet added or no data available")
            
    except Exception as e:
        if "column" in str(e).lower() and "does not exist" in str(e).lower():
            print("❌ Columns not yet added to database")
            print("Please execute the SQL commands in Supabase SQL Editor first")
        else:
            print(f"Error verifying columns: {e}")

def main():
    print("VARIETIES TABLE SCHEMA UPDATE")
    print("Adding columns for structured variety data")
    
    # Generate SQL commands
    add_variety_columns()
    
    # Wait for user to execute SQL
    input("\nPress Enter after you've executed the SQL commands in Supabase...")
    
    # Verify columns were added
    verify_columns()
    
    print("\n" + "=" * 80)
    print("SCHEMA UPDATE COMPLETE")
    print("You can now run the structured maize extractor again")
    print("=" * 80)

if __name__ == "__main__":
    main()


