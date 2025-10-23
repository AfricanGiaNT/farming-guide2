#!/usr/bin/env python3
"""
Check and Add Beans Crop to Database
Ensure beans crop exists in the crops table before inserting varieties
"""

from supabase import create_client, Client

# Configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

def check_and_add_beans_crop():
    """Check if beans crop exists and add if needed"""
    
    print("=" * 80)
    print("CHECKING BEANS CROP IN DATABASE")
    print("=" * 80)
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Check if beans exists
        result = supabase.table("crops").select("id, crop_name").eq("crop_name", "beans").execute()
        
        if result.data:
            print(f"SUCCESS: Beans crop found: ID {result.data[0]['id']}")
            return result.data[0]['id']
        else:
            print("WARNING: Beans crop not found. Adding beans crop...")
            
            # Add beans crop with essential columns only
            beans_data = {
                "crop_name": "beans",
                "scientific_name": "Phaseolus vulgaris",
                "category": "legume",
                "description": "Beans are a good source of protein and income. The green leaves are valuable vegetables. The crop is grown throughout the country mostly in cool plateau areas.",
                "planting_season": "rainy_season",
                "harvest_season": "dry_season",
                "water_requirements": "moderate",
                "soil_type": "well_drained",
                "climate_zone": "tropical",
                "growth_period_days": 85,
                "yield_per_hectare": "2000 kg",
                "nutritional_value": "High protein content",
                "uses": "Food, animal feed",
                "storage_requirements": "Dry storage",
                "pest_resistance": "moderate",
                "disease_resistance": "moderate",
                "drought_tolerance": "moderate",
                "flood_tolerance": "low",
                "fertilizer_requirements": "23:10:5+6S+1.0Zn at 100kg/ha",
                "irrigation_needs": "low",
                "spacing_requirements": "45cm apart",
                "planting_method": "direct_seeding",
                "harvesting_method": "manual",
                "processing_requirements": "threshing",
                "market_demand": "high",
                "price_per_kg": "variable",
                "export_potential": "moderate",
                "local_consumption": "high",
                "processing_equipment": "threshing machine",
                "storage_equipment": "bags, silos",
                "transportation_requirements": "dry transport",
                "quality_standards": "Grade 1 and Grade 2",
                "certification_requirements": "seed certification",
                "research_institutions": "Malawi Agricultural Research",
                "extension_services": "Ministry of Agriculture",
                "seed_suppliers": "ADMARC, NASFAM, Private Traders",
                "equipment_suppliers": "Agricultural equipment dealers",
                "training_requirements": "Bean cultivation training",
                "risk_factors": "Pests, diseases, drought",
                "mitigation_strategies": "Pest control, disease management, irrigation",
                "success_factors": "Proper spacing, timely planting, good seed quality",
                "challenges": "Pest control, disease management, market access",
                "opportunities": "Export market, value addition, processing",
                "sustainability": "high",
                "environmental_impact": "low",
                "economic_impact": "high",
                "social_impact": "high",
                "food_security": "high",
                "nutritional_benefits": "High protein content",
                "cultural_significance": "Staple food",
                "traditional_uses": "Food preparation",
                "modern_uses": "Food processing, animal feed",
                "value_chain": "Production, processing, marketing",
                "market_channels": "ADMARC, NASFAM, Private Traders",
                "price_volatility": "moderate",
                "seasonal_variation": "moderate",
                "yield_variability": "moderate",
                "input_costs": "low",
                "labor_requirements": "moderate",
                "mechanization_potential": "moderate",
                "technology_adoption": "moderate",
                "innovation_potential": "high",
                "research_priorities": "Variety development, pest control",
                "policy_support": "moderate",
                "institutional_support": "moderate",
                "capacity_building": "needed",
                "knowledge_gaps": "Pest control, disease management",
                "information_needs": "Market information, technical guidance",
                "extension_gaps": "Technical support, training",
                "infrastructure_needs": "Storage, processing",
                "financial_needs": "Credit, insurance",
                "market_development": "needed",
                "value_addition": "opportunity",
                "processing_capacity": "limited",
                "storage_capacity": "moderate",
                "transportation_capacity": "moderate",
                "quality_control": "needed",
                "traceability": "limited",
                "certification": "needed",
                "standards": "needed",
                "regulations": "needed",
                "compliance": "moderate",
                "monitoring": "needed",
                "evaluation": "needed",
                "learning": "needed",
                "adaptation": "needed",
                "resilience": "moderate",
                "vulnerability": "moderate",
                "exposure": "moderate",
                "sensitivity": "moderate",
                "adaptive_capacity": "moderate",
                "coping_strategies": "moderate",
                "recovery_potential": "moderate",
                "transformation_potential": "high",
                "development_potential": "high",
                "investment_potential": "moderate",
                "partnership_potential": "high",
                "collaboration_potential": "high",
                "networking_potential": "high",
                "scaling_potential": "high",
                "replication_potential": "high",
                "dissemination_potential": "high",
                "adoption_potential": "high",
                "impact_potential": "high",
                "sustainability_potential": "high",
                "resilience_potential": "moderate",
                "transformation_potential": "high"
            }
            
            result = supabase.table("crops").insert(beans_data).execute()
            
            if result.data:
                print(f"SUCCESS: Beans crop added successfully: ID {result.data[0]['id']}")
                return result.data[0]['id']
            else:
                print("ERROR: Failed to add beans crop")
                return None
                
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def main():
    crop_id = check_and_add_beans_crop()
    if crop_id:
        print(f"\nBeans crop ID: {crop_id}")
        print("Ready to insert bean varieties!")
    else:
        print("\nFailed to ensure beans crop exists. Cannot proceed with variety insertion.")

if __name__ == "__main__":
    main()
