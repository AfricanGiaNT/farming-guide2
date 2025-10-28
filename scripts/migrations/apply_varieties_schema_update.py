#!/usr/bin/env python3
"""
Apply varieties schema update to Supabase
Changes VARCHAR to TEXT and adds UNIQUE constraint
"""

import os
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

def apply_migration():
    """Apply the migration SQL to Supabase"""
    
    print("=" * 80)
    print("APPLYING VARIETIES SCHEMA UPDATE")
    print("=" * 80)
    print()
    print("Changes:")
    print("1. Converting VARCHAR columns to TEXT")
    print("2. Adding UNIQUE constraint on (crop_id, variety_name)")
    print("3. Creating index for faster lookups")
    print()
    
    # Read the migration SQL
    migration_file = os.path.join(os.path.dirname(__file__), 'update_varieties_schema_text_and_unique.sql')
    
    if not os.path.exists(migration_file):
        print(f"❌ Migration file not found: {migration_file}")
        return False
    
    with open(migration_file, 'r') as f:
        migration_sql = f.read()
    
    print(f"📄 Migration SQL loaded from: {migration_file}")
    print()
    print("=" * 80)
    print("MIGRATION SQL:")
    print("=" * 80)
    print(migration_sql)
    print()
    print("=" * 80)
    print()
    
    # Ask for confirmation
    response = input("Do you want to apply this migration? (yes/no): ")
    
    if response.lower() != 'yes':
        print("❌ Migration cancelled.")
        return False
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        print("🔄 Applying migration to Supabase...")
        
        # Execute the migration SQL
        # Note: Supabase Python client doesn't have direct SQL execution
        # You need to run this via the Supabase SQL editor or use psycopg2
        
        print()
        print("⚠️  IMPORTANT: This script shows the SQL to apply.")
        print("⚠️  Please run this SQL in the Supabase SQL Editor:")
        print()
        print("1. Go to https://app.supabase.com/project/itcsdacjopedjcyhqyki/sql")
        print("2. Copy the SQL from the migration file")
        print("3. Paste and execute it in the SQL editor")
        print()
        print("✅ Migration prepared successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    apply_migration()


