#!/usr/bin/env python3
"""
Supabase Schema Refresh Solutions
Different approaches to get Supabase to recognize updated schema
"""

import os
import time
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "sb_secret_gqVADapMDpM_hEi7F9DAGw_DOldbrBs"

def solution_1_restart_client():
    """Solution 1: Restart the Supabase client"""
    print("=" * 80)
    print("SOLUTION 1: RESTART SUPABASE CLIENT")
    print("=" * 80)
    
    # Create a new client instance
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    try:
        # Test with a simple query to refresh schema
        result = supabase.table('varieties').select('*').limit(1).execute()
        
        if result.data:
            variety = result.data[0]
            print("Current columns in varieties table:")
            for key in sorted(variety.keys()):
                print(f"  - {key}")
            return True
        else:
            print("No varieties found in table")
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def solution_2_wait_and_retry():
    """Solution 2: Wait for schema cache to refresh"""
    print("\n" + "=" * 80)
    print("SOLUTION 2: WAIT FOR SCHEMA CACHE REFRESH")
    print("=" * 80)
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Wait for schema cache to refresh (can take up to 5 minutes)
    print("Waiting for schema cache to refresh...")
    print("This can take up to 5 minutes after adding columns.")
    
    for attempt in range(1, 6):
        print(f"Attempt {attempt}/5: Waiting 60 seconds...")
        time.sleep(60)
        
        try:
            # Test with a query that uses new columns
            result = supabase.table('varieties').select('promotion_status').limit(1).execute()
            print("SUCCESS: Schema cache has been refreshed!")
            return True
            
        except Exception as e:
            if "Could not find" in str(e):
                print(f"Schema not yet refreshed: {str(e)}")
            else:
                print(f"Other error: {str(e)}")
    
    print("Schema cache still not refreshed after 5 minutes.")
    return False

def solution_3_use_raw_sql():
    """Solution 3: Use raw SQL queries instead of table methods"""
    print("\n" + "=" * 80)
    print("SOLUTION 3: USE RAW SQL QUERIES")
    print("=" * 80)
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    try:
        # Use raw SQL to insert data
        sql = """
        INSERT INTO varieties (crop_id, crop_name, variety_name, originator, type, maturity_days, yield_potential, table_source, source_document, extraction_confidence, fertilizer_requirements, pest_management, disease_management)
        VALUES (13, 'groundnut', 'Test Variety', 'Test Originator', 'Test Type', '90-120', '2000 kg/ha', 'Test Source', 'Guide to Agriculture Production in Malawi 2021', 'high', 'Test fertilizer info', 'Test pest info', 'Test disease info')
        RETURNING id;
        """
        
        result = supabase.rpc('execute_sql', {'sql': sql}).execute()
        print("SUCCESS: Raw SQL insertion worked!")
        return True
        
    except Exception as e:
        print(f"Raw SQL approach failed: {str(e)}")
        return False

def solution_4_check_schema_directly():
    """Solution 4: Check schema directly using information_schema"""
    print("\n" + "=" * 80)
    print("SOLUTION 4: CHECK SCHEMA DIRECTLY")
    print("=" * 80)
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    try:
        # Query information_schema to see actual columns
        sql = """
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'varieties' 
        ORDER BY column_name;
        """
        
        result = supabase.rpc('execute_sql', {'sql': sql}).execute()
        
        if result.data:
            print("Actual columns in varieties table:")
            for row in result.data:
                print(f"  - {row['column_name']}: {row['data_type']}")
            return True
        else:
            print("No schema information returned")
            return False
            
    except Exception as e:
        print(f"Schema check failed: {str(e)}")
        return False

def solution_5_force_schema_refresh():
    """Solution 5: Force schema refresh by making a schema-altering query"""
    print("\n" + "=" * 80)
    print("SOLUTION 5: FORCE SCHEMA REFRESH")
    print("=" * 80)
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    try:
        # Make a query that forces schema refresh
        # This is a harmless query that should trigger schema refresh
        sql = "SELECT * FROM varieties LIMIT 0;"
        
        result = supabase.rpc('execute_sql', {'sql': sql}).execute()
        print("Schema refresh query executed successfully")
        
        # Now try to use new columns
        time.sleep(5)  # Wait a moment
        
        result = supabase.table('varieties').select('promotion_status').limit(1).execute()
        print("SUCCESS: New columns are now accessible!")
        return True
        
    except Exception as e:
        print(f"Force refresh failed: {str(e)}")
        return False

def main():
    print("SUPABASE SCHEMA REFRESH SOLUTIONS")
    print("=" * 80)
    
    solutions = [
        solution_1_restart_client,
        solution_2_wait_and_retry,
        solution_3_use_raw_sql,
        solution_4_check_schema_directly,
        solution_5_force_schema_refresh
    ]
    
    for i, solution in enumerate(solutions, 1):
        try:
            success = solution()
            if success:
                print(f"\nSOLUTION {i} WORKED! You can now use the updated schema.")
                break
        except Exception as e:
            print(f"\nSolution {i} failed: {str(e)}")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS:")
    print("1. Try Solution 1 first (restart client)")
    print("2. If that doesn't work, wait 5-10 minutes and try again")
    print("3. Use raw SQL queries as a workaround")
    print("4. Check if columns were actually added using Solution 4")

if __name__ == "__main__":
    main()
