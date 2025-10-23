#!/usr/bin/env python3
"""
Check and Add Rice Crop to Database
Ensure rice crop exists in the crops table before inserting varieties
"""

from supabase import create_client, Client

# Configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

def check_and_add_rice_crop():
    """Check if rice crop exists and add if needed"""
    
    print("=" * 80)
    print("CHECKING RICE CROP IN DATABASE")
    print("=" * 80)
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Check if rice exists
        result = supabase.table("crops").select("id, crop_name").eq("crop_name", "rice").execute()
        
        if result.data:
            print(f"SUCCESS: Rice crop found: ID {result.data[0]['id']}")
            return result.data[0]['id']
        else:
            print("WARNING: Rice crop not found. Adding rice crop...")
            
            # Add rice crop
            rice_data = {
                "crop_name": "rice",
                "scientific_name": "Oryza sativa",
                "category": "cereal",
                "description": "Rice is one of the cereals grown along the Lakeshore, Phalombe plain, the Shire Valley and areas around Lake Chilwa either in irrigated rice or rainfed conditions.",
                "planting_season": "wet_season",
                "harvest_season": "dry_season",
                "water_requirements": "high",
                "soil_type": "clay_loam",
                "climate_zone": "tropical",
                "growth_period_days": 120,
                "yield_per_hectare": "4-6 tons",
                "nutritional_value": "High carbohydrate content",
                "uses": "Food, animal feed",
                "storage_requirements": "Dry storage at 14% moisture content",
                "pest_resistance": "moderate",
                "disease_resistance": "moderate",
                "drought_tolerance": "low",
                "flood_tolerance": "high",
                "fertilizer_requirements": "High nitrogen requirements",
                "irrigation_needs": "high",
                "spacing_requirements": "23cm x 15cm",
                "planting_method": "transplanting",
                "harvesting_method": "manual",
                "processing_requirements": "threshing, winnowing",
                "market_demand": "high",
                "price_per_kg": "variable",
                "export_potential": "high",
                "local_consumption": "high",
                "processing_equipment": "threshing machine, winnowing equipment",
                "storage_equipment": "silos, bags",
                "transportation_requirements": "dry transport",
                "quality_standards": "Grade 1 and Grade 2",
                "certification_requirements": "seed certification",
                "research_institutions": "Malawi Agricultural Research",
                "extension_services": "Ministry of Agriculture",
                "seed_suppliers": "ADMARC, NASFAM, Private Traders",
                "equipment_suppliers": "Agricultural equipment dealers",
                "training_requirements": "Rice cultivation training",
                "risk_factors": "Water shortage, pests, diseases",
                "mitigation_strategies": "Irrigation, pest control, disease management",
                "success_factors": "Proper water management, timely planting, good seed quality",
                "challenges": "Water management, pest control, market access",
                "opportunities": "Export market, value addition, processing",
                "sustainability": "moderate",
                "environmental_impact": "moderate",
                "economic_impact": "high",
                "social_impact": "high",
                "food_security": "high",
                "nutritional_benefits": "High energy content",
                "cultural_significance": "Staple food",
                "traditional_uses": "Food preparation",
                "modern_uses": "Food processing, animal feed",
                "value_chain": "Production, processing, marketing",
                "market_channels": "ADMARC, NASFAM, Private Traders",
                "price_volatility": "moderate",
                "seasonal_variation": "high",
                "yield_variability": "moderate",
                "input_costs": "moderate",
                "labor_requirements": "high",
                "mechanization_potential": "moderate",
                "technology_adoption": "moderate",
                "innovation_potential": "high",
                "research_priorities": "Variety development, water management",
                "policy_support": "moderate",
                "institutional_support": "moderate",
                "capacity_building": "needed",
                "knowledge_gaps": "Water management, pest control",
                "information_needs": "Market information, technical guidance",
                "extension_gaps": "Technical support, training",
                "infrastructure_needs": "Irrigation, storage, processing",
                "financial_needs": "Credit, insurance",
                "market_development": "needed",
                "value_addition": "opportunity",
                "processing_capacity": "limited",
                "storage_capacity": "limited",
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
                "coping_strategies": "limited",
                "recovery_potential": "moderate",
                "transformation_potential": "high",
                "development_potential": "high",
                "investment_potential": "high",
                "partnership_potential": "high",
                "collaboration_potential": "high",
                "networking_potential": "high",
                "scaling_potential": "high",
                "replication_potential": "high",
                "dissemination_potential": "high",
                "adoption_potential": "high",
                "impact_potential": "high",
                "sustainability_potential": "moderate",
                "resilience_potential": "moderate",
                "transformation_potential": "high"
            }
            
            result = supabase.table("crops").insert(rice_data).execute()
            
            if result.data:
                print(f"SUCCESS: Rice crop added successfully: ID {result.data[0]['id']}")
                return result.data[0]['id']
            else:
                print("ERROR: Failed to add rice crop")
                return None
                
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def main():
    crop_id = check_and_add_rice_crop()
    if crop_id:
        print(f"\nRice crop ID: {crop_id}")
        print("Ready to insert rice varieties!")
    else:
        print("\nFailed to ensure rice crop exists. Cannot proceed with variety insertion.")

if __name__ == "__main__":
    main()
