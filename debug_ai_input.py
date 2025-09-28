#!/usr/bin/env python3
"""
Debug script to see what the AI is receiving as input
"""

import sys
sys.path.append('/Users/trevorchimtengo/farming-guide2')
from scripts.handlers.varieties_handler import VarietiesHandler

def debug_ai_input():
    """Debug what the AI is receiving as input."""
    print("🔍 Debugging AI Input")
    print("=" * 50)
    
    try:
        handler = VarietiesHandler()
        
        # Get search results
        search_results = handler.search_varieties_knowledge('groundnut varieties', top_k=10)
        print(f"✅ Found {len(search_results)} search results")
        
        # Show first few search results
        for i, result in enumerate(search_results[:3]):
            print(f"\n--- Search Result {i+1} ---")
            print(f"Score: {result.get('score', 'N/A')}")
            print(f"Source: {result.get('source', 'N/A')}")
            print(f"Content preview: {result['content'][:200]}...")
            
            # Check if it contains variety names
            content_lower = result['content'].lower()
            variety_names = ['cg7', 'cg8', 'cg9', 'chalimbana', 'nsinjiro', 'kakoma', 'chitala', 'baka']
            found_varieties = [name for name in variety_names if name in content_lower]
            print(f"Contains variety names: {found_varieties}")
        
        # Test AI parsing
        print(f"\n🤖 Testing AI parsing...")
        ai_result = handler.parse_varieties_with_ai(search_results, 'groundnut', max_varieties=10)
        print(f"AI returned {len(ai_result.get('varieties', []))} varieties")
        
        for i, variety in enumerate(ai_result.get('varieties', [])[:5]):
            print(f"Variety {i+1}: {variety.get('name', 'No name')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_ai_input()
