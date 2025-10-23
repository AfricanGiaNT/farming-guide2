#!/usr/bin/env python3
"""
Migrate clean varieties data from SQLite to Supabase
"""

import sqlite3
import json
import os
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

class SupabaseMigrator:
    """Migrate data from SQLite to Supabase"""
    
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.sqlite_db = 'data/agricultural_documents.db'
    
    def migrate_crops(self):
        """Migrate crops data"""
        print("Migrating crops...")
        
        conn = sqlite3.connect(self.sqlite_db)
        cursor = conn.cursor()
        
        # Get all crops
        cursor.execute("SELECT crop_name, scientific_name, local_name, category, general_description, overview_image_url FROM crops")
        crops = cursor.fetchall()
        
        migrated_crops = []
        for crop in crops:
            crop_data = {
                "crop_name": crop[0],
                "scientific_name": crop[1],
                "local_name": crop[2],
                "category": crop[3],
                "general_description": crop[4],
                "overview_image_url": crop[5]
            }
            
            try:
                result = self.supabase.table("crops").insert(crop_data).execute()
                migrated_crops.append(crop_data)
                print(f"  + Migrated crop: {crop[0]}")
            except Exception as e:
                print(f"  - Error migrating crop {crop[0]}: {e}")
        
        conn.close()
        print(f"Migrated {len(migrated_crops)} crops")
        return migrated_crops
    
    def migrate_varieties(self):
        """Migrate varieties data"""
        print("Migrating varieties...")
        
        conn = sqlite3.connect(self.sqlite_db)
        cursor = conn.cursor()
        
        # Get maize crop ID from Supabase
        maize_result = self.supabase.table("crops").select("id").eq("crop_name", "maize").execute()
        if not maize_result.data:
            print("Error: Maize crop not found in Supabase")
            return []
        
        maize_crop_id = maize_result.data[0]["id"]
        print(f"Found maize crop ID: {maize_crop_id}")
        
        # Get varieties from SQLite
        cursor.execute("""
            SELECT variety_name, type, maturity_days, drought_tolerance, disease_resistance,
                   yield_potential, planting_months, harvest_months, min_rainfall_mm, max_rainfall_mm,
                   optimal_temperature_min, optimal_temperature_max, soil_requirements,
                   spacing_requirements, fertilizer_requirements, pest_management,
                   disease_management, harvesting_guidelines, storage_requirements,
                   source_document, extraction_confidence
            FROM varieties 
            WHERE crop_id IN (SELECT id FROM crops WHERE crop_name = 'maize')
        """)
        
        varieties = cursor.fetchall()
        
        migrated_varieties = []
        for variety in varieties:
            variety_data = {
                "crop_id": maize_crop_id,
                "variety_name": variety[0],
                "type": variety[1],
                "maturity_days": variety[2],
                "drought_tolerance": variety[3],
                "disease_resistance": json.loads(variety[4]) if variety[4] else None,
                "yield_potential": variety[5],
                "planting_months": json.loads(variety[6]) if variety[6] else None,
                "harvest_months": json.loads(variety[7]) if variety[7] else None,
                "min_rainfall_mm": variety[8],
                "max_rainfall_mm": variety[9],
                "optimal_temperature_min": variety[10],
                "optimal_temperature_max": variety[11],
                "soil_requirements": variety[12],
                "spacing_requirements": variety[13],
                "fertilizer_requirements": variety[14],
                "pest_management": variety[15],
                "disease_management": variety[16],
                "harvesting_guidelines": variety[17],
                "storage_requirements": variety[18],
                "source_document": variety[19],
                "extraction_confidence": variety[20]
            }
            
            try:
                result = self.supabase.table("varieties").insert(variety_data).execute()
                migrated_varieties.append(variety_data)
                print(f"  + Migrated variety: {variety[0]}")
            except Exception as e:
                print(f"  - Error migrating variety {variety[0]}: {e}")
        
        conn.close()
        print(f"Migrated {len(migrated_varieties)} varieties")
        return migrated_varieties
    
    def verify_migration(self):
        """Verify the migration was successful"""
        print("Verifying migration...")
        
        # Check crops
        crops_result = self.supabase.table("crops").select("*").execute()
        print(f"Crops in Supabase: {len(crops_result.data)}")
        
        # Check varieties
        varieties_result = self.supabase.table("varieties").select("*").execute()
        print(f"Varieties in Supabase: {len(varieties_result.data)}")
        
        # Show maize varieties
        maize_varieties = self.supabase.table("varieties").select("variety_name, type, maturity_days, yield_potential").eq("crop_id", 1).execute()
        print("\nMaize varieties in Supabase:")
        for variety in maize_varieties.data:
            print(f"  - {variety['variety_name']} ({variety['type']}) - {variety['maturity_days']} days - {variety['yield_potential']} yield")
    
    def run_migration(self):
        """Run the complete migration"""
        print("Starting Supabase migration...")
        print("=" * 50)
        
        # Migrate crops
        crops = self.migrate_crops()
        
        # Migrate varieties
        varieties = self.migrate_varieties()
        
        # Verify migration
        self.verify_migration()
        
        print("\nMigration completed successfully!")
        print(f"Migrated {len(crops)} crops and {len(varieties)} varieties")

def main():
    """Main execution function"""
    migrator = SupabaseMigrator()
    migrator.run_migration()

if __name__ == "__main__":
    main()
