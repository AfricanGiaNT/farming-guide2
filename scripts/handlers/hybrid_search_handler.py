#!/usr/bin/env python3
"""
Hybrid Search Handler for Varieties System
Combines keyword search (varieties table) with semantic search (documents table)
"""

import sqlite3
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
import re
from collections import defaultdict

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.handlers.varieties_handler import VarietiesHandler

class HybridSearchHandler:
    """Handles hybrid search combining keyword and semantic search"""
    
    def __init__(self, db_path: str = "data/agricultural_documents.db"):
        self.db_path = db_path
        if not os.path.isabs(self.db_path):
            self.db_path = os.path.join(project_root, self.db_path)
        
        # Initialize the existing varieties handler for semantic search
        self.varieties_handler = VarietiesHandler()
        
        # Search weights
        self.KEYWORD_WEIGHT = 0.7
        self.SEMANTIC_WEIGHT = 0.3
        
        # Cache for frequent queries
        self._search_cache = {}
        
    def get_db_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def keyword_search_varieties(self, query: str, crop_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search varieties table directly using keyword matching
        Returns structured variety data with high confidence scores
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Normalize query terms and handle variety name patterns
            query_terms = [term.strip().lower() for term in query.split() if len(term.strip()) > 1]
            
            # Special handling for variety codes like "CG7" -> "CG 7"
            processed_terms = []
            for term in query_terms:
                processed_terms.append(term)
                # If term looks like a variety code (letters + numbers), also try with space
                if re.match(r'^[a-z]+\d+$', term):
                    # Split letters and numbers: "cg7" -> "cg 7"
                    match = re.match(r'^([a-z]+)(\d+)$', term)
                    if match:
                        spaced_term = f"{match.group(1)} {match.group(2)}"
                        processed_terms.append(spaced_term)
            
            query_terms = list(set(processed_terms))  # Remove duplicates
            
            # Build SQL query for variety name matching
            variety_conditions = []
            params = []
            
            # Add crop filter
            variety_conditions.append("LOWER(crop_name) = ?")
            params.append(crop_name.lower())
            
            # Add variety name matching conditions (use OR for multiple terms)
            if query_terms:
                name_conditions = []
                for term in query_terms:
                    name_conditions.append("(LOWER(variety_name) LIKE ? OR LOWER(variety_type) LIKE ?)")
                    params.extend([f"%{term}%", f"%{term}%"])
                
                # Combine name conditions with OR
                variety_conditions.append(f"({' OR '.join(name_conditions)})")
            
            # Simplified query without complex scoring
            sql_query = f"""
                SELECT 
                    crop_name,
                    variety_name,
                    variety_type,
                    yield_potential,
                    maturity_days,
                    weather_requirements,
                    soil_requirements,
                    growing_areas,
                    disease_resistance,
                    planting_time,
                    source_document
                FROM varieties 
                WHERE {' AND '.join(variety_conditions)}
                ORDER BY variety_name ASC
                LIMIT ?
            """
            
            all_params = params + [limit]
            
            cursor.execute(sql_query, all_params)
            results = cursor.fetchall()
            
            # Convert to structured format
            varieties = []
            for i, row in enumerate(results):
                # Calculate simple relevance score based on position and name match
                main_term = query_terms[0] if query_terms else ""
                if main_term.lower() in row[1].lower():
                    score = 1.0 - (i * 0.1)  # Exact match gets high score
                else:
                    score = 0.8 - (i * 0.1)  # Partial match gets lower score
                
                variety = {
                    'crop_name': row[0],
                    'name': row[1],
                    'variety_type': row[2] or 'Not specified',
                    'yield_potential': row[3] or 'Not specified',
                    'maturity_days': row[4],
                    'weather_requirements': row[5] or 'Not specified',
                    'soil_requirements': row[6] or 'Not specified',
                    'growing_areas': row[7] or 'Not specified',
                    'disease_resistance': row[8] or 'Not specified',
                    'planting_time': row[9] or 'Not specified',
                    'source_document': row[10] or 'Database',
                    'score': max(score, 0.1),
                    'search_method': 'keyword_varieties_table'
                }
                varieties.append(variety)
            
            return varieties
            
        except Exception as e:
            print(f"Error in keyword search: {e}")
            return []
        finally:
            conn.close()
    
    def semantic_search_documents(self, query: str, crop_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Use existing semantic search on documents table
        Returns document-based results that need AI parsing
        """
        try:
            # Use existing varieties handler for semantic search
            search_results = self.varieties_handler.search_varieties_knowledge(
                f"{crop_name} {query}", 
                top_k=limit
            )
            
            # Convert to standard format and add metadata
            formatted_results = []
            for i, result in enumerate(search_results):
                if hasattr(result, 'get'):
                    # Dictionary-like result
                    content = result.get('content', str(result))
                    source = result.get('source', 'Unknown')
                    score = result.get('score', 0.5)
                else:
                    # String or other format
                    content = str(result)
                    source = 'Document search'
                    score = max(0.5 - (i * 0.1), 0.1)  # Decreasing score by position
                
                formatted_results.append({
                    'content': content,
                    'source': source,
                    'score': score,
                    'search_method': 'semantic_documents'
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []
    
    def combine_and_rank_results(self, keyword_results: List[Dict], semantic_results: List[Dict]) -> List[Dict[str, Any]]:
        """
        Combine keyword and semantic results with weighted scoring
        """
        combined_results = []
        
        # Add keyword results with higher weight
        for result in keyword_results:
            result['final_score'] = result['score'] * self.KEYWORD_WEIGHT
            result['result_type'] = 'structured_variety'
            combined_results.append(result)
        
        # Add semantic results with lower weight (need AI parsing)
        for result in semantic_results:
            result['final_score'] = result['score'] * self.SEMANTIC_WEIGHT
            result['result_type'] = 'document_content'
            combined_results.append(result)
        
        # Sort by final score descending
        combined_results.sort(key=lambda x: x['final_score'], reverse=True)
        
        return combined_results
    
    def hybrid_search(self, query: str, crop_name: str, limit: int = 10) -> Dict[str, Any]:
        """
        Main hybrid search function combining keyword and semantic search
        """
        # Check cache first
        cache_key = f"{query}_{crop_name}_{limit}"
        if cache_key in self._search_cache:
            return self._search_cache[cache_key]
        
        try:
            # 1. Keyword search on varieties table (fast, high precision)
            keyword_results = self.keyword_search_varieties(query, crop_name, limit=limit//2 + 2)
            
            # 2. Semantic search on documents table (comprehensive, needs parsing)
            semantic_results = self.semantic_search_documents(query, crop_name, limit=limit//2 + 2)
            
            # 3. Combine and rank results
            combined_results = self.combine_and_rank_results(keyword_results, semantic_results)
            
            # 4. Process semantic results that need AI parsing
            final_varieties = []
            semantic_content_to_parse = []
            
            for result in combined_results[:limit]:
                if result['result_type'] == 'structured_variety':
                    # Already structured variety data
                    final_varieties.append(result)
                elif result['result_type'] == 'document_content':
                    # Needs AI parsing
                    semantic_content_to_parse.append(result)
            
            # 5. Parse semantic results if needed
            if semantic_content_to_parse and len(final_varieties) < limit:
                try:
                    # Prepare content for AI parsing
                    mock_search_results = [{
                        'content': result['content'],
                        'source': result['source'],
                        'score': result['score']
                    } for result in semantic_content_to_parse]
                    
                    # Use AI to parse varieties from document content
                    parsed_info = self.varieties_handler.parse_varieties_with_ai(
                        mock_search_results, 
                        crop_name, 
                        max_varieties=limit - len(final_varieties)
                    )
                    
                    # Add parsed varieties
                    for variety in parsed_info.get('varieties', []):
                        if variety.get('name'):
                            variety_data = {
                                'crop_name': crop_name,
                                'name': variety.get('name'),
                                'variety_type': variety.get('variety_type', 'Not specified'),
                                'yield_potential': variety.get('yield_potential', variety.get('yield', 'Not specified')),
                                'maturity_days': variety.get('maturity_days'),
                                'weather_requirements': variety.get('weather_requirements', variety.get('weather', 'Not specified')),
                                'soil_requirements': variety.get('soil_requirements', variety.get('soil', 'Not specified')),
                                'growing_areas': variety.get('growing_areas', variety.get('areas', 'Not specified')),
                                'disease_resistance': variety.get('disease_resistance', 'Not specified'),
                                'planting_time': variety.get('planting_time', 'Not specified'),
                                'source_document': 'AI parsed from documents',
                                'score': 0.7,  # Medium confidence for AI parsed
                                'final_score': 0.7 * self.SEMANTIC_WEIGHT,
                                'search_method': 'ai_parsed_semantic',
                                'result_type': 'ai_parsed_variety'
                            }
                            final_varieties.append(variety_data)
                
                except Exception as e:
                    print(f"Error in AI parsing: {e}")
            
            # 6. Final ranking and limiting
            final_varieties.sort(key=lambda x: x['final_score'], reverse=True)
            final_varieties = final_varieties[:limit]
            
            # 7. Prepare response
            response = {
                'crop': crop_name,
                'query': query,
                'varieties': final_varieties,
                'total_found': len(final_varieties),
                'search_methods_used': list(set([v.get('search_method', 'unknown') for v in final_varieties])),
                'keyword_results_count': len(keyword_results),
                'semantic_results_count': len(semantic_results),
                'search_time_ms': 0  # Could add timing if needed
            }
            
            # Cache the result
            self._search_cache[cache_key] = response
            
            return response
            
        except Exception as e:
            print(f"Error in hybrid search: {e}")
            return {
                'crop': crop_name,
                'query': query,
                'varieties': [],
                'total_found': 0,
                'error': str(e)
            }
    
    def clear_cache(self):
        """Clear search cache"""
        self._search_cache.clear()

# Test function
def test_hybrid_search():
    """Test the hybrid search functionality"""
    handler = HybridSearchHandler()
    
    # Test with groundnut varieties
    print("Testing hybrid search with groundnut varieties...")
    result = handler.hybrid_search("CG7 varieties", "groundnut", limit=5)
    
    print(f"Found {result['total_found']} varieties")
    print(f"Search methods used: {result.get('search_methods_used', [])}")
    print(f"Keyword results: {result.get('keyword_results_count', 0)}")
    print(f"Semantic results: {result.get('semantic_results_count', 0)}")
    
    for i, variety in enumerate(result['varieties'][:3]):
        print(f"{i+1}. {variety['name']} (Score: {variety['final_score']:.3f}, Method: {variety.get('search_method', 'unknown')})")
    
    return result

if __name__ == "__main__":
    test_hybrid_search()
