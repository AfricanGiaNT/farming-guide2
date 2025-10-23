#!/usr/bin/env python3
"""
Clean Up Rice Variety Names and Handle Duplicates
Remove trailing periods and handle duplicate names properly
"""

from supabase import create_client, Client

# Configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

def clean_up_variety_names_and_duplicates():
    """Clean up rice variety names and handle duplicates"""
    
    print("=" * 80)
    print("CLEANING UP RICE VARIETY NAMES AND HANDLING DUPLICATES")
    print("=" * 80)
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Get all rice varieties
        result = supabase.table("varieties").select("id, variety_name, ecology, table_source").eq("crop_name", "rice").execute()
        
        if not result.data:
            print("No rice varieties found in database")
            return
        
        print(f"Found {len(result.data)} rice varieties")
        
        # Group varieties by cleaned name
        varieties_by_name = {}
        for variety in result.data:
            cleaned_name = variety['variety_name'].strip().rstrip('.,;')
            if cleaned_name not in varieties_by_name:
                varieties_by_name[cleaned_name] = []
            varieties_by_name[cleaned_name].append(variety)
        
        # Handle duplicates and clean names
        cleaned_count = 0
        for cleaned_name, varieties in varieties_by_name.items():
            if len(varieties) > 1:
                print(f"\nFound {len(varieties)} varieties with name '{cleaned_name}':")
                for variety in varieties:
                    print(f"  - {variety['variety_name']} (ID: {variety['id']}, Ecology: {variety['ecology']})")
                
                # Keep the one with the cleanest name and best ecology info
                best_variety = None
                for variety in varieties:
                    if variety['variety_name'] == cleaned_name and variety['ecology'] != 'General':
                        best_variety = variety
                        break
                
                if not best_variety:
                    best_variety = varieties[0]
                
                print(f"  Keeping: {best_variety['variety_name']} (ID: {best_variety['id']})")
                
                # Update the kept variety if needed
                if best_variety['variety_name'] != cleaned_name:
                    print(f"  Updating name: '{best_variety['variety_name']}' -> '{cleaned_name}'")
                    update_result = supabase.table("varieties").update({
                        "variety_name": cleaned_name
                    }).eq("id", best_variety['id']).execute()
                    
                    if update_result.data:
                        print(f"    SUCCESS: Updated variety name")
                        cleaned_count += 1
                    else:
                        print(f"    ERROR: Failed to update variety name")
                
                # Delete the duplicates
                varieties_to_delete = [v for v in varieties if v['id'] != best_variety['id']]
                for variety in varieties_to_delete:
                    try:
                        delete_result = supabase.table("varieties").delete().eq("id", variety['id']).execute()
                        if delete_result.data:
                            print(f"    SUCCESS: Deleted duplicate {variety['variety_name']}")
                        else:
                            print(f"    ERROR: Failed to delete {variety['variety_name']}")
                    except Exception as e:
                        print(f"    ERROR: Error deleting {variety['variety_name']}: {e}")
            
            elif len(varieties) == 1:
                variety = varieties[0]
                if variety['variety_name'] != cleaned_name:
                    print(f"Cleaning: '{variety['variety_name']}' -> '{cleaned_name}'")
                    
                    update_result = supabase.table("varieties").update({
                        "variety_name": cleaned_name
                    }).eq("id", variety['id']).execute()
                    
                    if update_result.data:
                        print(f"  SUCCESS: Updated variety name")
                        cleaned_count += 1
                    else:
                        print(f"  ERROR: Failed to update variety name")
        
        print(f"\nCleaned {cleaned_count} variety names")
        
        # Show final count
        final_result = supabase.table("varieties").select("id").eq("crop_name", "rice").execute()
        print(f"Final rice variety count: {len(final_result.data)}")
        
        # Show final varieties
        print("\nFinal rice varieties:")
        varieties_result = supabase.table("varieties").select("variety_name, ecology, table_source").eq("crop_name", "rice").order("variety_name").execute()
        
        for variety in varieties_result.data:
            print(f"  - {variety['variety_name']} ({variety['ecology']}) - {variety['table_source']}")
        
    except Exception as e:
        print(f"ERROR: {e}")

def main():
    clean_up_variety_names_and_duplicates()

if __name__ == "__main__":
    main()
