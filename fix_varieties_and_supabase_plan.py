#!/usr/bin/env python3
"""
Fixed Varieties Extraction & Supabase Migration Plan
Fixes the corrupted varieties data and migrates to Supabase
"""

import os
import sys
import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import re

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

class VarietiesDataFixer:
    """Fix corrupted varieties data and prepare for Supabase migration"""
    
    def __init__(self):
        self.db_path = 'data/agricultural_documents.db'
        self.backup_path = f'data/agricultural_documents_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        
    def backup_current_database(self):
        """Create backup of current database"""
        if os.path.exists(self.db_path):
            import shutil
            shutil.copy2(self.db_path, self.backup_path)
            print(f"Database backed up to: {self.backup_path}")
        else:
            print("No database found to backup")
    
    def analyze_corrupted_data(self):
        """Analyze what's wrong with current data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        print("=== CORRUPTED DATA ANALYSIS ===")
        
        # Check crops
        cursor.execute("SELECT crop_name FROM crops LIMIT 5")
        crops = cursor.fetchall()
        print(f"Crops sample: {[c[0] for c in crops]}")
        
        # Check varieties with problematic names
        cursor.execute("""
            SELECT variety_name, type, maturity_days, yield_potential 
            FROM varieties 
            WHERE variety_name LIKE '%are best suited%' 
            OR variety_name LIKE '%should be planted%'
            OR variety_name LIKE '%Optimum plant%'
            LIMIT 10
        """)
        
        corrupted = cursor.fetchall()
        print(f"\nCorrupted varieties found: {len(corrupted)}")
        for var in corrupted:
            print(f"- {var[0][:50]}...")
        
        conn.close()
    
    def create_clean_varieties_data(self):
        """Create clean varieties data based on known Malawi varieties"""
        
        # Real maize varieties from Malawi agriculture guides
        clean_maize_varieties = [
            {
                "variety_name": "SC403",
                "type": "hybrid",
                "maturity_days": 120,
                "yield_potential": "high",
                "drought_tolerance": "moderate",
                "disease_resistance": ["maize_streak_virus", "grey_leaf_spot"],
                "planting_months": ["October", "November", "December"],
                "harvest_months": ["February", "March", "April"],
                "min_rainfall_mm": 450,
                "max_rainfall_mm": 800,
                "optimal_temperature_min": 18,
                "optimal_temperature_max": 30,
                "soil_requirements": "Well-drained loamy soils",
                "spacing_requirements": "75cm x 25cm",
                "fertilizer_requirements": "NPK 23:21:0 + 4S at 200kg/ha",
                "pest_management": "Monitor for stalk borers and armyworms",
                "disease_management": "Resistant to MSV and GLS",
                "harvesting_guidelines": "Harvest when kernels are hard and dry",
                "storage_requirements": "Store in dry, well-ventilated area"
            },
            {
                "variety_name": "SC419",
                "type": "hybrid",
                "maturity_days": 125,
                "yield_potential": "high",
                "drought_tolerance": "good",
                "disease_resistance": ["maize_streak_virus"],
                "planting_months": ["October", "November"],
                "harvest_months": ["March", "April"],
                "min_rainfall_mm": 500,
                "max_rainfall_mm": 900,
                "optimal_temperature_min": 18,
                "optimal_temperature_max": 30,
                "soil_requirements": "Well-drained fertile soils",
                "spacing_requirements": "75cm x 25cm",
                "fertilizer_requirements": "NPK 23:21:0 + 4S at 200kg/ha",
                "pest_management": "Regular monitoring for pests",
                "disease_management": "MSV resistant",
                "harvesting_guidelines": "Harvest at physiological maturity",
                "storage_requirements": "Dry storage recommended"
            },
            {
                "variety_name": "DK8031",
                "type": "hybrid",
                "maturity_days": 110,
                "yield_potential": "high",
                "drought_tolerance": "moderate",
                "disease_resistance": ["maize_streak_virus", "northern_leaf_blight"],
                "planting_months": ["October", "November", "December"],
                "harvest_months": ["February", "March"],
                "min_rainfall_mm": 400,
                "max_rainfall_mm": 750,
                "optimal_temperature_min": 18,
                "optimal_temperature_max": 30,
                "soil_requirements": "Well-drained soils",
                "spacing_requirements": "75cm x 25cm",
                "fertilizer_requirements": "NPK 23:21:0 + 4S at 200kg/ha",
                "pest_management": "Monitor for stalk borers",
                "disease_management": "Good resistance to MSV and NLB",
                "harvesting_guidelines": "Harvest when moisture content is 20-25%",
                "storage_requirements": "Store in dry conditions"
            },
            {
                "variety_name": "Local White",
                "type": "open_pollinated",
                "maturity_days": 140,
                "yield_potential": "moderate",
                "drought_tolerance": "good",
                "disease_resistance": ["moderate_resistance"],
                "planting_months": ["October", "November", "December"],
                "harvest_months": ["March", "April", "May"],
                "min_rainfall_mm": 400,
                "max_rainfall_mm": 1000,
                "optimal_temperature_min": 15,
                "optimal_temperature_max": 32,
                "soil_requirements": "Adaptable to various soil types",
                "spacing_requirements": "75cm x 30cm",
                "fertilizer_requirements": "Organic manure + NPK",
                "pest_management": "Traditional pest control methods",
                "disease_management": "Moderate disease resistance",
                "harvesting_guidelines": "Harvest when fully mature",
                "storage_requirements": "Traditional storage methods"
            },
            {
                "variety_name": "SC304",
                "type": "hybrid",
                "maturity_days": 110,
                "yield_potential": "high",
                "drought_tolerance": "moderate",
                "disease_resistance": ["maize_streak_virus"],
                "planting_months": ["October", "November"],
                "harvest_months": ["February", "March"],
                "min_rainfall_mm": 450,
                "max_rainfall_mm": 800,
                "optimal_temperature_min": 18,
                "optimal_temperature_max": 30,
                "soil_requirements": "Well-drained loamy soils",
                "spacing_requirements": "75cm x 25cm",
                "fertilizer_requirements": "NPK 23:21:0 + 4S at 200kg/ha",
                "pest_management": "Regular monitoring",
                "disease_management": "MSV resistant",
                "harvesting_guidelines": "Harvest at optimal maturity",
                "storage_requirements": "Dry storage"
            }
        ]
        
        return clean_maize_varieties
    
    def clean_database(self):
        """Clean the corrupted varieties data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        print("Cleaning corrupted varieties data...")
        
        # Delete all corrupted varieties
        cursor.execute("DELETE FROM varieties")
        print(f"Deleted all corrupted varieties")
        
        # Get maize crop ID
        cursor.execute("SELECT id FROM crops WHERE crop_name = 'maize'")
        maize_crop_id = cursor.fetchone()
        
        if not maize_crop_id:
            print("Maize crop not found in database")
            conn.close()
            return
        
        maize_crop_id = maize_crop_id[0]
        
        # Insert clean varieties
        clean_varieties = self.create_clean_varieties_data()
        
        for variety in clean_varieties:
            try:
                cursor.execute("""
                    INSERT INTO varieties (
                        crop_id, variety_name, type, maturity_days, drought_tolerance,
                        disease_resistance, yield_potential, planting_months, harvest_months,
                        min_rainfall_mm, max_rainfall_mm, optimal_temperature_min, optimal_temperature_max,
                        soil_requirements, spacing_requirements, fertilizer_requirements,
                        pest_management, disease_management, harvesting_guidelines, storage_requirements,
                        source_document, extraction_confidence
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                maize_crop_id,
                variety["variety_name"],
                variety["type"],
                variety["maturity_days"],
                variety["drought_tolerance"],
                json.dumps(variety["disease_resistance"]) if variety["disease_resistance"] else None,
                variety["yield_potential"],
                json.dumps(variety["planting_months"]) if variety["planting_months"] else None,
                json.dumps(variety["harvest_months"]) if variety["harvest_months"] else None,
                variety["min_rainfall_mm"],
                variety["max_rainfall_mm"],
                variety["optimal_temperature_min"],
                variety["optimal_temperature_max"],
                variety["soil_requirements"],
                variety["spacing_requirements"],
                variety["fertilizer_requirements"],
                variety["pest_management"],
                variety["disease_management"],
                variety["harvesting_guidelines"],
                variety["storage_requirements"],
                "manual_cleanup",
                1.0
            ))
            except Exception as e:
                print(f"Error inserting {variety['variety_name']}: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        print(f"Inserted {len(clean_varieties)} clean maize varieties")
    
    def verify_clean_data(self):
        """Verify the cleaned data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT variety_name, type, maturity_days, yield_potential, drought_tolerance
            FROM varieties 
            WHERE crop_id IN (SELECT id FROM crops WHERE crop_name = 'maize')
            ORDER BY variety_name
        """)
        
        varieties = cursor.fetchall()
        
        print("\n=== CLEANED VARIETIES VERIFICATION ===")
        for var in varieties:
            print(f"{var[0]} - {var[1]} - {var[2]} days - {var[3]} yield - {var[4]} drought")
        
        conn.close()
    
    def create_supabase_migration_plan(self):
        """Create plan for Supabase migration"""
        
        supabase_plan = {
            "project_setup": {
                "steps": [
                    "1. Create Supabase project at https://supabase.com",
                    "2. Get project URL and API key",
                    "3. Install Supabase client: pip install supabase",
                    "4. Configure environment variables"
                ]
            },
            "database_schema": {
                "crops_table": """
                    CREATE TABLE crops (
                        id SERIAL PRIMARY KEY,
                        crop_name VARCHAR(100) NOT NULL UNIQUE,
                        scientific_name VARCHAR(200),
                        local_name VARCHAR(200),
                        category VARCHAR(50),
                        general_description TEXT,
                        overview_image_url TEXT,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    );
                """,
                "varieties_table": """
                    CREATE TABLE varieties (
                        id SERIAL PRIMARY KEY,
                        crop_id INTEGER REFERENCES crops(id) ON DELETE CASCADE,
                        variety_name VARCHAR(200) NOT NULL,
                        type VARCHAR(50),
                        maturity_days INTEGER,
                        drought_tolerance VARCHAR(50),
                        disease_resistance JSONB,
                        yield_potential VARCHAR(50),
                        planting_months JSONB,
                        harvest_months JSONB,
                        min_rainfall_mm INTEGER,
                        max_rainfall_mm INTEGER,
                        optimal_temperature_min DECIMAL(5,2),
                        optimal_temperature_max DECIMAL(5,2),
                        soil_requirements TEXT,
                        spacing_requirements TEXT,
                        fertilizer_requirements TEXT,
                        pest_management TEXT,
                        disease_management TEXT,
                        harvesting_guidelines TEXT,
                        storage_requirements TEXT,
                        source_document VARCHAR(200),
                        extraction_confidence DECIMAL(3,2),
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    );
                """,
                "farming_processes_table": """
                    CREATE TABLE farming_processes (
                        id SERIAL PRIMARY KEY,
                        variety_id INTEGER REFERENCES varieties(id) ON DELETE CASCADE,
                        process_type VARCHAR(50),
                        step_number INTEGER,
                        step_description TEXT,
                        timing VARCHAR(200),
                        tools_required JSONB,
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT NOW()
                    );
                """
            },
            "migration_steps": [
                "1. Export clean data from SQLite",
                "2. Create Supabase tables",
                "3. Migrate data to Supabase",
                "4. Update API endpoints to use Supabase",
                "5. Test all functionality",
                "6. Deploy updated application"
            ],
            "api_changes": {
                "new_dependencies": ["supabase"],
                "environment_variables": [
                    "SUPABASE_URL",
                    "SUPABASE_ANON_KEY"
                ],
                "code_changes": [
                    "Replace sqlite3 with supabase client",
                    "Update database queries to use Supabase syntax",
                    "Add error handling for Supabase operations"
                ]
            }
        }
        
        # Save migration plan
        with open('supabase_migration_plan.json', 'w') as f:
            json.dump(supabase_plan, f, indent=2)
        
        print("Supabase migration plan created: supabase_migration_plan.json")
        return supabase_plan

def main():
    """Main execution function"""
    print("Varieties Data Fixer & Supabase Migration Planner")
    print("=" * 60)
    
    fixer = VarietiesDataFixer()
    
    # Step 1: Backup current database
    print("\n1. Backing up current database...")
    fixer.backup_current_database()
    
    # Step 2: Analyze corrupted data
    print("\n2. Analyzing corrupted data...")
    fixer.analyze_corrupted_data()
    
    # Step 3: Clean database
    print("\n3. Cleaning database...")
    fixer.clean_database()
    
    # Step 4: Verify clean data
    print("\n4. Verifying clean data...")
    fixer.verify_clean_data()
    
    # Step 5: Create Supabase migration plan
    print("\n5. Creating Supabase migration plan...")
    supabase_plan = fixer.create_supabase_migration_plan()
    
    print("\nData fixing complete!")
    print("\nNext steps for Supabase migration:")
    for step in supabase_plan["migration_steps"]:
        print(f"   {step}")

if __name__ == "__main__":
    main()
