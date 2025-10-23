#!/usr/bin/env python3
"""Debug the constraint issue"""

import json

# Test the data that's being inserted
variety = {
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
}

print("Testing data values:")
print(f"yield_potential: '{variety['yield_potential']}'")
print(f"drought_tolerance: '{variety['drought_tolerance']}'")
print(f"type: '{variety['type']}'")

# Test JSON serialization
print(f"\nJSON serialization:")
print(f"disease_resistance: {json.dumps(variety['disease_resistance'])}")
print(f"planting_months: {json.dumps(variety['planting_months'])}")
print(f"harvest_months: {json.dumps(variety['harvest_months'])}")

# Test the exact values that would be inserted
values = (
    1,  # maize_crop_id
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
)

print(f"\nValues to be inserted:")
for i, val in enumerate(values):
    print(f"{i}: {repr(val)}")
