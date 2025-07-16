"""
Varieties handler for the Agricultural Advisor Bot.
Handles variety-specific information and recommendations using knowledge base.
"""
from telegram import Update
from telegram.ext import ContextTypes
from scripts.utils.logger import logger
from scripts.data_pipeline.embedding_generator import EmbeddingGenerator
from migrate_to_sqlite_vector import SQLiteVectorDatabase
from scripts.weather_engine.coordinate_handler import coordinate_handler
# Phase 2: Historical Weather Integration
from scripts.weather_engine.historical_weather_api import historical_weather_api
from scripts.weather_engine.enhanced_rainfall_analyzer import enhanced_rainfall_analyzer
import sqlite3
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI
import os
import re
import time
from datetime import datetime, timedelta
import calendar


class VarietiesHandler:
    """Handler for crop variety information and recommendations."""
    
    def __init__(self):
        """Initialize varieties handler."""
        self.db_path = "data/farming_guide_vectors.db"
        self.embedding_generator = EmbeddingGenerator()
        
        # Phase 2: Weather analysis components
        self.historical_weather_api = historical_weather_api
        self.enhanced_rainfall_analyzer = enhanced_rainfall_analyzer
        self.weather_cache = {}  # Simple in-memory cache for weather data
        self.cache_timeout = 3600  # 1 hour cache timeout
        
        # Phase 5: Planting calendar data
        self.planting_months = {
            'primary_planting': ['October', 'November', 'December', 'January'],
            'secondary_planting': ['February', 'March'],
            'dry_season_planting': ['April', 'May', 'June', 'July'],
            'preparation_months': ['August', 'September']
        }
        
        self.crop_maturity_periods = {
            'maize': {'early': 90, 'medium': 120, 'late': 150},
            'groundnut': {'early': 90, 'medium': 105, 'late': 120},
            'bean': {'early': 60, 'medium': 90, 'late': 120},
            'soybean': {'early': 90, 'medium': 120, 'late': 150},
            'sorghum': {'early': 100, 'medium': 120, 'late': 150},
            'millet': {'early': 90, 'medium': 120, 'late': 150},
            'cassava': {'early': 360, 'medium': 480, 'late': 600},
            'sweet_potato': {'early': 90, 'medium': 120, 'late': 150}
        }
        
        # Initialize OpenAI client
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                # Try to load from config file
                config_path = "config/openai_key.env"
                if os.path.exists(config_path):
                    with open(config_path, 'r') as f:
                        for line in f:
                            if line.startswith('OPENAI_API_KEY='):
                                api_key = line.split('=', 1)[1].strip()
                                break
            
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
            else:
                self.openai_client = None
                logger.warning("OpenAI API key not found - AI parsing will be disabled")
                
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {e}")
            self.openai_client = None
            
        logger.info("Varieties handler initialized with weather integration and planting calendar")
    
    def search_varieties_knowledge(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search the knowledge base for variety-specific information.
        
        Args:
            query: Search query about varieties
            top_k: Number of results to return
            
        Returns:
            List of search results with content and scores
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_generator.generate_query_embedding(query)
            if not query_embedding:
                logger.error("Failed to generate query embedding")
                return []
            
            # Connect to SQLite database
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all documents and calculate similarity
            cursor.execute("SELECT content, source, metadata, embedding FROM documents WHERE length(content) > 50")
            results = []
            query_vec = np.array(query_embedding)
            
            for row in cursor.fetchall():
                try:
                    doc_embedding = json.loads(row['embedding'])
                    doc_vec = np.array(doc_embedding)
                    
                    # Cosine similarity
                    similarity = np.dot(query_vec, doc_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(doc_vec))
                    
                    results.append({
                        'content': row['content'],
                        'source': row['source'],
                        'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                        'score': float(similarity)
                    })
                except Exception as e:
                    logger.error(f"Error processing document: {e}")
                    continue
            
            # Sort by similarity and return top results
            results.sort(key=lambda x: x['score'], reverse=True)
            conn.close()
            
            logger.info(f"Found {len(results[:top_k])} relevant documents for query: {query}")
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error searching varieties knowledge: {e}")
            return []
    
    def extract_variety_info(self, search_results: List[Dict[str, Any]], crop_name: str) -> Dict[str, Any]:
        """
        Extract variety-specific information from search results.
        
        Args:
            search_results: Results from knowledge base search
            crop_name: Name of the crop
            
        Returns:
            Extracted variety information
        """
        variety_info = {
            'variety_names': [],
            'planting_times': [],
            'yields': [],
            'seasons': [],
            'weather_requirements': [],
            'soil_requirements': [],
            'growing_areas': [],
            'general_info': [],
            'sources': []
        }
        
        for result in search_results:
            content = result['content'].lower()
            original_content = result['content']
            source = result['source']
            score = result['score']
            
            # Skip low-relevance results
            if score < 0.7:
                continue
            
            # Extract variety names
            if any(keyword in content for keyword in ['variety', 'varieties', 'cultivar', 'type']):
                variety_info['variety_names'].append({
                    'content': original_content,
                    'source': source,
                    'score': score
                })
            
            # Extract planting times/seasons
            if any(keyword in content for keyword in ['plant', 'sow', 'season', 'month', 'timing']):
                variety_info['planting_times'].append({
                    'content': original_content,
                    'source': source,
                    'score': score
                })
            
            # Extract yield information
            if any(keyword in content for keyword in ['yield', 'hectare', 'kg/ha', 'ton/ha', 'production']):
                variety_info['yields'].append({
                    'content': original_content,
                    'source': source,
                    'score': score
                })
            
            # Extract weather requirements
            if any(keyword in content for keyword in ['rain', 'weather', 'temperature', 'climate', 'water']):
                variety_info['weather_requirements'].append({
                    'content': original_content,
                    'source': source,
                    'score': score
                })
            
            # Extract soil requirements
            if any(keyword in content for keyword in ['soil', 'ph', 'fertile', 'drainage', 'nutrient']):
                variety_info['soil_requirements'].append({
                    'content': original_content,
                    'source': source,
                    'score': score
                })
            
            # Extract growing areas/districts
            if any(keyword in content for keyword in ['area', 'district', 'region', 'zone', 'grown']):
                variety_info['growing_areas'].append({
                    'content': original_content,
                    'source': source,
                    'score': score
                })
            
            # Keep general info for fallback
            variety_info['general_info'].append({
                'content': original_content,
                'source': source,
                'score': score
            })
            
            # Track sources
            if source not in variety_info['sources']:
                variety_info['sources'].append(source)
        
        return variety_info
    
    def _extract_clean_info(self, search_results: List[Dict[str, Any]], crop_name: str) -> Dict[str, List[str]]:
        """
        Extract clean, targeted information from search results.
        
        Args:
            search_results: Results from knowledge base search
            crop_name: Name of the crop
            
        Returns:
            Dictionary with clean extracted information
        """
        clean_info = {
            'variety_names': [],
            'planting_times': [],
            'yields': [],
            'weather': [],
            'soil': [],
            'areas': []
        }
        
        for result in search_results:
            if result['score'] < 0.75:  # Higher threshold for quality
                continue
                
            content = result['content']
            
            # Split into sentences and clean each one
            sentences = self._split_into_sentences(content)
            
            for sentence in sentences:
                if not self._is_valid_sentence(sentence):
                    continue
                    
                sentence_lower = sentence.lower()
                crop_lower = crop_name.lower()
                
                # Skip if sentence doesn't relate to the crop
                if crop_lower not in sentence_lower and not self._contains_variety_keywords(sentence_lower):
                    continue
                
                # Truncate long sentences to focus on key information
                processed_sentence = self._truncate_sentence(sentence)
                if not processed_sentence:
                    continue
                
                # Extract variety names - look for specific patterns
                if self._is_variety_info(sentence_lower):
                    clean_info['variety_names'].append(processed_sentence)
                
                # Extract planting times - look for temporal information
                elif self._is_planting_time_info(sentence_lower):
                    clean_info['planting_times'].append(processed_sentence)
                
                # Extract yields - look for quantitative production data
                elif self._is_yield_info(sentence_lower):
                    clean_info['yields'].append(processed_sentence)
                
                # Extract weather requirements - look for climate/rainfall data
                elif self._is_weather_info(sentence_lower):
                    clean_info['weather'].append(processed_sentence)
                
                # Extract soil requirements - look for soil-related specifications
                elif self._is_soil_info(sentence_lower):
                    clean_info['soil'].append(processed_sentence)
                
                # Extract growing areas - look for location/geographic data
                elif self._is_area_info(sentence_lower):
                    clean_info['areas'].append(processed_sentence)
        
        # Remove duplicates and limit results
        for key in clean_info:
            # Remove duplicates while preserving order
            seen = set()
            unique_items = []
            for item in clean_info[key]:
                if item not in seen:
                    seen.add(item)
                    unique_items.append(item)
            clean_info[key] = unique_items[:2]  # Limit to 2 items per category for conciseness
        
        return clean_info
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into clean sentences."""
        # Split by periods, but be careful with abbreviations
        sentences = []
        current_sentence = ""
        
        for char in text:
            current_sentence += char
            if char == '.':
                # Check if this is likely end of sentence
                if len(current_sentence) > 20:  # Minimum sentence length
                    sentences.append(current_sentence.strip())
                    current_sentence = ""
        
        # Add remaining text if any
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
        
        return sentences
    
    def _is_valid_sentence(self, sentence: str) -> bool:
        """Check if sentence is valid for extraction."""
        if not sentence or len(sentence) < 20 or len(sentence) > 150:  # Reduced max length
            return False
            
        # Skip sentences that are clearly not useful
        skip_patterns = [
            'table', 'figure', 'page', 'chapter', 'section', 'appendix',
            'according to', 'as shown', 'see also', 'refer to', 'source:',
            'phone', 'fax', 'email', 'website', 'contact', 'address',
            'copyright', '©', 'all rights reserved', 'isbn',
            'government of malawi', 'ministry of', 'department of',
            'lack of seed was', 'most common reason', 'surveyed households'
        ]
        
        sentence_lower = sentence.lower()
        if any(pattern in sentence_lower for pattern in skip_patterns):
            return False
        
        # Must contain actual content (not just numbers or punctuation)
        if not any(c.isalpha() for c in sentence):
            return False
            
        return True
    
    def _contains_variety_keywords(self, sentence_lower: str) -> bool:
        """Check if sentence contains variety-related keywords."""
        variety_keywords = [
            'variety', 'varieties', 'cultivar', 'cultivars', 'type', 'types',
            'strain', 'strains', 'breed', 'breeds', 'released', 'developed'
        ]
        return any(keyword in sentence_lower for keyword in variety_keywords)
    
    def _is_variety_info(self, sentence_lower: str) -> bool:
        """Check if sentence contains variety name information."""
        variety_indicators = [
            'variety', 'cultivar', 'released', 'developed', 'bred', 'strain'
        ]
        
        # Must contain variety indicator
        if not any(indicator in sentence_lower for indicator in variety_indicators):
            return False
        
        # Should contain actual variety names or characteristics
        variety_chars = [
            'high yield', 'drought tolerant', 'resistant', 'early maturing',
            'late maturing', 'improved', 'hybrid', 'open pollinated',
            'released', 'developed', 'bred', 'adapted'
        ]
        
        # Look for actual variety names (often contain numbers or specific terms)
        has_variety_name = any(char.isdigit() for char in sentence_lower) or \
                          any(term in sentence_lower for term in ['cg', 'k', 'var', 'line', 'selection'])
        
        return any(char in sentence_lower for char in variety_chars) or has_variety_name
    
    def _is_planting_time_info(self, sentence_lower: str) -> bool:
        """Check if sentence contains planting time information."""
        # Must contain time reference
        months = [
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december'
        ]
        
        seasons = ['rainy season', 'dry season', 'wet season', 'planting season']
        
        time_indicators = ['plant', 'sow', 'sowing', 'planting', 'season', 'timing']
        
        has_time = any(month in sentence_lower for month in months) or \
                  any(season in sentence_lower for season in seasons)
        
        has_action = any(indicator in sentence_lower for indicator in time_indicators)
        
        return has_time and has_action
    
    def _is_yield_info(self, sentence_lower: str) -> bool:
        """Check if sentence contains yield information."""
        yield_indicators = ['yield', 'production', 'harvest', 'output', 'produce']
        units = ['kg/ha', 'kg per hectare', 'tons/ha', 'tonnes/ha', 'mt/ha', 'kg per ha']
        
        has_yield = any(indicator in sentence_lower for indicator in yield_indicators)
        has_units = any(unit in sentence_lower for unit in units)
        has_numbers = any(char.isdigit() for char in sentence_lower)
        
        # Must have yield term AND numbers, prefer if it has units too
        return has_yield and has_numbers and (has_units or 'kg' in sentence_lower)
    
    def _is_weather_info(self, sentence_lower: str) -> bool:
        """Check if sentence contains weather requirement information."""
        weather_indicators = [
            'rainfall', 'rain', 'water', 'irrigation', 'drought',
            'temperature', 'climate', 'weather', 'moisture'
        ]
        
        requirements = [
            'require', 'need', 'prefer', 'tolerant', 'resistant',
            'suitable', 'optimal', 'minimum', 'maximum'
        ]
        
        has_weather = any(indicator in sentence_lower for indicator in weather_indicators)
        has_requirement = any(req in sentence_lower for req in requirements)
        has_measurement = any(unit in sentence_lower for unit in ['mm', 'ml', 'cm', 'inches'])
        
        return has_weather and (has_requirement or has_measurement)
    
    def _is_soil_info(self, sentence_lower: str) -> bool:
        """Check if sentence contains soil requirement information."""
        soil_indicators = [
            'soil', 'soils', 'ph', 'fertile', 'fertility', 'drainage',
            'nutrient', 'nutrients', 'organic matter', 'clay', 'sandy', 'loam'
        ]
        
        requirements = [
            'require', 'need', 'prefer', 'suitable', 'optimal',
            'well-drained', 'poorly-drained', 'acidic', 'alkaline'
        ]
        
        has_soil = any(indicator in sentence_lower for indicator in soil_indicators)
        has_requirement = any(req in sentence_lower for req in requirements)
        
        return has_soil and has_requirement
    
    def _is_area_info(self, sentence_lower: str) -> bool:
        """Check if sentence contains growing area information."""
        locations = [
            'lilongwe', 'blantyre', 'mzuzu', 'zomba', 'kasungu',
            'machinga', 'mangochi', 'salima', 'ntchisi', 'dowa'
        ]
        
        area_indicators = [
            'area', 'areas', 'district', 'districts', 'region', 'regions',
            'grown', 'cultivated', 'planted', 'produced', 'suitable'
        ]
        
        has_location = any(location in sentence_lower for location in locations)
        has_area = any(indicator in sentence_lower for indicator in area_indicators)
        
        return has_location or (has_area and ('grown' in sentence_lower or 'cultivated' in sentence_lower))

    def _clean_sentence(self, sentence: str) -> str:
        """Clean and format a sentence for display."""
        # Remove extra spaces and clean up
        cleaned = ' '.join(sentence.split())
        
        # Skip if too short or contains unwanted patterns
        if len(cleaned) < 15 or len(cleaned) > 120:
            return None
            
        # Skip administrative/reference sentences
        skip_patterns = ['table', 'figure', 'chapter', 'according to', 'see also', 'refer to']
        if any(pattern in cleaned.lower() for pattern in skip_patterns):
            return None
        
        return cleaned
    
    def format_varieties_response(self, variety_info: Dict[str, Any], crop_name: str) -> str:
        """
        Format variety information into a structured, summarized response.
        
        Args:
            variety_info: Extracted variety information (contains search results and AI parsed info)
            crop_name: Name of the crop
            
        Returns:
            Formatted response message
        """
        crop_display = crop_name.title()
        
        # Use AI parsed info if available (Phase 3), otherwise parse again
        if 'ai_parsed_info' in variety_info:
            clean_info = variety_info['ai_parsed_info']
        else:
            # Fallback to original parsing
            search_results = variety_info.get('general_info', [])
            clean_info = self.parse_varieties_with_ai(search_results, crop_name)
        
        message = f"🌱 **{crop_display} Varieties Summary**\n\n"
        
        varieties = clean_info.get('varieties', [])
        weather_matched = clean_info.get('weather_matched', False)
        
        if varieties:
            # Add weather matching header if applicable
            if weather_matched:
                message += "🌦️ **Weather-Optimized Ranking** (Best suited varieties first)\n\n"
            
            for i, variety in enumerate(varieties, 1):
                # Variety header with weather score if available
                variety_name = variety.get('name', f'Variety {i}')
                
                # Phase 3: Add weather suitability indicator
                if weather_matched and 'weather_suitability' in variety:
                    suitability = variety['weather_suitability']
                    emoji = suitability.get('emoji', '')
                    percentage = suitability.get('percentage', '')
                    message += f"**{emoji} {variety_name}** ({percentage} weather suitable)\n\n"
                else:
                    message += f"**🌾 {variety_name}**\n\n"
                
                # Weather suitability details (Phase 3)
                if weather_matched and 'weather_suitability' in variety:
                    suitability = variety['weather_suitability']
                    message += f"🌦️ **Weather Suitability:** {suitability.get('description', 'Not assessed')}\n"
                
                # Planting time
                if 'planting_time' in variety:
                    message += f"📅 **Planting Time:** {variety['planting_time']}\n"
                
                # Expected yield
                if 'yield' in variety:
                    message += f"📈 **Expected Yield:** {variety['yield']}\n"
                
                # Weather requirements
                if 'weather' in variety:
                    message += f"🌦️ **Weather:** {variety['weather']}\n"
                
                # Soil requirements
                if 'soil' in variety:
                    message += f"🌍 **Soil:** {variety['soil']}\n"
                
                # Growing areas
                if 'areas' in variety:
                    message += f"📍 **Growing Areas:** {variety['areas']}\n"
                
                message += "\n"
        
        else:
            # Add fallback message if no varieties were extracted
            message += "ℹ️ **Information Status:**\n"
            message += "• Limited specific variety information found in knowledge base\n"
            message += "• Try general crop recommendations or check alternative spellings\n\n"
        
        # Add weather matching explanation if applied
        if weather_matched:
            message += "🌡️ **Weather Analysis:**\n"
            message += "• Varieties ranked by historical weather compatibility\n"
            message += "• Scores consider rainfall patterns, drought tolerance, and climate trends\n"
            message += "• Higher scores indicate better suitability for local conditions\n\n"
        
        # Phase 5: Add planting calendar information if available
        if 'planting_calendar' in variety_info and variety_info['planting_calendar']:
            message += self._format_planting_calendar_section(variety_info['planting_calendar'])
        
        # Add sources if available
        if variety_info.get('sources'):
            message += "📚 **Sources:**\n"
            for source in variety_info['sources'][:2]:
                message += f"• {source}\n"
            message += "\n"
        
        # Add related commands
        message += "🔧 **Related Commands:**\n"
        message += f"• `/crops [location]` - Get crop recommendations\n"
        message += f"• `/weather [location]` - Check weather conditions\n"
        message += f"• `/rain [location]` - Analyze rainfall patterns\n"
        
        return message
    
    def _format_planting_calendar_section(self, planting_calendar: Dict[str, Any]) -> str:
        """
        Format planting calendar information into a readable section.
        
        Args:
            planting_calendar: Planting calendar data
            
        Returns:
            Formatted planting calendar section
        """
        try:
            section = "📅 **Planting Calendar** (Based on historical weather patterns)\n\n"
            
            # Optimal planting information
            best_month = planting_calendar.get('best_planting_month', 'Unknown')
            alternative_months = planting_calendar.get('alternative_months', [])
            avoid_months = planting_calendar.get('avoid_months', [])
            
            section += f"🌟 **Best Planting Month:** {best_month}\n"
            
            if alternative_months:
                section += f"✅ **Alternative Months:** {', '.join(alternative_months)}\n"
            
            if avoid_months:
                section += f"⚠️ **Avoid Months:** {', '.join(avoid_months)}\n"
            
            section += "\n"
            
            # Monthly recommendations (show next 3 months)
            monthly_recommendations = planting_calendar.get('monthly_recommendations', {})
            if monthly_recommendations:
                section += "📊 **Monthly Recommendations:**\n"
                
                # Get current month and next 2 months
                current_month = datetime.now().strftime('%B')
                current_month_num = datetime.now().month
                
                months_to_show = []
                for i in range(3):
                    month_num = ((current_month_num + i - 1) % 12) + 1
                    month_name = calendar.month_name[month_num]
                    months_to_show.append(month_name)
                
                for month in months_to_show:
                    if month in monthly_recommendations:
                        rec = monthly_recommendations[month]
                        rec_type = rec.get('recommendation_type', 'unknown')
                        advice = rec.get('advice', 'No advice available')
                        
                        # Format based on recommendation type
                        if rec_type == 'optimal':
                            section += f"🌟 **{month}:** {advice}\n"
                        elif rec_type == 'alternative':
                            section += f"✅ **{month}:** {advice}\n"
                        elif rec_type == 'avoid':
                            section += f"⚠️ **{month}:** {advice}\n"
                        elif rec_type == 'possible':
                            section += f"⚖️ **{month}:** {advice}\n"
                        else:
                            section += f"❌ **{month}:** {advice}\n"
                
                section += "\n"
            
            # Risk assessment
            risk_assessment = planting_calendar.get('risk_assessment', {})
            if risk_assessment:
                section += "⚠️ **Risk Assessment:**\n"
                
                overall_risk = risk_assessment.get('overall_risk_level', 'unknown')
                section += f"• Overall Risk Level: {overall_risk.title()}\n"
                
                # Drought risk
                drought_risk = risk_assessment.get('drought_risk', {})
                if drought_risk.get('level') != 'unknown':
                    drought_prob = drought_risk.get('probability', 0)
                    section += f"• Drought Risk: {drought_risk.get('level', 'unknown').title()} ({drought_prob}%)\n"
                
                # Flood risk
                flood_risk = risk_assessment.get('flood_risk', {})
                if flood_risk.get('level') != 'unknown':
                    flood_prob = flood_risk.get('probability', 0)
                    section += f"• Flood Risk: {flood_risk.get('level', 'unknown').title()} ({flood_prob}%)\n"
                
                # Mitigation strategies
                mitigation_strategies = risk_assessment.get('mitigation_strategies', [])
                if mitigation_strategies:
                    section += "\n🛡️ **Risk Mitigation Strategies:**\n"
                    for strategy in mitigation_strategies[:3]:  # Show top 3
                        section += f"• {strategy}\n"
                
                section += "\n"
            
            return section
            
        except Exception as e:
            logger.error(f"Error formatting planting calendar section: {e}")
            return "📅 **Planting Calendar:** Unable to format calendar information\n\n"
    
    def _extract_specific_info(self, info_list: List[Dict[str, Any]], keywords: List[str]) -> List[str]:
        """
        Extract specific information from content based on keywords.
        
        Args:
            info_list: List of information items
            keywords: Keywords to look for
            
        Returns:
            List of extracted information snippets
        """
        extracted = []
        
        for item in info_list:
            content = item['content']
            content_lower = content.lower()
            
            # Split content into sentences
            sentences = [s.strip() for s in content.split('.') if s.strip()]
            
            for sentence in sentences:
                sentence_lower = sentence.lower()
                
                # Check if sentence contains relevant keywords
                if any(keyword in sentence_lower for keyword in keywords):
                    # Clean up the sentence
                    cleaned_sentence = sentence.strip()
                    
                    # Only keep reasonable length sentences
                    if 15 <= len(cleaned_sentence) <= 120:
                        # Additional filtering for specific types
                        if self._is_relevant_sentence(cleaned_sentence, keywords):
                            extracted.append(cleaned_sentence)
                            if len(extracted) >= 5:  # Limit to prevent overloading
                                break
            
            if len(extracted) >= 5:
                break
        
        # Remove duplicates and return unique items
        return list(set(extracted))[:3]
    
    def _is_relevant_sentence(self, sentence: str, keywords: List[str]) -> bool:
        """
        Check if a sentence contains relevant information.
        
        Args:
            sentence: The sentence to check
            keywords: Keywords to look for
            
        Returns:
            True if sentence is relevant, False otherwise
        """
        sentence_lower = sentence.lower()
        
        # Skip sentences that are too generic or administrative
        skip_phrases = [
            'table', 'figure', 'chapter', 'section', 'page', 'appendix',
            'according to', 'as shown in', 'see also', 'refer to'
        ]
        
        if any(phrase in sentence_lower for phrase in skip_phrases):
            return False
        
        # For variety names, look for specific patterns
        if 'variety' in keywords or 'cultivar' in keywords:
            variety_indicators = ['variety', 'cultivar', 'type', 'released', 'developed']
            return any(indicator in sentence_lower for indicator in variety_indicators)
        
        # For planting times, look for temporal information
        if any(month in keywords for month in ['november', 'december', 'january']):
            time_indicators = ['plant', 'sow', 'season', 'month', 'time']
            return any(indicator in sentence_lower for indicator in time_indicators)
        
        # For yields, look for quantitative information
        if 'yield' in keywords or 'kg/ha' in keywords:
            yield_indicators = ['yield', 'production', 'kg', 'ton', 'hectare', 'harvest']
            return any(indicator in sentence_lower for indicator in yield_indicators)
        
        # For weather, look for climate information
        if 'rain' in keywords or 'weather' in keywords:
            weather_indicators = ['rain', 'water', 'climate', 'temperature', 'mm']
            return any(indicator in sentence_lower for indicator in weather_indicators)
        
        # For soil, look for soil-related information
        if 'soil' in keywords:
            soil_indicators = ['soil', 'ph', 'fertile', 'drainage', 'nutrient']
            return any(indicator in sentence_lower for indicator in soil_indicators)
        
        # For areas, look for location information
        if 'area' in keywords or 'district' in keywords:
            area_indicators = ['area', 'district', 'region', 'grown', 'cultivated']
            return any(indicator in sentence_lower for indicator in area_indicators)
        
        return True

    def _truncate_sentence(self, sentence: str) -> str:
        """Truncate sentence to focus on key information."""
        # Clean up the sentence
        sentence = sentence.strip()
        
        # If sentence is reasonably short, return as is
        if len(sentence) <= 80:
            return sentence
            
        # Try to find a good breaking point
        words = sentence.split()
        
        # Look for natural break points
        break_points = [',', ';', 'and', 'but', 'which', 'that', 'with']
        
        for i, word in enumerate(words):
            if i > 10:  # Don't break too early
                if any(bp in word.lower() for bp in break_points):
                    truncated = ' '.join(words[:i])
                    if len(truncated) >= 40:  # Ensure meaningful length
                        return truncated + '.'
        
        # If no good break point, just truncate at reasonable length
        if len(words) > 15:
            return ' '.join(words[:15]) + '.'
        
        return sentence

    def parse_varieties_with_ai(self, search_results: List[Dict[str, Any]], crop_name: str) -> Dict[str, List[Dict]]:
        """
        Use OpenAI to parse search results and extract structured variety information.
        
        Args:
            search_results: Results from knowledge base search
            crop_name: Name of the crop
            
        Returns:
            Dictionary with parsed variety information
        """
        if not self.openai_client:
            logger.warning("OpenAI client not initialized, skipping AI parsing.")
            return self._get_empty_varieties_info()

        try:
            # Combine top search results into context (reduced size)
            context_text = ""
            for i, result in enumerate(search_results[:5]):  # Reduced from 8 to 5
                if result['score'] > 0.75:  # Higher threshold for faster processing
                    # Truncate very long content
                    content = result['content']
                    if len(content) > 800:  # Limit content length
                        content = content[:800] + "..."
                    context_text += f"Source {i+1}: {content}\n\n"
            
            if not context_text:
                return self._get_empty_varieties_info()
            
            # Create more concise prompt for OpenAI
            prompt = f"""
You are an agricultural expert. Extract information about SPECIFIC {crop_name} CULTIVAR NAMES from these documents:

{context_text}

CRITICAL: Look for EXACT cultivar names, variety codes, and released variety names. NOT general types.

SPECIFIC NAMES TO LOOK FOR:
- Cultivar codes: "CG7", "CG9", "CG11", "SC 301", "SC 627", "SC 719"
- Named varieties: "Nsinjiro", "Makwacha", "Nasoko", "Baka SB", "Kholophethe"
- Released varieties: "Chalimbana", "Chitembana", "Maluwa"

AVOID generic descriptions like:
- "Virginia type", "Spanish type", "Hybrid", "Open pollinated"
- "Early maturing variety", "High yielding variety"
- "Improved variety", "Local variety"

For EACH SPECIFIC CULTIVAR NAME you find, extract:
- name: The exact cultivar name/code (e.g., "CG7", "Nsinjiro")
- planting_time: When to plant this specific cultivar
- yield: Expected yield for this specific cultivar
- weather: Weather/climate needs for this specific cultivar
- soil: Soil requirements for this specific cultivar
- areas: Where this specific cultivar is grown

Return JSON like this:
{{
  "varieties": [
    {{
      "name": "CG7",
      "planting_time": "timing info",
      "yield": "yield info",
      "weather": "weather info",
      "soil": "soil info",
      "areas": "location info"
    }},
    {{
      "name": "CG9",
      "planting_time": "timing info",
      "yield": "yield info",
      "weather": "weather info",
      "soil": "soil info",
      "areas": "location info"
    }},
    {{
      "name": "Nsinjiro",
      "planting_time": "timing info",
      "yield": "yield info",
      "weather": "weather info",
      "soil": "soil info",
      "areas": "location info"
    }}
  ]
}}

CRITICAL REQUIREMENTS:
- Only include varieties with SPECIFIC names (not generic types)
- Look for variety names mentioned in tables, lists, or descriptions
- Include variety codes (letters + numbers like CG7, SC301)
- Include proper variety names (like Nsinjiro, Makwacha)
- Each variety must have a unique, specific name
- Use "Not specified" if information is missing for a field
- Focus on released/recommended varieties
"""

            # Call OpenAI with timeout
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an agricultural expert who extracts specific variety information from agricultural documents."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=800,  # Reduced from 1000
                    temperature=0.1,
                    timeout=15.0  # 15 second timeout
                )
                
                # Parse response
                response_text = response.choices[0].message.content.strip()
                
            except Exception as openai_error:
                logger.error(f"OpenAI API error: {openai_error}")
                return self._get_empty_varieties_info()
            
            # Try to extract JSON from response
            try:
                # Find JSON in response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start != -1 and json_end != -1:
                    json_text = response_text[json_start:json_end]
                    parsed_info = json.loads(json_text)
                    
                    # Validate and clean the parsed info
                    if 'varieties' in parsed_info and isinstance(parsed_info['varieties'], list):
                        clean_varieties = []
                        
                        for variety in parsed_info['varieties'][:5]:  # Max 5 varieties
                            if isinstance(variety, dict) and 'name' in variety:
                                clean_variety = {}
                                variety_name = variety['name'].strip()
                                
                                # Skip if name is too generic or empty
                                generic_terms = [
                                    'variety', 'type', 'cultivar', 'not specified', 'hybrid', 'open pollinated',
                                    'virginia type', 'spanish type', 'early maturing', 'late maturing',
                                    'high yielding', 'drought tolerant', 'improved variety', 'local variety',
                                    'released variety', 'recommended variety', 'modern variety', 'traditional variety'
                                ]
                                
                                if (len(variety_name) < 2 or 
                                    variety_name.lower() in generic_terms or
                                    any(term in variety_name.lower() for term in ['type', 'variety', 'cultivar']) and 
                                    not any(char.isdigit() for char in variety_name)):
                                    continue
                                
                                # Prefer names with codes (letters + numbers) or specific proper names
                                has_code = any(char.isdigit() for char in variety_name) and any(char.isalpha() for char in variety_name)
                                is_proper_name = variety_name[0].isupper() and len(variety_name) > 3
                                
                                if not (has_code or is_proper_name):
                                    continue
                                
                                # Add the variety name
                                clean_variety['name'] = variety_name
                                
                                # Clean each field (more lenient validation)
                                for field in ['planting_time', 'yield', 'weather', 'soil', 'areas']:
                                    if field in variety and isinstance(variety[field], str):
                                        cleaned_value = variety[field].strip()
                                        if len(cleaned_value) > 3 and cleaned_value.lower() not in ['not specified', 'n/a', 'none']:
                                            clean_variety[field] = cleaned_value[:80]  # Limit length
                                
                                # Include variety if it has name (more lenient - don't require other fields)
                                if 'name' in clean_variety:
                                    clean_varieties.append(clean_variety)
                        
                        if clean_varieties:
                            logger.info(f"AI parsed {len(clean_varieties)} varieties for {crop_name}")
                            return {'varieties': clean_varieties}
                    
                    # If no varieties found, try to extract from a different JSON structure
                    logger.warning(f"No varieties found in expected format for {crop_name}")
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                logger.debug(f"AI response was: {response_text}")
                
        except Exception as e:
            logger.error(f"Error in AI parsing: {e}")
            
        # Fallback to empty info if AI parsing fails
        return self._get_empty_varieties_info()
    
    def _get_empty_varieties_info(self) -> Dict[str, List[Dict]]:
        """Return empty varieties info structure."""
        return {'varieties': []}

    def get_location_weather_analysis(self, 
                                    lat: float, 
                                    lon: float, 
                                    years: int = 5,
                                    user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive weather analysis for a location.
        
        Args:
            lat: Latitude
            lon: Longitude
            years: Number of years of historical data (default: 5)
            user_id: Optional user ID for logging
            
        Returns:
            Weather analysis data or None if failed
        """
        try:
            # Generate cache key
            cache_key = f"weather_{lat}_{lon}_{years}"
            current_time = time.time()
            
            # Check cache first
            if cache_key in self.weather_cache:
                cached_data, timestamp = self.weather_cache[cache_key]
                if current_time - timestamp < self.cache_timeout:
                    logger.info(f"Using cached weather data for {lat}, {lon}", user_id)
                    return cached_data
            
            logger.info(f"Fetching weather analysis for {lat}, {lon} ({years} years)", user_id)
            
            # Get historical rainfall data
            historical_data = self.historical_weather_api.get_historical_rainfall(
                lat, lon, years, user_id
            )
            
            if not historical_data:
                logger.warning(f"No historical weather data available for {lat}, {lon}", user_id)
                return None
            
            # Analyze current conditions (using dummy data for now - can be enhanced with real current weather)
            current_month = datetime.now().strftime('%B')
            current_rainfall = 0  # Placeholder - would come from current weather API
            
            # Perform comprehensive analysis
            comprehensive_analysis = self.enhanced_rainfall_analyzer.analyze_comprehensive_rainfall(
                lat, lon, current_rainfall, 0, years, user_id
            )
            
            # Combine historical and comprehensive analysis
            weather_analysis = {
                'location': {'lat': lat, 'lon': lon},
                'historical_data': {
                    'years_analyzed': historical_data.years_analyzed,
                    'monthly_averages': historical_data.monthly_averages,
                    'annual_averages': historical_data.annual_averages,
                    'wet_season_months': historical_data.wet_season_months,
                    'dry_season_months': historical_data.dry_season_months,
                    'drought_years': historical_data.drought_years,
                    'flood_years': historical_data.flood_years,
                    'rainfall_variability': historical_data.rainfall_variability,
                    'climate_trend': historical_data.climate_trend
                },
                'comprehensive_analysis': comprehensive_analysis,
                'current_month': current_month,
                'analysis_timestamp': datetime.now().isoformat(),
                'cache_key': cache_key
            }
            
            # Cache the results
            self.weather_cache[cache_key] = (weather_analysis, current_time)
            
            logger.info(f"Weather analysis completed for {lat}, {lon}", user_id)
            return weather_analysis
            
        except Exception as e:
            logger.error(f"Error in weather analysis: {e}", user_id)
            return None
    
    def _format_weather_context(self, weather_analysis: Dict[str, Any]) -> str:
        """
        Format weather analysis into a readable context string.
        
        Args:
            weather_analysis: Weather analysis data
            
        Returns:
            Formatted weather context string
        """
        if not weather_analysis:
            return ""
        
        historical_data = weather_analysis.get('historical_data', {})
        current_month = weather_analysis.get('current_month', 'Unknown')
        
        context = f"\n🌦️ **Weather Context ({historical_data.get('years_analyzed', 0)} years)**\n"
        
        # Monthly average for current month
        monthly_avg = historical_data.get('monthly_averages', {}).get(current_month, 0)
        if monthly_avg > 0:
            context += f"• {current_month} average: {monthly_avg:.0f}mm\n"
        
        # Climate trend
        climate_trend = historical_data.get('climate_trend', 'stable')
        if climate_trend != 'stable':
            trend_desc = climate_trend.replace('_', ' ').title()
            context += f"• Climate trend: {trend_desc}\n"
        
        # Rainfall variability
        variability = historical_data.get('rainfall_variability', 0)
        if variability > 30:
            context += f"• Rainfall variability: {variability:.0f}% (High)\n"
        elif variability > 0:
            context += f"• Rainfall variability: {variability:.0f}% (Moderate)\n"
        
        # Seasonal info
        wet_months = historical_data.get('wet_season_months', [])
        dry_months = historical_data.get('dry_season_months', [])
        
        if wet_months:
            context += f"• Wet season: {', '.join(wet_months[:3])}...\n"
        if dry_months:
            context += f"• Dry season: {', '.join(dry_months[:3])}...\n"
        
        # Recent extreme years
        drought_years = historical_data.get('drought_years', [])
        flood_years = historical_data.get('flood_years', [])
        
        if drought_years:
            recent_droughts = drought_years[-3:] if len(drought_years) > 3 else drought_years
            context += f"• Recent drought years: {', '.join(map(str, recent_droughts))}\n"
        
        if flood_years:
            recent_floods = flood_years[-3:] if len(flood_years) > 3 else flood_years
            context += f"• Recent flood years: {', '.join(map(str, recent_floods))}\n"
        
        return context
    
    def _clear_old_cache_entries(self):
        """Clear old cache entries to prevent memory buildup."""
        current_time = time.time()
        keys_to_remove = []
        
        for key, (_, timestamp) in self.weather_cache.items():
            if current_time - timestamp > self.cache_timeout:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.weather_cache[key]
        
        if keys_to_remove:
            logger.info(f"Cleared {len(keys_to_remove)} old cache entries")

    # Phase 3: Weather-Variety Matching Algorithm
    def match_varieties_to_weather(self, 
                                 varieties: List[Dict[str, Any]], 
                                 weather_analysis: Dict[str, Any],
                                 crop_name: str,
                                 user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Match varieties to weather patterns and score them based on suitability.
        
        Args:
            varieties: List of variety information dictionaries
            weather_analysis: Historical weather analysis data
            crop_name: Name of the crop
            user_id: Optional user ID for logging
            
        Returns:
            List of varieties with weather suitability scores
        """
        if not weather_analysis or not varieties:
            logger.warning("No weather analysis or varieties data for matching", user_id)
            return varieties
        
        try:
            logger.info(f"Starting weather-variety matching for {len(varieties)} {crop_name} varieties", user_id)
            
            # Analyze weather patterns
            weather_patterns = self._analyze_weather_patterns(weather_analysis)
            
            # Score each variety based on weather compatibility
            scored_varieties = []
            for variety in varieties:
                weather_score = self._calculate_weather_suitability_score(
                    variety, weather_patterns, crop_name, user_id
                )
                
                # Add weather scoring to variety
                variety_with_score = variety.copy()
                variety_with_score['weather_score'] = weather_score
                variety_with_score['weather_suitability'] = self._interpret_weather_score(weather_score)
                
                scored_varieties.append(variety_with_score)
            
            # Sort by weather score (highest first)
            scored_varieties.sort(key=lambda x: x['weather_score']['total_score'], reverse=True)
            
            logger.info(f"Weather-variety matching completed for {crop_name}", user_id)
            return scored_varieties
            
        except Exception as e:
            logger.error(f"Error in weather-variety matching: {e}", user_id)
            return varieties
    
    def _analyze_weather_patterns(self, weather_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze weather patterns to extract key characteristics for variety matching.
        
        Args:
            weather_analysis: Historical weather analysis data
            
        Returns:
            Dictionary with analyzed weather patterns
        """
        try:
            historical_data = weather_analysis.get('historical_data', {})
            current_month = weather_analysis.get('current_month', 'Unknown')
            
            # Extract key weather characteristics
            patterns = {
                'current_month': current_month,
                'rainfall_variability': historical_data.get('rainfall_variability', 0),
                'climate_trend': historical_data.get('climate_trend', 'stable'),
                'wet_season_months': historical_data.get('wet_season_months', []),
                'dry_season_months': historical_data.get('dry_season_months', []),
                'monthly_averages': historical_data.get('monthly_averages', {}),
                'drought_risk': len(historical_data.get('drought_years', [])) / max(historical_data.get('years_analyzed', 1), 1),
                'flood_risk': len(historical_data.get('flood_years', [])) / max(historical_data.get('years_analyzed', 1), 1),
                'seasonal_distribution': self._analyze_seasonal_distribution(historical_data.get('monthly_averages', {})),
                'planting_season_suitability': self._analyze_planting_season_suitability(historical_data, current_month)
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing weather patterns: {e}")
            return {}
    
    def _analyze_seasonal_distribution(self, monthly_averages: Dict[str, float]) -> Dict[str, Any]:
        """
        Analyze seasonal rainfall distribution patterns.
        
        Args:
            monthly_averages: Monthly rainfall averages
            
        Returns:
            Dictionary with seasonal distribution analysis
        """
        try:
            # Define seasons for Malawi
            wet_season_months = ['November', 'December', 'January', 'February', 'March', 'April']
            dry_season_months = ['May', 'June', 'July', 'August', 'September', 'October']
            
            # Calculate seasonal totals
            wet_season_total = sum(monthly_averages.get(month, 0) for month in wet_season_months)
            dry_season_total = sum(monthly_averages.get(month, 0) for month in dry_season_months)
            annual_total = wet_season_total + dry_season_total
            
            # Calculate distribution characteristics
            distribution = {
                'wet_season_total': wet_season_total,
                'dry_season_total': dry_season_total,
                'annual_total': annual_total,
                'wet_season_percentage': (wet_season_total / annual_total * 100) if annual_total > 0 else 0,
                'dry_season_percentage': (dry_season_total / annual_total * 100) if annual_total > 0 else 0,
                'seasonal_contrast': wet_season_total / max(dry_season_total, 1),  # Ratio of wet to dry
                'peak_month': max(monthly_averages, key=monthly_averages.get) if monthly_averages else 'Unknown',
                'peak_rainfall': max(monthly_averages.values()) if monthly_averages else 0,
                'min_month': min(monthly_averages, key=monthly_averages.get) if monthly_averages else 'Unknown',
                'min_rainfall': min(monthly_averages.values()) if monthly_averages else 0
            }
            
            return distribution
            
        except Exception as e:
            logger.error(f"Error analyzing seasonal distribution: {e}")
            return {}
    
    def _analyze_planting_season_suitability(self, historical_data: Dict[str, Any], current_month: str) -> Dict[str, Any]:
        """
        Analyze planting season suitability based on historical patterns.
        
        Args:
            historical_data: Historical weather data
            current_month: Current month name
            
        Returns:
            Dictionary with planting season suitability analysis
        """
        try:
            monthly_averages = historical_data.get('monthly_averages', {})
            
            # Define typical planting months for Malawi
            planting_months = ['October', 'November', 'December', 'January']
            
            # Calculate planting season characteristics
            planting_season_rainfall = sum(monthly_averages.get(month, 0) for month in planting_months)
            planting_season_average = planting_season_rainfall / len(planting_months)
            
            # Analyze reliability
            rainfall_variability = historical_data.get('rainfall_variability', 0)
            drought_years = historical_data.get('drought_years', [])
            
            suitability = {
                'planting_season_rainfall': planting_season_rainfall,
                'planting_season_average': planting_season_average,
                'current_month_suitable': current_month in planting_months,
                'rainfall_reliability': 'high' if rainfall_variability < 25 else 'moderate' if rainfall_variability < 40 else 'low',
                'drought_risk_level': 'high' if len(drought_years) > 2 else 'moderate' if len(drought_years) > 0 else 'low',
                'optimal_planting_month': max(
                    [(month, monthly_averages.get(month, 0)) for month in planting_months],
                    key=lambda x: x[1]
                )[0] if monthly_averages else 'Unknown'
            }
            
            return suitability
            
        except Exception as e:
            logger.error(f"Error analyzing planting season suitability: {e}")
            return {}
    
    def _calculate_weather_suitability_score(self, 
                                           variety: Dict[str, Any], 
                                           weather_patterns: Dict[str, Any],
                                           crop_name: str,
                                           user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate weather suitability score for a variety.
        
        Args:
            variety: Variety information dictionary
            weather_patterns: Analyzed weather patterns
            crop_name: Name of the crop
            user_id: Optional user ID for logging
            
        Returns:
            Dictionary with detailed weather suitability scores
        """
        try:
            # Initialize scoring components
            scores = {
                'rainfall_compatibility': 0,
                'seasonal_timing': 0,
                'drought_tolerance': 0,
                'climate_trend_alignment': 0,
                'variability_resilience': 0
            }
            
            # Score rainfall compatibility
            scores['rainfall_compatibility'] = self._score_rainfall_compatibility(
                variety, weather_patterns, crop_name
            )
            
            # Score seasonal timing
            scores['seasonal_timing'] = self._score_seasonal_timing(
                variety, weather_patterns, crop_name
            )
            
            # Score drought tolerance
            scores['drought_tolerance'] = self._score_drought_tolerance(
                variety, weather_patterns, crop_name
            )
            
            # Score climate trend alignment
            scores['climate_trend_alignment'] = self._score_climate_trend_alignment(
                variety, weather_patterns, crop_name
            )
            
            # Score variability resilience
            scores['variability_resilience'] = self._score_variability_resilience(
                variety, weather_patterns, crop_name
            )
            
            # Calculate total score (weighted average)
            weights = {
                'rainfall_compatibility': 0.3,
                'seasonal_timing': 0.25,
                'drought_tolerance': 0.2,
                'climate_trend_alignment': 0.15,
                'variability_resilience': 0.1
            }
            
            total_score = sum(scores[component] * weights[component] for component in scores)
            
            return {
                'total_score': round(total_score, 2),
                'component_scores': scores,
                'weights': weights,
                'max_possible_score': 100
            }
            
        except Exception as e:
            logger.error(f"Error calculating weather suitability score: {e}", user_id)
            return {
                'total_score': 50,  # Default neutral score
                'component_scores': {k: 50 for k in ['rainfall_compatibility', 'seasonal_timing', 'drought_tolerance', 'climate_trend_alignment', 'variability_resilience']},
                'weights': {'rainfall_compatibility': 0.3, 'seasonal_timing': 0.25, 'drought_tolerance': 0.2, 'climate_trend_alignment': 0.15, 'variability_resilience': 0.1},
                'max_possible_score': 100
            }
    
    def _score_rainfall_compatibility(self, variety: Dict[str, Any], weather_patterns: Dict[str, Any], crop_name: str) -> float:
        """Score how well variety rainfall requirements match local patterns."""
        try:
            variety_weather = variety.get('weather', '').lower()
            seasonal_dist = weather_patterns.get('seasonal_distribution', {})
            
            # Base score
            score = 50
            
            # Analyze variety rainfall requirements
            if 'drought tolerant' in variety_weather or 'drought resistant' in variety_weather:
                # Benefit from low rainfall/high drought risk
                drought_risk = weather_patterns.get('drought_risk', 0)
                if drought_risk > 0.3:  # High drought risk
                    score += 25
                elif drought_risk > 0.1:  # Moderate drought risk
                    score += 15
            
            if 'water' in variety_weather and 'require' in variety_weather:
                # High water requirement varieties
                wet_season_percentage = seasonal_dist.get('wet_season_percentage', 0)
                if wet_season_percentage > 80:  # High wet season rainfall
                    score += 20
                elif wet_season_percentage > 60:  # Moderate wet season rainfall
                    score += 10
                else:  # Low wet season rainfall
                    score -= 15
            
            if 'rain' in variety_weather:
                # General rain-dependent varieties
                annual_total = seasonal_dist.get('annual_total', 0)
                if annual_total > 800:  # High annual rainfall
                    score += 15
                elif annual_total > 600:  # Moderate annual rainfall
                    score += 10
                elif annual_total < 400:  # Low annual rainfall
                    score -= 10
            
            return max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Error scoring rainfall compatibility: {e}")
            return 50
    
    def _score_seasonal_timing(self, variety: Dict[str, Any], weather_patterns: Dict[str, Any], crop_name: str) -> float:
        """Score how well variety planting times match weather patterns."""
        try:
            variety_planting_time = variety.get('planting_time', '').lower()
            planting_suitability = weather_patterns.get('planting_season_suitability', {})
            current_month = weather_patterns.get('current_month', 'Unknown')
            
            # Base score
            score = 50
            
            # Check if planting time mentions optimal months
            optimal_months = ['november', 'december', 'january', 'october']
            variety_mentions_optimal = any(month in variety_planting_time for month in optimal_months)
            
            if variety_mentions_optimal:
                score += 20
            
            # Check current month suitability
            if planting_suitability.get('current_month_suitable', False):
                score += 15
            
            # Check rainfall reliability
            reliability = planting_suitability.get('rainfall_reliability', 'moderate')
            if reliability == 'high':
                score += 10
            elif reliability == 'low':
                score -= 10
            
            # Season-specific adjustments
            if 'rainy season' in variety_planting_time:
                wet_season_months = weather_patterns.get('wet_season_months', [])
                if current_month in wet_season_months:
                    score += 15
            
            if 'dry season' in variety_planting_time:
                dry_season_months = weather_patterns.get('dry_season_months', [])
                if current_month in dry_season_months:
                    score += 15
            
            return max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Error scoring seasonal timing: {e}")
            return 50
    
    def _score_drought_tolerance(self, variety: Dict[str, Any], weather_patterns: Dict[str, Any], crop_name: str) -> float:
        """Score variety drought tolerance against local drought risk."""
        try:
            variety_weather = variety.get('weather', '').lower()
            drought_risk = weather_patterns.get('drought_risk', 0)
            rainfall_variability = weather_patterns.get('rainfall_variability', 0)
            
            # Base score
            score = 50
            
            # Drought tolerance indicators
            drought_terms = ['drought tolerant', 'drought resistant', 'water stress', 'dry conditions']
            is_drought_tolerant = any(term in variety_weather for term in drought_terms)
            
            if is_drought_tolerant:
                # Drought-tolerant varieties score higher in drought-prone areas
                if drought_risk > 0.3:  # High drought risk
                    score += 30
                elif drought_risk > 0.1:  # Moderate drought risk
                    score += 20
                else:  # Low drought risk
                    score += 10
            else:
                # Non-drought-tolerant varieties score lower in drought-prone areas
                if drought_risk > 0.3:  # High drought risk
                    score -= 20
                elif drought_risk > 0.1:  # Moderate drought risk
                    score -= 10
            
            # Rainfall variability adjustment
            if rainfall_variability > 40:  # High variability
                if is_drought_tolerant:
                    score += 15
                else:
                    score -= 15
            
            return max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Error scoring drought tolerance: {e}")
            return 50
    
    def _score_climate_trend_alignment(self, variety: Dict[str, Any], weather_patterns: Dict[str, Any], crop_name: str) -> float:
        """Score how well variety aligns with climate trends."""
        try:
            variety_weather = variety.get('weather', '').lower()
            climate_trend = weather_patterns.get('climate_trend', 'stable')
            
            # Base score
            score = 50
            
            if climate_trend == 'decreasing':
                # Decreasing rainfall trend
                if 'drought tolerant' in variety_weather or 'drought resistant' in variety_weather:
                    score += 20
                elif 'water' in variety_weather and 'require' in variety_weather:
                    score -= 15
            elif climate_trend == 'increasing':
                # Increasing rainfall trend
                if 'water' in variety_weather and 'require' in variety_weather:
                    score += 15
                elif 'flood' in variety_weather and 'tolerant' in variety_weather:
                    score += 10
            
            # Stable climate gets neutral score
            return max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Error scoring climate trend alignment: {e}")
            return 50
    
    def _score_variability_resilience(self, variety: Dict[str, Any], weather_patterns: Dict[str, Any], crop_name: str) -> float:
        """Score variety resilience to weather variability."""
        try:
            variety_weather = variety.get('weather', '').lower()
            rainfall_variability = weather_patterns.get('rainfall_variability', 0)
            
            # Base score
            score = 50
            
            # Resilience indicators
            resilience_terms = ['adaptable', 'flexible', 'versatile', 'hardy', 'robust']
            is_resilient = any(term in variety_weather for term in resilience_terms)
            
            if rainfall_variability > 40:  # High variability
                if is_resilient:
                    score += 25
                else:
                    score -= 10
            elif rainfall_variability > 25:  # Moderate variability
                if is_resilient:
                    score += 15
                else:
                    score -= 5
            
            # Early/late maturing varieties handle variability better
            if 'early maturing' in variety_weather or 'short season' in variety_weather:
                score += 10  # Can escape late season stress
            
            return max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Error scoring variability resilience: {e}")
            return 50
    
    def _interpret_weather_score(self, weather_score: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interpret weather suitability score into human-readable format.
        
        Args:
            weather_score: Weather suitability score dictionary
            
        Returns:
            Dictionary with interpreted score information
        """
        try:
            total_score = weather_score.get('total_score', 50)
            
            # Determine suitability level
            if total_score >= 80:
                level = 'excellent'
                description = 'Highly suitable for local weather conditions'
                emoji = '🌟'
            elif total_score >= 70:
                level = 'very_good'
                description = 'Very well suited for local weather conditions'
                emoji = '✅'
            elif total_score >= 60:
                level = 'good'
                description = 'Well suited for local weather conditions'
                emoji = '👍'
            elif total_score >= 50:
                level = 'moderate'
                description = 'Moderately suited for local weather conditions'
                emoji = '⚖️'
            elif total_score >= 40:
                level = 'fair'
                description = 'Reasonably suited with some limitations'
                emoji = '⚠️'
            else:
                level = 'poor'
                description = 'May face challenges in local weather conditions'
                emoji = '🔻'
            
            return {
                'level': level,
                'description': description,
                'emoji': emoji,
                'score': total_score,
                'percentage': f"{total_score:.0f}%"
            }
            
        except Exception as e:
            logger.error(f"Error interpreting weather score: {e}")
            return {
                'level': 'unknown',
                'description': 'Weather suitability could not be determined',
                'emoji': '❓',
                'score': 50,
                'percentage': '50%'
            }

    # Phase 5: Planting Calendar Integration
    def generate_planting_calendar(self, 
                                 crop_name: str,
                                 weather_analysis: Dict[str, Any],
                                 user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate month-by-month planting calendar based on historical weather patterns.
        
        Args:
            crop_name: Name of the crop
            weather_analysis: Historical weather analysis data
            user_id: Optional user ID for logging
            
        Returns:
            Dictionary with month-by-month planting recommendations
        """
        try:
            logger.info(f"Generating planting calendar for {crop_name}", user_id)
            
            if not weather_analysis:
                return self._generate_basic_planting_calendar(crop_name)
            
            # Analyze historical weather for optimal planting windows
            planting_windows = self._analyze_optimal_planting_windows(weather_analysis, crop_name)
            
            # Generate monthly recommendations
            monthly_recommendations = self._generate_monthly_recommendations(
                crop_name, weather_analysis, planting_windows
            )
            
            # Assess drought/flood risks
            risk_assessment = self._assess_planting_risks(weather_analysis, crop_name)
            
            # Generate planting calendar
            planting_calendar = {
                'crop_name': crop_name,
                'optimal_planting_windows': planting_windows,
                'monthly_recommendations': monthly_recommendations,
                'risk_assessment': risk_assessment,
                'best_planting_month': planting_windows.get('primary_optimal_month', 'November'),
                'alternative_months': planting_windows.get('alternative_months', []),
                'avoid_months': planting_windows.get('avoid_months', []),
                'generated_at': datetime.now().isoformat()
            }
            
            logger.info(f"Planting calendar generated for {crop_name}", user_id)
            return planting_calendar
            
        except Exception as e:
            logger.error(f"Error generating planting calendar: {e}", user_id)
            return self._generate_basic_planting_calendar(crop_name)
    
    def _analyze_optimal_planting_windows(self, 
                                        weather_analysis: Dict[str, Any], 
                                        crop_name: str) -> Dict[str, Any]:
        """
        Analyze historical weather patterns to identify optimal planting windows.
        
        Args:
            weather_analysis: Historical weather analysis data
            crop_name: Name of the crop
            
        Returns:
            Dictionary with optimal planting windows
        """
        try:
            historical_data = weather_analysis.get('historical_data', {})
            monthly_averages = historical_data.get('monthly_averages', {})
            
            # Get crop maturity information
            crop_maturity = self.crop_maturity_periods.get(crop_name.lower(), {'medium': 120})
            maturity_days = crop_maturity.get('medium', 120)
            
            # Analyze each potential planting month
            planting_scores = {}
            
            for month in self.planting_months['primary_planting']:
                score = self._score_planting_month(
                    month, monthly_averages, maturity_days, historical_data
                )
                planting_scores[month] = score
            
            # Find optimal and alternative months
            sorted_months = sorted(planting_scores.items(), key=lambda x: x[1], reverse=True)
            
            optimal_month = sorted_months[0][0] if sorted_months else 'November'
            alternative_months = [month for month, score in sorted_months[1:3] if score > 60]
            avoid_months = [month for month, score in sorted_months if score < 40]
            
            return {
                'primary_optimal_month': optimal_month,
                'alternative_months': alternative_months,
                'avoid_months': avoid_months,
                'month_scores': planting_scores,
                'maturity_days': maturity_days
            }
            
        except Exception as e:
            logger.error(f"Error analyzing optimal planting windows: {e}")
            return {
                'primary_optimal_month': 'November',
                'alternative_months': ['December', 'January'],
                'avoid_months': [],
                'month_scores': {},
                'maturity_days': 120
            }
    
    def _score_planting_month(self, 
                            month: str, 
                            monthly_averages: Dict[str, float], 
                            maturity_days: int,
                            historical_data: Dict[str, Any]) -> float:
        """
        Score a planting month based on weather suitability.
        
        Args:
            month: Month name to score
            monthly_averages: Monthly rainfall averages
            maturity_days: Crop maturity period in days
            historical_data: Historical weather data
            
        Returns:
            Score from 0-100 for the planting month
        """
        try:
            score = 50  # Base score
            
            # Get planting month rainfall
            planting_rainfall = monthly_averages.get(month, 0)
            
            # Calculate growing season months
            growing_months = self._calculate_growing_season_months(month, maturity_days)
            
            # Score based on planting month rainfall
            if 50 <= planting_rainfall <= 150:  # Optimal range
                score += 20
            elif 30 <= planting_rainfall <= 200:  # Good range
                score += 10
            elif planting_rainfall < 20:  # Too dry
                score -= 15
            elif planting_rainfall > 250:  # Too wet
                score -= 10
            
            # Score based on growing season rainfall
            growing_season_rainfall = sum(
                monthly_averages.get(grow_month, 0) for grow_month in growing_months
            )
            
            if growing_season_rainfall > 400:  # Good total rainfall
                score += 15
            elif growing_season_rainfall > 300:  # Adequate rainfall
                score += 10
            elif growing_season_rainfall < 200:  # Insufficient rainfall
                score -= 20
            
            # Consider drought and flood risks
            drought_years = len(historical_data.get('drought_years', []))
            flood_years = len(historical_data.get('flood_years', []))
            total_years = historical_data.get('years_analyzed', 1)
            
            if drought_years / total_years > 0.3:  # High drought risk
                score -= 10
            if flood_years / total_years > 0.3:  # High flood risk
                score -= 5
            
            # Seasonal timing bonus
            if month in ['November', 'December']:  # Peak planting season
                score += 10
            elif month in ['January', 'October']:  # Good timing
                score += 5
            
            return max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Error scoring planting month {month}: {e}")
            return 50
    
    def _calculate_growing_season_months(self, planting_month: str, maturity_days: int) -> List[str]:
        """
        Calculate the months during which a crop will be growing.
        
        Args:
            planting_month: Month when crop is planted
            maturity_days: Number of days to maturity
            
        Returns:
            List of month names during growing season
        """
        try:
            # Get month number (1-12)
            month_num = datetime.strptime(planting_month, '%B').month
            
            # Calculate number of months for growing season
            growing_months_count = (maturity_days // 30) + 1
            
            # Generate list of growing months
            growing_months = []
            for i in range(growing_months_count):
                current_month_num = ((month_num + i - 1) % 12) + 1
                month_name = calendar.month_name[current_month_num]
                growing_months.append(month_name)
            
            return growing_months
            
        except Exception as e:
            logger.error(f"Error calculating growing season months: {e}")
            return [planting_month]
    
    def _generate_monthly_recommendations(self, 
                                        crop_name: str,
                                        weather_analysis: Dict[str, Any],
                                        planting_windows: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Generate month-by-month planting recommendations.
        
        Args:
            crop_name: Name of the crop
            weather_analysis: Historical weather analysis data
            planting_windows: Optimal planting windows
            
        Returns:
            Dictionary with recommendations for each month
        """
        try:
            monthly_recommendations = {}
            historical_data = weather_analysis.get('historical_data', {})
            monthly_averages = historical_data.get('monthly_averages', {})
            
            # All months to provide recommendations for
            all_months = [
                'January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December'
            ]
            
            for month in all_months:
                month_rainfall = monthly_averages.get(month, 0)
                month_score = planting_windows.get('month_scores', {}).get(month, 50)
                
                # Determine recommendation type
                if month == planting_windows.get('primary_optimal_month'):
                    recommendation_type = 'optimal'
                elif month in planting_windows.get('alternative_months', []):
                    recommendation_type = 'alternative'
                elif month in planting_windows.get('avoid_months', []):
                    recommendation_type = 'avoid'
                elif month in self.planting_months['primary_planting']:
                    recommendation_type = 'possible'
                else:
                    recommendation_type = 'not_recommended'
                
                # Generate specific recommendation
                recommendation = self._generate_month_specific_recommendation(
                    month, crop_name, month_rainfall, month_score, recommendation_type
                )
                
                monthly_recommendations[month] = recommendation
            
            return monthly_recommendations
            
        except Exception as e:
            logger.error(f"Error generating monthly recommendations: {e}")
            return {}
    
    def _generate_month_specific_recommendation(self, 
                                             month: str, 
                                             crop_name: str,
                                             month_rainfall: float,
                                             month_score: float,
                                             recommendation_type: str) -> Dict[str, Any]:
        """
        Generate specific recommendation for a month.
        
        Args:
            month: Month name
            crop_name: Name of the crop
            month_rainfall: Average rainfall for the month
            month_score: Planting score for the month
            recommendation_type: Type of recommendation
            
        Returns:
            Dictionary with month-specific recommendation
        """
        try:
            # Base recommendation structure
            recommendation = {
                'month': month,
                'recommendation_type': recommendation_type,
                'planting_score': month_score,
                'average_rainfall': month_rainfall,
                'activities': [],
                'risks': [],
                'opportunities': [],
                'advice': ''
            }
            
            # Generate recommendation based on type
            if recommendation_type == 'optimal':
                recommendation['activities'] = [
                    f"🌱 OPTIMAL TIME: Plant {crop_name} varieties",
                    "🌧️ Take advantage of good rainfall patterns",
                    "🌾 Prepare fields and plant quality seeds",
                    "💧 Ensure proper drainage systems"
                ]
                recommendation['advice'] = f"Best month for {crop_name} planting with {month_rainfall:.0f}mm average rainfall"
                
            elif recommendation_type == 'alternative':
                recommendation['activities'] = [
                    f"🌱 GOOD TIME: Plant {crop_name} varieties",
                    "🌧️ Monitor rainfall patterns closely",
                    "🌾 Consider early-maturing varieties",
                    "💧 Plan for supplemental irrigation if needed"
                ]
                recommendation['advice'] = f"Good alternative month for {crop_name} with {month_rainfall:.0f}mm rainfall"
                
            elif recommendation_type == 'avoid':
                recommendation['activities'] = [
                    f"⚠️ AVOID: Not recommended for {crop_name} planting",
                    "🌧️ Rainfall patterns not suitable",
                    "🌾 Use time for field preparation",
                    "📚 Plan for better planting months"
                ]
                recommendation['advice'] = f"Avoid planting {crop_name} - only {month_rainfall:.0f}mm average rainfall"
                
            elif recommendation_type == 'possible':
                recommendation['activities'] = [
                    f"🌱 POSSIBLE: {crop_name} can be planted with care",
                    "🌧️ Monitor weather forecasts closely",
                    "🌾 Use drought-tolerant varieties",
                    "💧 Plan for water management"
                ]
                recommendation['advice'] = f"Possible to plant {crop_name} with {month_rainfall:.0f}mm rainfall but requires care"
                
            else:  # not_recommended
                recommendation['activities'] = [
                    f"❌ NOT RECOMMENDED: {crop_name} planting not advised",
                    "🌧️ Seasonal patterns not suitable",
                    "🌾 Focus on field preparation or other crops",
                    "📅 Plan for optimal planting months"
                ]
                recommendation['advice'] = f"Not recommended for {crop_name} planting ({month_rainfall:.0f}mm rainfall)"
            
            # Add risk assessment
            if month_rainfall < 30:
                recommendation['risks'].append("🌵 High drought risk")
            elif month_rainfall > 200:
                recommendation['risks'].append("🌊 High flood risk")
            
            if month_score < 40:
                recommendation['risks'].append("📉 Low success probability")
            
            # Add opportunities
            if month_score > 70:
                recommendation['opportunities'].append("✅ High success probability")
            
            if 50 <= month_rainfall <= 150:
                recommendation['opportunities'].append("🌧️ Optimal rainfall range")
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error generating month-specific recommendation: {e}")
            return {
                'month': month,
                'recommendation_type': 'unknown',
                'advice': 'Unable to generate recommendation'
            }
    
    def _assess_planting_risks(self, 
                             weather_analysis: Dict[str, Any], 
                             crop_name: str) -> Dict[str, Any]:
        """
        Assess drought and flood risks for planting decisions.
        
        Args:
            weather_analysis: Historical weather analysis data
            crop_name: Name of the crop
            
        Returns:
            Dictionary with risk assessment
        """
        try:
            historical_data = weather_analysis.get('historical_data', {})
            
            # Calculate risk indicators
            drought_years = len(historical_data.get('drought_years', []))
            flood_years = len(historical_data.get('flood_years', []))
            total_years = historical_data.get('years_analyzed', 1)
            rainfall_variability = historical_data.get('rainfall_variability', 0)
            
            # Calculate risk levels
            drought_risk = drought_years / total_years if total_years > 0 else 0
            flood_risk = flood_years / total_years if total_years > 0 else 0
            
            # Determine risk levels
            drought_level = 'high' if drought_risk > 0.3 else 'moderate' if drought_risk > 0.1 else 'low'
            flood_level = 'high' if flood_risk > 0.3 else 'moderate' if flood_risk > 0.1 else 'low'
            variability_level = 'high' if rainfall_variability > 40 else 'moderate' if rainfall_variability > 25 else 'low'
            
            # Generate risk mitigation strategies
            mitigation_strategies = []
            
            if drought_level == 'high':
                mitigation_strategies.extend([
                    "🌵 Use drought-tolerant varieties",
                    "💧 Implement water harvesting systems",
                    "🌱 Consider early-maturing varieties",
                    "📅 Plant at optimal timing"
                ])
            
            if flood_level == 'high':
                mitigation_strategies.extend([
                    "🌊 Ensure proper field drainage",
                    "🏔️ Use raised beds or ridges",
                    "🌾 Plant flood-tolerant varieties",
                    "📍 Choose well-drained locations"
                ])
            
            if variability_level == 'high':
                mitigation_strategies.extend([
                    "📊 Monitor weather forecasts closely",
                    "🌾 Diversify with multiple varieties",
                    "📅 Stagger planting dates",
                    "💧 Have backup irrigation plans"
                ])
            
            return {
                'drought_risk': {
                    'level': drought_level,
                    'probability': round(drought_risk * 100, 1),
                    'recent_years': historical_data.get('drought_years', [])[-3:]
                },
                'flood_risk': {
                    'level': flood_level,
                    'probability': round(flood_risk * 100, 1),
                    'recent_years': historical_data.get('flood_years', [])[-3:]
                },
                'rainfall_variability': {
                    'level': variability_level,
                    'percentage': round(rainfall_variability, 1)
                },
                'mitigation_strategies': mitigation_strategies,
                'overall_risk_level': 'high' if drought_level == 'high' or flood_level == 'high' else 'moderate' if variability_level == 'high' else 'low'
            }
            
        except Exception as e:
            logger.error(f"Error assessing planting risks: {e}")
            return {
                'drought_risk': {'level': 'unknown', 'probability': 0},
                'flood_risk': {'level': 'unknown', 'probability': 0},
                'rainfall_variability': {'level': 'unknown', 'percentage': 0},
                'mitigation_strategies': [],
                'overall_risk_level': 'unknown'
            }
    
    def _generate_basic_planting_calendar(self, crop_name: str) -> Dict[str, Any]:
        """
        Generate basic planting calendar when weather analysis is unavailable.
        
        Args:
            crop_name: Name of the crop
            
        Returns:
            Basic planting calendar dictionary
        """
        try:
            # Default planting recommendations for Malawi
            basic_calendar = {
                'crop_name': crop_name,
                'best_planting_month': 'November',
                'alternative_months': ['December', 'January'],
                'avoid_months': ['May', 'June', 'July', 'August'],
                'monthly_recommendations': {
                    'November': {
                        'recommendation_type': 'optimal',
                        'advice': f'Best time to plant {crop_name} - start of rainy season'
                    },
                    'December': {
                        'recommendation_type': 'alternative',
                        'advice': f'Good time to plant {crop_name} - rainy season continues'
                    },
                    'January': {
                        'recommendation_type': 'alternative',
                        'advice': f'Last good chance to plant {crop_name} this season'
                    }
                },
                'risk_assessment': {
                    'overall_risk_level': 'unknown',
                    'mitigation_strategies': [
                        "🌧️ Monitor local weather conditions",
                        "🌾 Use locally adapted varieties",
                        "📅 Plant at traditional timing"
                    ]
                },
                'note': 'Basic recommendations - location-specific weather analysis not available',
                'generated_at': datetime.now().isoformat()
            }
            
            return basic_calendar
            
        except Exception as e:
            logger.error(f"Error generating basic planting calendar: {e}")
            return {
                'crop_name': crop_name,
                'note': 'Unable to generate planting calendar',
                'generated_at': datetime.now().isoformat()
            }

def parse_varieties_arguments(args: List[str]) -> Tuple[str, Optional[Tuple[float, float]]]:
    """
    Parse varieties command arguments to extract crop name and optional coordinates.
    
    Args:
        args: List of command arguments
        
    Returns:
        Tuple of (crop_name, coordinates) where coordinates is None if not provided
    """
    if not args:
        return "", None
    
    # Convert args to string for easier parsing
    args_text = ' '.join(args)
    
    # Common coordinate patterns to detect
    coordinate_patterns = [
        r'-?\d+\.?\d*\s*,\s*-?\d+\.?\d*',  # Decimal coordinates: -13.9833, 33.7833
        r'-?\d+\.?\d*\s*[NS]\s*,\s*-?\d+\.?\d*\s*[EW]',  # With N/S/E/W
    ]
    
    # Check if any coordinate pattern is found
    coordinate_match = None
    for pattern in coordinate_patterns:
        match = re.search(pattern, args_text)
        if match:
            coordinate_match = match
            break
    
    if coordinate_match:
        # Extract coordinates part
        coordinate_text = coordinate_match.group()
        
        # Remove coordinates from args_text to get crop name
        crop_name = args_text.replace(coordinate_text, '').strip()
        
        # Parse coordinates using existing coordinate handler
        coordinates = coordinate_handler.parse_coordinates(coordinate_text)
        
        return crop_name, coordinates
    
    else:
        # No coordinates found, check if it's a known location
        # Try to parse the entire text as coordinates first
        coordinates = coordinate_handler.parse_coordinates(args_text)
        if coordinates:
            # If entire text is coordinates, no crop name provided
            return "", coordinates
        
        # Check if last few words might be a location
        words = args_text.split()
        if len(words) >= 2:
            # Try different combinations
            for i in range(1, len(words)):
                potential_crop = ' '.join(words[:i])
                potential_location = ' '.join(words[i:])
                
                # Test if potential_location is a valid location
                coordinates = coordinate_handler.parse_coordinates(potential_location)
                if coordinates:
                    return potential_crop, coordinates
        
        # No coordinates found, treat everything as crop name
        return args_text, None


# Create handler instance
varieties_handler = VarietiesHandler()


async def varieties_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /varieties command for crop variety information.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    user_id = str(update.effective_user.id)
    
    # Parse arguments to extract crop name and optional coordinates
    crop_name, coordinates = parse_varieties_arguments(context.args) if context.args else ("", None)
    
    # Log the query with coordinates info
    location_info = f" {coordinates}" if coordinates else ""
    logger.log_user_query(user_id, f"/varieties {crop_name}{location_info}", "command")
    
    if not crop_name:
        await update.message.reply_text(
            "🌱 Please specify a crop name for variety information!\n\n"
            "**Examples:**\n"
            "• `/varieties groundnut`\n"
            "• `/varieties maize`\n"
            "• `/varieties bean`\n"
            "• `/varieties soybean`\n"
            "• `/varieties tomato`\n\n"
            "**New: Location-based recommendations:**\n"
            "• `/varieties groundnut -13.9833, 33.7833`\n"
            "• `/varieties maize Lilongwe`\n"
            "• `/varieties soybean Area 1`\n\n"
            "**What you'll get:**\n"
            "• Variety names and types\n"
            "• Planting times and seasons\n"
            "• Expected yields per hectare\n"
            "• Weather and soil requirements\n"
            "• Growing areas and districts\n"
            "• Location-specific recommendations (when coordinates provided)\n\n"
            "Use `/help` for more commands.",
            parse_mode='Markdown'
        )
        logger.log_bot_response(user_id, "varieties_error", False)
        return
    
    # Send "typing" indicator
    await update.message.reply_chat_action("typing")
    
    # Add location context to search if coordinates provided
    if coordinates:
        lat, lon = coordinates
        location_context = f" location {lat} {lon}"
        progress_message_text = f"🔍 Searching for {crop_name} varieties near {lat:.3f}, {lon:.3f}...\n🌦️ Analyzing weather patterns...\n🤖 Processing with AI..."
    else:
        location_context = ""
        progress_message_text = f"🔍 Searching for {crop_name} varieties...\n🤖 Analyzing with AI..."
    
    try:
        # Phase 2: Get weather analysis if coordinates provided
        weather_analysis = None
        if coordinates:
            lat, lon = coordinates
            # Clear old cache entries periodically
            varieties_handler._clear_old_cache_entries()
            
            # Get weather analysis with 5 years of historical data
            weather_analysis = varieties_handler.get_location_weather_analysis(lat, lon, 5, user_id)
            
            if weather_analysis:
                logger.info(f"Weather analysis integrated for {crop_name} at {lat}, {lon}", user_id)
            else:
                logger.warning(f"Weather analysis failed for {lat}, {lon}, proceeding without it", user_id)
        
        # Search for variety information in knowledge base
        search_query = f"{crop_name} varieties cultivars types characteristics recommendations{location_context}"
        search_results = varieties_handler.search_varieties_knowledge(search_query, top_k=10)
        
        if not search_results:
            location_suggestion = f"\n\n**Try with location:**\n• `/varieties {crop_name} Lilongwe`\n• `/varieties {crop_name} -13.9833, 33.7833`" if not coordinates else ""
            
            await update.message.reply_text(
                f"❌ No variety information found for '{crop_name}' in the knowledge base.\n\n"
                "**Possible reasons:**\n"
                "• Crop name not recognized\n"
                "• Limited information available\n"
                "• Try a different crop name\n\n"
                "**Common crops with variety info:**\n"
                "• Groundnut (Peanut)\n"
                "• Maize (Corn)\n"
                "• Bean\n"
                "• Soybean\n"
                "• Tomato\n\n"
                "**Alternative:**\n"
                f"Try `/crops [location]` for general crop recommendations.{location_suggestion}",
                parse_mode='Markdown'
            )
            logger.log_bot_response(user_id, "varieties_no_results", False)
            return
        
        # Send progress message
        progress_message = await update.message.reply_text(
            progress_message_text,
            parse_mode='Markdown'
        )
        
        # Extract variety information
        variety_info = varieties_handler.extract_variety_info(search_results, crop_name)
        
        # Check if we have meaningful information (updated for new structure)
        # Get AI parsed varieties 
        search_results_for_ai = variety_info.get('general_info', [])
        ai_parsed_info = varieties_handler.parse_varieties_with_ai(search_results_for_ai, crop_name)
        has_varieties = len(ai_parsed_info.get('varieties', [])) > 0
        
        if not has_varieties:
            # Delete progress message
            try:
                await progress_message.delete()
            except:
                pass
                
            location_suggestion = f"\n\n**Try with location:**\n• `/varieties {crop_name} Lilongwe`\n• `/varieties {crop_name} -13.9833, 33.7833`" if not coordinates else ""
            
            await update.message.reply_text(
                f"🔍 Found documents about '{crop_name}' but no specific variety information.\n\n"
                "**What was found:**\n"
                f"• {len(search_results)} relevant documents\n"
                f"• From {len(set(r['source'] for r in search_results))} sources\n\n"
                "**Suggestions:**\n"
                "• Try a more specific crop name\n"
                "• Use `/crops [location]` for general recommendations\n"
                "• Check alternative spellings\n\n"
                "**Example specific names:**\n"
                "• `groundnut` instead of `peanut`\n"
                "• `maize` instead of `corn`\n"
                f"• `common bean` instead of `bean`{location_suggestion}",
                parse_mode='Markdown'
            )
            logger.log_bot_response(user_id, "varieties_no_specific_info", False)
            return
        
        # Phase 3: Weather-Variety Matching Algorithm
        varieties_list = ai_parsed_info.get('varieties', [])
        if coordinates and weather_analysis and varieties_list:
            # Apply weather-variety matching algorithm
            try:
                logger.info(f"Applying weather-variety matching for {len(varieties_list)} varieties", user_id)
                weather_matched_varieties = varieties_handler.match_varieties_to_weather(
                    varieties_list, weather_analysis, crop_name, user_id
                )
                
                # Update AI parsed info with weather-matched varieties
                ai_parsed_info['varieties'] = weather_matched_varieties
                ai_parsed_info['weather_matched'] = True
                
                logger.info(f"Weather-variety matching completed for {crop_name}", user_id)
                
            except Exception as e:
                logger.error(f"Error in weather-variety matching: {e}", user_id)
                # Continue with unmatched varieties if weather matching fails
                ai_parsed_info['weather_matched'] = False
        else:
            ai_parsed_info['weather_matched'] = False
        
        # Phase 5: Generate planting calendar if coordinates provided
        planting_calendar = None
        if coordinates and weather_analysis:
            try:
                logger.info(f"Generating planting calendar for {crop_name}", user_id)
                planting_calendar = varieties_handler.generate_planting_calendar(
                    crop_name, weather_analysis, user_id
                )
                logger.info(f"Planting calendar generated for {crop_name}", user_id)
            except Exception as e:
                logger.error(f"Error generating planting calendar: {e}", user_id)
                # Continue without planting calendar if generation fails
                planting_calendar = None
        
        # Delete progress message
        try:
            await progress_message.delete()
        except:
            pass
        
        # Store coordinates and weather analysis for future use (Phase 2+)
        variety_info['coordinates'] = coordinates
        variety_info['weather_analysis'] = weather_analysis
        variety_info['ai_parsed_info'] = ai_parsed_info  # Pass processed varieties to formatter
        variety_info['planting_calendar'] = planting_calendar  # Phase 5: Add planting calendar
        
        # Format and send response
        response_message = varieties_handler.format_varieties_response(variety_info, crop_name)
        
        # Phase 2: Add location and weather context to response if coordinates provided
        if coordinates:
            lat, lon = coordinates
            location_header = f"📍 **Location-based recommendations for {lat:.3f}, {lon:.3f}**\n"
            
            # Add weather context if available
            if weather_analysis:
                weather_context = varieties_handler._format_weather_context(weather_analysis)
                response_message = location_header + weather_context + "\n" + response_message
            else:
                response_message = location_header + "\n" + response_message
        
        await update.message.reply_text(response_message, parse_mode='Markdown')
        logger.log_bot_response(user_id, "varieties_success", True)
        
    except Exception as e:
        # Delete progress message if it exists
        try:
            await progress_message.delete()
        except:
            pass
            
        logger.error(f"Error in varieties command: {e}", user_id)
        
        # Handle timeout errors specifically
        if "timed out" in str(e).lower() or "timeout" in str(e).lower():
            error_message = f"""⏱️ Request timed out while analyzing '{crop_name}' varieties.

**This usually means:**
• AI processing took longer than expected
• Try a more specific crop name
• Check your internet connection

**Quick alternatives:**
• Use `/crops [location]` for general recommendations
• Try `/weather [location]` for weather info
• Use `/help` for other commands

**Common crops that work well:**
• groundnut, maize, soybean, common bean

Please try again in a moment."""
        else:
            error_message = f"""❌ Error retrieving variety information for '{crop_name}'.

**Possible Issues:**
• Knowledge base temporarily unavailable
• Embedding generation failed
• Database connection error

**Try These Solutions:**
• Wait 30 seconds and try again
• Check your crop name spelling
• Use `/crops [location]` for general recommendations
• Try `/help` for other available commands

**Common Crops:**
• groundnut, maize, bean, soybean, tomato

Please try again in a moment."""
        
        await update.message.reply_text(error_message, parse_mode='Markdown')
        logger.log_bot_response(user_id, "varieties_processing_error", False)