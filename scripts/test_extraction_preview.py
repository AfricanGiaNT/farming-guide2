#!/usr/bin/env python3
"""
Preview what will be extracted - TEST MODE
Shows varieties that would be extracted WITHOUT inserting to database
"""

import sys
sys.path.insert(0, 'scripts')

from improved_variety_extractor import ImprovedVarietyExtractor, CHAPTER3_CROPS

def preview_extraction():
    """Preview extraction for all crops"""
    print("=" * 80)
    print("EXTRACTION PREVIEW - TEST MODE")
    print("No data will be inserted into database")
    print("=" * 80)
    
    extractor = ImprovedVarietyExtractor()
    
    all_results = {}
    
    for crop_name, page_range in CHAPTER3_CROPS.items():
        try:
            varieties = extractor.extract_crop_varieties(crop_name, page_range)
            all_results[crop_name] = sorted(varieties)
            
            if varieties:
                print(f"\n  Extracted {len(varieties)} varieties:")
                for v in sorted(varieties):
                    print(f"    - {v}")
        except Exception as e:
            print(f"\n  ERROR: {e}")
            all_results[crop_name] = []
    
    # Summary
    print("\n" + "=" * 80)
    print("PREVIEW SUMMARY")
    print("=" * 80)
    
    total = sum(len(v) for v in all_results.values())
    print(f"\nTotal varieties found: {total}")
    print("\nBreakdown:")
    for crop, varieties in sorted(all_results.items()):
        print(f"  {crop}: {len(varieties)} varieties")
        if varieties:
            print(f"    Examples: {', '.join(varieties[:3])}")
    
    # Quality check
    print("\n" + "=" * 80)
    print("QUALITY CHECK")
    print("=" * 80)
    
    suspicious = []
    for crop, varieties in all_results.items():
        for v in varieties:
            # Flag suspicious patterns
            if len(v) < 3 or len(v) > 30:
                suspicious.append(f"{crop}: {v} (length issue)")
            elif any(word in v.lower() for word in ['and', 'or', 'total', 'average']):
                suspicious.append(f"{crop}: {v} (contains reserved word)")
    
    if suspicious:
        print("\nSuspicious entries found:")
        for s in suspicious[:10]:
            print(f"  WARNING: {s}")
    else:
        print("\nNo suspicious entries detected - quality looks good!")
    
    print("\n" + "=" * 80)
    print("Ready to run full extraction? Review results above.")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    preview_extraction()



