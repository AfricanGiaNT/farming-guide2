#!/usr/bin/env python3
"""
Clean Up Faya Rice Varieties
Consolidate Faya14-M-49 variants into a single proper entry
"""

from supabase import create_client, Client

# Configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

def clean_up_faya_varieties():
    """Clean up and consolidate Faya rice varieties"""
    
    print("=" * 80)
    print("CLEANING UP FAYA RICE VARIETIES")
    print("=" * 80)
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Get all rice varieties
        result = supabase.table("varieties").select("id, variety_name, ecology, table_source").eq("crop_name", "rice").execute()
        
        if not result.data:
            print("No rice varieties found in database")
            return
        
        print(f"Found {len(result.data)} rice varieties")
        
        # Find Faya-related varieties
        faya_varieties = []
        for variety in result.data:
            variety_name = variety['variety_name'].lower()
            if 'faya' in variety_name:
                faya_varieties.append(variety)
        
        print(f"\nFound {len(faya_varieties)} Faya-related varieties:")
        for variety in faya_varieties:
            print(f"  - {variety['variety_name']} (ID: {variety['id']}, Ecology: {variety['ecology']}, Source: {variety['table_source']})")
        
        if len(faya_varieties) > 1:
            print(f"\nConsolidating {len(faya_varieties)} Faya varieties into one...")
            
            # Find the best Faya variety to keep (prefer Table 23 with full name)
            best_faya = None
            for variety in faya_varieties:
                if variety['table_source'] == 'Table 23' and 'faya' in variety['variety_name'].lower() and '14' in variety['variety_name']:
                    best_faya = variety
                    break
            
            # If no Table 23 version, pick the most complete one
            if not best_faya:
                for variety in faya_varieties:
                    if 'faya' in variety['variety_name'].lower() and '14' in variety['variety_name']:
                        best_faya = variety
                        break
            
            # If still no good one, pick the first one
            if not best_faya:
                best_faya = faya_varieties[0]
            
            print(f"Keeping: {best_faya['variety_name']} (ID: {best_faya['id']})")
            
            # Update the kept variety to have the proper name
            proper_name = "Faya14-M-49"
            if best_faya['variety_name'] != proper_name:
                print(f"Updating name from '{best_faya['variety_name']}' to '{proper_name}'")
                
                update_result = supabase.table("varieties").update({
                    "variety_name": proper_name,
                    "table_source": "Table 23 (consolidated)"
                }).eq("id", best_faya['id']).execute()
                
                if update_result.data:
                    print(f"  SUCCESS: Updated variety name")
                else:
                    print(f"  ERROR: Failed to update variety name")
            
            # Delete the other Faya varieties
            varieties_to_delete = [v for v in faya_varieties if v['id'] != best_faya['id']]
            
            for variety in varieties_to_delete:
                try:
                    delete_result = supabase.table("varieties").delete().eq("id", variety['id']).execute()
                    if delete_result.data:
                        print(f"  SUCCESS: Deleted duplicate {variety['variety_name']}")
                    else:
                        print(f"  ERROR: Failed to delete {variety['variety_name']}")
                except Exception as e:
                    print(f"  ERROR: Error deleting {variety['variety_name']}: {e}")
        else:
            print("\nOnly one Faya variety found. No consolidation needed.")
        
        # Show final count
        final_result = supabase.table("varieties").select("id").eq("crop_name", "rice").execute()
        print(f"\nFinal rice variety count: {len(final_result.data)}")
        
        # Show remaining varieties
        print("\nRemaining rice varieties:")
        varieties_result = supabase.table("varieties").select("variety_name, ecology, table_source").eq("crop_name", "rice").order("variety_name").execute()
        
        for variety in varieties_result.data:
            print(f"  - {variety['variety_name']} ({variety['ecology']}) - {variety['table_source']}")
        
    except Exception as e:
        print(f"ERROR: {e}")

def main():
    clean_up_faya_varieties()

if __name__ == "__main__":
    main()
