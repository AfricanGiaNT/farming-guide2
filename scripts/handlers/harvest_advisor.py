#!/usr/bin/env python3
"""
Harvest Advisor Handler - Phase 6
Provides harvest timing, drying, storage, and post-harvest loss prevention advice
Leverages existing vector database and agricultural knowledge base
Enhanced with AI-powered insights and personalized recommendations
"""

import os
import sys
import re
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from scripts.data_pipeline.semantic_search import SemanticSearch
from scripts.ai_agent.gpt_integration import GPTIntegration
from scripts.ai_agent.prompt_formatter import prompt_formatter
from scripts.utils.logger import logger
from scripts.weather_engine.coordinate_handler import coordinate_handler
from scripts.weather_engine.historical_weather_api import HistoricalWeatherAPI


class HarvestAdvisor:
    """
    Harvest and Post-Harvest Advisory System
    Provides comprehensive harvest timing, drying, storage, and loss prevention advice
    Enhanced with AI-powered insights and personalized recommendations
    """
    
    def __init__(self):
        """Initialize the harvest advisor."""
        self.semantic_search = SemanticSearch()
        self.gpt_integration = GPTIntegration()
        self.prompt_formatter = prompt_formatter
        self.coordinate_handler = coordinate_handler
        self.weather_data = HistoricalWeatherAPI()
        
        # Harvest-related search categories
        self.harvest_categories = {
            'timing': ['harvest timing', 'when to harvest', 'optimal harvest', 'harvest season'],
            'drying': ['drying methods', 'sun drying', 'artificial drying', 'moisture content'],
            'storage': ['storage methods', 'warehouse storage', 'container storage', 'preservation'],
            'loss_prevention': ['post harvest loss', 'quality maintenance', 'spoilage prevention'],
            'processing': ['value addition', 'processing methods', 'market preparation']
        }
        
        logger.info("HarvestAdvisor initialized successfully with AI enhancement")
    
    async def get_harvest_advice(self, crop: str, location: Optional[str] = None, 
                                user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get comprehensive harvest advice for a specific crop and location.
        Enhanced with AI-powered insights and personalized recommendations.
        
        Args:
            crop: Crop name (e.g., 'maize', 'beans', 'groundnuts')
            location: Location coordinates or name
            user_id: User identifier for personalization
            
        Returns:
            Dictionary with harvest advice sections including AI insights
        """
        try:
            logger.info(f"Generating AI-enhanced harvest advice for {crop} at {location}")
            
            # Get location-specific weather data if coordinates provided
            weather_context = {}
            if location:
                coords = self.coordinate_handler.parse_coordinates(location, user_id)
                if coords:
                    weather_context = self._get_weather_context({'lat': coords[0], 'lon': coords[1]}, crop)
            
            # Search knowledge base for harvest information
            harvest_knowledge = self._search_harvest_knowledge(crop)
            
            # Generate base advice
            base_advice = {
                'crop': crop,
                'location': location,
                'weather_context': weather_context,
                'harvest_timing': self._get_harvest_timing(crop, harvest_knowledge, weather_context),
                'drying_recommendations': self._get_drying_recommendations(crop, harvest_knowledge),
                'storage_guidelines': self._get_storage_guidelines(crop, harvest_knowledge),
                'loss_prevention': self._get_loss_prevention(crop, harvest_knowledge),
                'processing_advice': self._get_processing_advice(crop, harvest_knowledge),
                'quality_standards': self._get_quality_standards(crop, harvest_knowledge),
                'generated_at': datetime.now().isoformat()
            }
            
            # Enhance with AI insights
            enhanced_advice = await self._enhance_with_ai(base_advice, crop, location, user_id)
            
            logger.info(f"Successfully generated AI-enhanced harvest advice for {crop}")
            return enhanced_advice
            
        except Exception as e:
            logger.error(f"Error generating harvest advice: {str(e)}")
            return {
                'error': f"Failed to generate harvest advice: {str(e)}",
                'crop': crop,
                'location': location
            }
    
    async def _enhance_with_ai(self, base_advice: Dict[str, Any], crop: str, 
                              location: str, user_id: str) -> Dict[str, Any]:
        """
        Enhance harvest advice with AI-powered insights and personalized recommendations.
        
        Args:
            base_advice: Base harvest advice
            crop: Crop name
            location: Location string
            user_id: User identifier
            
        Returns:
            Enhanced advice with AI insights
        """
        try:
            # Create AI prompt for harvest enhancement
            prompt = self._create_harvest_ai_prompt(base_advice, crop, location)
            
            # Get AI response
            ai_response = await self._get_ai_response(prompt, user_id)
            
            # Parse AI insights
            ai_insights = self._parse_ai_harvest_insights(ai_response)
            
            # Integrate AI insights into base advice
            enhanced_advice = base_advice.copy()
            enhanced_advice['ai_insights'] = ai_insights
            enhanced_advice['ai_enhanced'] = True
            enhanced_advice['ai_generated_at'] = datetime.now().isoformat()
            
            # Add personalized recommendations
            enhanced_advice['personalized_recommendations'] = await self._generate_personalized_recommendations(
                base_advice, crop, location, user_id
            )
            
            # Add risk assessment
            enhanced_advice['risk_assessment'] = await self._assess_harvest_risks(
                base_advice, crop, location, user_id
            )
            
            return enhanced_advice
            
        except Exception as e:
            logger.error(f"Error enhancing with AI: {str(e)}")
            # Return base advice if AI enhancement fails
            base_advice['ai_enhanced'] = False
            base_advice['ai_error'] = str(e)
            return base_advice
    
    def _create_harvest_ai_prompt(self, base_advice: Dict[str, Any], crop: str, location: str) -> str:
        """
        Create AI prompt for harvest advice enhancement.
        
        Args:
            base_advice: Base harvest advice
            crop: Crop name
            location: Location string
            
        Returns:
            Formatted AI prompt
        """
        weather_context = base_advice.get('weather_context', {})
        timing = base_advice.get('harvest_timing', {})
        drying = base_advice.get('drying_recommendations', {})
        storage = base_advice.get('storage_guidelines', {})
        
        # Extract key weather data
        rainfall_patterns = weather_context.get('rainfall_patterns', {})
        drying_conditions = weather_context.get('drying_conditions', {})
        storage_risks = weather_context.get('storage_risks', {})
        
        prompt = f"""As an agricultural expert for {location}, enhance harvest advice for {crop}:

CURRENT CONDITIONS:
- Crop: {crop}
- Location: {location}
- Weather patterns: {list(rainfall_patterns.keys())[:3] if rainfall_patterns else 'Unknown'}

EXISTING RECOMMENDATIONS:
- Timing: {len(timing.get('knowledge_based_timing', []))} timing recommendations
- Drying: {len(drying.get('methods', []))} drying methods
- Storage: {len(storage.get('storage_methods', []))} storage methods

Provide enhanced insights:
1. **Risk Assessment**: Identify specific risks for {crop} harvest in {location}
2. **Timing Optimization**: Suggest optimal harvest windows based on weather patterns
3. **Quality Enhancement**: Recommend practices to maximize crop quality
4. **Market Timing**: Suggest best times to sell for maximum profit
5. **Resource Optimization**: Recommend cost-effective harvest and storage methods

Focus on practical, actionable advice specific to {location} conditions.
Keep response under 300 words with clear bullet points."""

        return prompt
    
    async def _get_ai_response(self, prompt: str, user_id: str) -> str:
        """
        Get AI response for harvest enhancement.
        
        Args:
            prompt: AI prompt
            user_id: User identifier
            
        Returns:
            AI response text
        """
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.gpt_integration.client.chat.completions.create(
                    model=self.gpt_integration.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert agricultural advisor specializing in harvest and post-harvest management for Malawi. Provide practical, location-specific advice that farmers can implement immediately."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=400,
                    temperature=0.7
                )
            )
            
            ai_text = response.choices[0].message.content.strip()
            logger.info(f"AI harvest enhancement generated for user {user_id}")
            return ai_text
            
        except Exception as e:
            logger.error(f"Error getting AI response: {str(e)}")
            raise
    
    def _parse_ai_harvest_insights(self, ai_response: str) -> Dict[str, Any]:
        """
        Parse AI response into structured harvest insights.
        
        Args:
            ai_response: Raw AI response
            
        Returns:
            Structured insights dictionary
        """
        insights = {
            'risk_assessment': [],
            'timing_optimization': [],
            'quality_enhancement': [],
            'market_timing': [],
            'resource_optimization': [],
            'raw_response': ai_response
        }
        
        # Parse response by sections
        lines = ai_response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect section headers
            if 'risk' in line.lower() and 'assessment' in line.lower():
                current_section = 'risk_assessment'
            elif 'timing' in line.lower() and 'optimization' in line.lower():
                current_section = 'timing_optimization'
            elif 'quality' in line.lower() and 'enhancement' in line.lower():
                current_section = 'quality_enhancement'
            elif 'market' in line.lower() and 'timing' in line.lower():
                current_section = 'market_timing'
            elif 'resource' in line.lower() and 'optimization' in line.lower():
                current_section = 'resource_optimization'
            elif line.startswith('•') or line.startswith('-') or line.startswith('*'):
                # Extract bullet point
                if current_section and current_section in insights:
                    cleaned_point = line.lstrip('•-* ').strip()
                    if cleaned_point:
                        insights[current_section].append(cleaned_point)
        
        return insights
    
    async def _generate_personalized_recommendations(self, base_advice: Dict[str, Any], 
                                                   crop: str, location: str, user_id: str) -> List[str]:
        """
        Generate personalized harvest recommendations based on user context.
        
        Args:
            base_advice: Base harvest advice
            crop: Crop name
            location: Location string
            user_id: User identifier
            
        Returns:
            List of personalized recommendations
        """
        try:
            # Create personalized prompt
            prompt = f"""Generate 3 personalized harvest recommendations for {crop} in {location}:

Consider:
- Local weather patterns
- Crop-specific requirements
- Practical implementation
- Resource constraints

Provide specific, actionable steps that a farmer can take immediately.
Format as numbered list, max 20 words each."""

            # Get AI response
            ai_response = await self._get_ai_response(prompt, user_id)
            
            # Parse recommendations
            recommendations = []
            lines = ai_response.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line.startswith('1.') or line.startswith('2.') or line.startswith('3.')):
                    cleaned_rec = line.lstrip('123. ').strip()
                    if cleaned_rec:
                        recommendations.append(cleaned_rec)
            
            return recommendations[:3]  # Limit to 3 recommendations
            
        except Exception as e:
            logger.error(f"Error generating personalized recommendations: {str(e)}")
            return [
                f"Monitor {crop} maturity indicators regularly",
                f"Prepare drying area for {crop} harvest",
                f"Check storage containers for {crop} preservation"
            ]
    
    async def _assess_harvest_risks(self, base_advice: Dict[str, Any], crop: str, 
                                  location: str, user_id: str) -> Dict[str, Any]:
        """
        Assess harvest risks using AI analysis.
        
        Args:
            base_advice: Base harvest advice
            crop: Crop name
            location: Location string
            user_id: User identifier
            
        Returns:
            Risk assessment dictionary
        """
        try:
            weather_context = base_advice.get('weather_context', {})
            storage_risks = weather_context.get('storage_risks', {})
            
            # Create risk assessment prompt
            prompt = f"""Assess harvest risks for {crop} in {location}:

WEATHER CONTEXT:
- Rainfall patterns: {list(weather_context.get('rainfall_patterns', {}).keys())[:3] if weather_context.get('rainfall_patterns') else 'Unknown'}
- Storage risks: {len(storage_risks.get('high_humidity_months', []))} high humidity months

Identify:
1. Weather-related risks
2. Storage risks
3. Quality risks
4. Market risks

Provide risk level (low/medium/high) and mitigation strategies.
Format as structured response."""

            # Get AI response
            ai_response = await self._get_ai_response(prompt, user_id)
            
            # Parse risk assessment
            risk_assessment = {
                'weather_risks': {'level': 'medium', 'mitigation': []},
                'storage_risks': {'level': 'medium', 'mitigation': []},
                'quality_risks': {'level': 'medium', 'mitigation': []},
                'market_risks': {'level': 'medium', 'mitigation': []},
                'overall_risk_level': 'medium',
                'ai_analysis': ai_response
            }
            
            # Extract risk levels and mitigation from AI response
            lines = ai_response.split('\n')
            current_risk = None
            
            for line in lines:
                line = line.strip().lower()
                if 'weather' in line and 'risk' in line:
                    current_risk = 'weather_risks'
                elif 'storage' in line and 'risk' in line:
                    current_risk = 'storage_risks'
                elif 'quality' in line and 'risk' in line:
                    current_risk = 'quality_risks'
                elif 'market' in line and 'risk' in line:
                    current_risk = 'market_risks'
                elif current_risk and ('low' in line or 'medium' in line or 'high' in line):
                    if 'low' in line:
                        risk_assessment[current_risk]['level'] = 'low'
                    elif 'high' in line:
                        risk_assessment[current_risk]['level'] = 'high'
            
            return risk_assessment
            
        except Exception as e:
            logger.error(f"Error assessing harvest risks: {str(e)}")
            return {
                'weather_risks': {'level': 'medium', 'mitigation': ['Monitor weather forecasts']},
                'storage_risks': {'level': 'medium', 'mitigation': ['Use proper storage containers']},
                'quality_risks': {'level': 'medium', 'mitigation': ['Handle crops carefully']},
                'market_risks': {'level': 'medium', 'mitigation': ['Research market prices']},
                'overall_risk_level': 'medium',
                'ai_analysis': 'Risk assessment unavailable'
            }
    
    def _get_weather_context(self, coords: Dict[str, float], crop: str) -> Dict[str, Any]:
        """Get weather context for harvest timing decisions."""
        try:
            # Get historical rainfall data
            rainfall_data = self.weather_data.get_historical_rainfall(
                coords['lat'], coords['lon'], years=5
            )
            
            if not rainfall_data:
                return {}
            
            # Analyze rainfall patterns for harvest timing
            weather_context = {
                'coordinates': coords,
                'rainfall_patterns': rainfall_data.monthly_averages,
                'drying_conditions': self._analyze_drying_conditions(rainfall_data),
                'storage_risks': self._analyze_storage_risks(rainfall_data)
            }
            
            return weather_context
            
        except Exception as e:
            logger.warning(f"Could not get weather context: {str(e)}")
            return {}
    
    def _analyze_drying_conditions(self, rainfall_data) -> Dict[str, Any]:
        """Analyze weather conditions for crop drying."""
        monthly_avg = rainfall_data.monthly_averages
        
        # Find months with low rainfall (good for drying)
        drying_months = []
        for month, rainfall in monthly_avg.items():
            if rainfall < 50:  # Less than 50mm rainfall
                drying_months.append({
                    'month': month,
                    'rainfall': rainfall,
                    'suitability': 'excellent' if rainfall < 20 else 'good'
                })
        
        return {
            'optimal_drying_months': drying_months,
            'drying_risk_months': [m for m in monthly_avg.items() if m[1] > 100]
        }
    
    def _analyze_storage_risks(self, rainfall_data) -> Dict[str, Any]:
        """Analyze weather risks for storage."""
        monthly_avg = rainfall_data.monthly_averages
        
        # High humidity months (risk for storage)
        high_humidity_months = []
        for month, rainfall in monthly_avg.items():
            if rainfall > 150:  # High rainfall months
                high_humidity_months.append({
                    'month': month,
                    'rainfall': rainfall,
                    'risk_level': 'high' if rainfall > 200 else 'moderate'
                })
        
        return {
            'high_humidity_months': high_humidity_months,
            'storage_recommendations': self._get_storage_recommendations(high_humidity_months)
        }
    
    def _get_storage_recommendations(self, high_humidity_months: List[Dict]) -> List[str]:
        """Get storage recommendations based on high humidity months."""
        recommendations = []
        
        if high_humidity_months:
            recommendations.append("Use airtight containers during high humidity months")
            recommendations.append("Consider artificial drying before storage")
            recommendations.append("Monitor for mold and fungal growth")
        
        return recommendations
    
    def _search_harvest_knowledge(self, crop: str) -> Dict[str, List[Dict[str, Any]]]:
        """Search the knowledge base for harvest-related information."""
        harvest_knowledge = {}
        
        for category, search_terms in self.harvest_categories.items():
            category_results = []
            
            for term in search_terms:
                # Add crop-specific search
                crop_specific_term = f"{crop} {term}"
                
                # Search in vector database
                search_results = self.semantic_search.search_documents(
                    crop_specific_term, 
                    top_k=5,
                    threshold=0.6
                )
                
                if search_results:
                    category_results.extend(search_results)
                
                # Also search general harvest terms
                general_results = self.semantic_search.search_documents(
                    term,
                    top_k=3,
                    threshold=0.7
                )
                
                if general_results:
                    category_results.extend(general_results)
            
            # Remove duplicates and sort by relevance
            unique_results = self._deduplicate_results(category_results)
            harvest_knowledge[category] = unique_results[:8]  # Top 8 results per category
        
        return harvest_knowledge
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate search results based on text content."""
        seen_texts = set()
        unique_results = []
        
        for result in results:
            text = result.get('text', '').strip()
            if text and text not in seen_texts:
                seen_texts.add(text)
                unique_results.append(result)
        
        # Sort by relevance score
        unique_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        return unique_results
    
    def _get_harvest_timing(self, crop: str, knowledge: Dict[str, Any], 
                           weather_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get harvest timing recommendations."""
        timing_knowledge = knowledge.get('timing', [])
        
        # Extract timing information from knowledge base
        timing_info = []
        for result in timing_knowledge:
            text = result.get('text', '')
            # Look for timing patterns
            timing_patterns = [
                r'(\d+)\s*(days?|weeks?|months?)\s*(?:after|before|during)',
                r'harvest.*?(\d{1,2})\s*(?:weeks?|months?)',
                r'(\w+)\s*(?:season|month).*?harvest',
                r'harvest.*?(\w+)\s*(?:season|month)'
            ]
            
            for pattern in timing_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    timing_info.append({
                        'source': result.get('source_document', ''),
                        'text': text[:200] + '...' if len(text) > 200 else text,
                        'timing_matches': matches,
                        'relevance': result.get('score', 0)
                    })
                    break
        
        # Combine with weather context
        weather_timing = {}
        if weather_context.get('rainfall_patterns'):
            # Find optimal harvest months based on rainfall
            rainfall_patterns = weather_context['rainfall_patterns']
            optimal_months = []
            
            for month, rainfall in rainfall_patterns.items():
                if rainfall < 80:  # Low rainfall months good for harvest
                    optimal_months.append({
                        'month': month,
                        'rainfall': rainfall,
                        'reason': 'Low rainfall allows for proper drying'
                    })
            
            weather_timing = {
                'optimal_harvest_months': optimal_months,
                'avoid_months': [m for m in rainfall_patterns.items() if m[1] > 150]
            }
        
        return {
            'knowledge_based_timing': timing_info,
            'weather_based_timing': weather_timing,
            'recommendations': self._generate_timing_recommendations(timing_info, weather_timing)
        }
    
    def _get_drying_recommendations(self, crop: str, knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Get drying recommendations."""
        drying_knowledge = knowledge.get('drying', [])
        
        recommendations = {
            'methods': [],
            'moisture_targets': [],
            'duration_estimates': [],
            'weather_considerations': []
        }
        
        for result in drying_knowledge:
            text = result.get('text', '')
            
            # Extract drying methods
            if any(method in text.lower() for method in ['sun dry', 'artificial dry', 'mechanical dry']):
                recommendations['methods'].append({
                    'method': self._extract_drying_method(text),
                    'source': result.get('source_document', ''),
                    'description': text[:150] + '...' if len(text) > 150 else text
                })
            
            # Extract moisture content targets
            moisture_matches = re.findall(r'(\d+(?:\.\d+)?)\s*%?\s*moisture', text, re.IGNORECASE)
            if moisture_matches:
                recommendations['moisture_targets'].extend(moisture_matches)
            
            # Extract duration estimates
            duration_matches = re.findall(r'(\d+)\s*(days?|weeks?)\s*(?:to|for)\s*dry', text, re.IGNORECASE)
            if duration_matches:
                recommendations['duration_estimates'].extend(duration_matches)
        
        return recommendations
    
    def _get_storage_guidelines(self, crop: str, knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Get storage guidelines."""
        storage_knowledge = knowledge.get('storage', [])
        
        guidelines = {
            'storage_methods': [],
            'container_types': [],
            'environmental_conditions': [],
            'duration_limits': []
        }
        
        for result in storage_knowledge:
            text = result.get('text', '')
            
            # Extract storage methods
            if any(method in text.lower() for method in ['warehouse', 'silo', 'container', 'bag']):
                guidelines['storage_methods'].append({
                    'method': self._extract_storage_method(text),
                    'source': result.get('source_document', ''),
                    'description': text[:150] + '...' if len(text) > 150 else text
                })
            
            # Extract environmental conditions
            if any(condition in text.lower() for condition in ['temperature', 'humidity', 'ventilation']):
                guidelines['environmental_conditions'].append({
                    'condition': self._extract_environmental_condition(text),
                    'source': result.get('source_document', ''),
                    'description': text[:150] + '...' if len(text) > 150 else text
                })
        
        return guidelines
    
    def _get_loss_prevention(self, crop: str, knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Get post-harvest loss prevention strategies."""
        loss_knowledge = knowledge.get('loss_prevention', [])
        
        prevention_strategies = {
            'pest_control': [],
            'disease_prevention': [],
            'quality_maintenance': [],
            'handling_practices': []
        }
        
        for result in loss_knowledge:
            text = result.get('text', '')
            
            # Categorize prevention strategies
            if any(term in text.lower() for term in ['pest', 'insect', 'rodent']):
                prevention_strategies['pest_control'].append({
                    'strategy': self._extract_prevention_strategy(text, 'pest'),
                    'source': result.get('source_document', ''),
                    'description': text[:150] + '...' if len(text) > 150 else text
                })
            
            if any(term in text.lower() for term in ['disease', 'fungal', 'mold']):
                prevention_strategies['disease_prevention'].append({
                    'strategy': self._extract_prevention_strategy(text, 'disease'),
                    'source': result.get('source_document', ''),
                    'description': text[:150] + '...' if len(text) > 150 else text
                })
        
        return prevention_strategies
    
    def _get_processing_advice(self, crop: str, knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Get value addition and processing advice."""
        processing_knowledge = knowledge.get('processing', [])
        
        processing_advice = {
            'value_addition': [],
            'processing_methods': [],
            'market_preparation': []
        }
        
        for result in processing_knowledge:
            text = result.get('text', '')
            
            # Extract value addition opportunities
            if any(term in text.lower() for term in ['value addition', 'processing', 'grading']):
                processing_advice['value_addition'].append({
                    'opportunity': self._extract_processing_opportunity(text),
                    'source': result.get('source_document', ''),
                    'description': text[:150] + '...' if len(text) > 150 else text
                })
        
        return processing_advice
    
    def _get_quality_standards(self, crop: str, knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Get quality standards and grading information."""
        # Search specifically for quality standards
        quality_results = self.semantic_search.search_documents(
            f"{crop} quality standards grading",
            top_k=5,
            threshold=0.6
        )
        
        quality_standards = {
            'grading_criteria': [],
            'quality_parameters': [],
            'market_standards': []
        }
        
        for result in quality_results:
            text = result.get('text', '')
            
            # Extract grading criteria
            if any(term in text.lower() for term in ['grade', 'quality', 'standard']):
                quality_standards['grading_criteria'].append({
                    'criterion': self._extract_quality_criterion(text),
                    'source': result.get('source_document', ''),
                    'description': text[:150] + '...' if len(text) > 150 else text
                })
        
        return quality_standards
    
    def _extract_drying_method(self, text: str) -> str:
        """Extract drying method from text."""
        methods = ['sun drying', 'artificial drying', 'mechanical drying', 'natural drying']
        for method in methods:
            if method in text.lower():
                return method
        return 'drying method'
    
    def _extract_storage_method(self, text: str) -> str:
        """Extract storage method from text."""
        methods = ['warehouse storage', 'silo storage', 'container storage', 'bag storage']
        for method in methods:
            if method in text.lower():
                return method
        return 'storage method'
    
    def _extract_environmental_condition(self, text: str) -> str:
        """Extract environmental condition from text."""
        conditions = ['temperature control', 'humidity control', 'ventilation', 'air circulation']
        for condition in conditions:
            if condition in text.lower():
                return condition
        return 'environmental condition'
    
    def _extract_prevention_strategy(self, text: str, strategy_type: str) -> str:
        """Extract prevention strategy from text."""
        if strategy_type == 'pest':
            strategies = ['pest control', 'insect control', 'rodent control']
        else:
            strategies = ['disease prevention', 'fungal control', 'mold prevention']
        
        for strategy in strategies:
            if strategy in text.lower():
                return strategy
        return f'{strategy_type} prevention'
    
    def _extract_processing_opportunity(self, text: str) -> str:
        """Extract processing opportunity from text."""
        opportunities = ['value addition', 'processing', 'grading', 'packaging']
        for opportunity in opportunities:
            if opportunity in text.lower():
                return opportunity
        return 'processing opportunity'
    
    def _extract_quality_criterion(self, text: str) -> str:
        """Extract quality criterion from text."""
        criteria = ['size grading', 'color grading', 'moisture content', 'purity']
        for criterion in criteria:
            if criterion in text.lower():
                return criterion
        return 'quality criterion'
    
    def _generate_timing_recommendations(self, timing_info: List[Dict], 
                                       weather_timing: Dict) -> List[str]:
        """Generate timing recommendations from knowledge and weather data."""
        recommendations = []
        
        # Add knowledge-based recommendations
        if timing_info:
            recommendations.append("Based on agricultural best practices:")
            for info in timing_info[:3]:  # Top 3 recommendations
                recommendations.append(f"• {info['text'][:100]}...")
        
        # Add weather-based recommendations
        if weather_timing.get('optimal_harvest_months'):
            recommendations.append("\nBased on local weather patterns:")
            optimal_months = weather_timing['optimal_harvest_months'][:3]
            for month_info in optimal_months:
                recommendations.append(
                    f"• {month_info['month']}: {month_info['reason']} "
                    f"(rainfall: {month_info['rainfall']}mm)"
                )
        
        return recommendations
    
    def format_harvest_advice(self, advice: Dict[str, Any]) -> str:
        """Format harvest advice for user response with AI enhancements."""
        if 'error' in advice:
            return f"❌ {advice['error']}"
        
        crop = advice.get('crop', 'Unknown crop')
        location = advice.get('location', 'General')
        
        response = f"🌾 **Harvest & Post-Harvest Advice for {crop.title()}**\n"
        if location != 'General':
            response += f"📍 **Location**: {location}\n"
        
        # Add AI enhancement indicator
        if advice.get('ai_enhanced'):
            response += "🤖 **AI-Enhanced Analysis**\n"
        response += "\n"
        
        # AI Insights Section
        ai_insights = advice.get('ai_insights', {})
        if ai_insights and ai_insights.get('raw_response'):
            response += "🧠 **AI-Powered Insights**\n"
            raw_response = ai_insights.get('raw_response', '')
            # Extract key points from AI response
            lines = raw_response.split('\n')
            key_points = []
            for line in lines:
                line = line.strip()
                if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                    key_points.append(line)
            
            # Add top 3 AI insights
            for point in key_points[:3]:
                response += f"{point}\n"
            response += "\n"
        
        # Personalized Recommendations
        personalized_recs = advice.get('personalized_recommendations', [])
        if personalized_recs:
            response += "🎯 **Personalized Recommendations**\n"
            for i, rec in enumerate(personalized_recs, 1):
                response += f"{i}. {rec}\n"
            response += "\n"
        
        # Risk Assessment
        risk_assessment = advice.get('risk_assessment', {})
        if risk_assessment and risk_assessment.get('overall_risk_level'):
            overall_risk = risk_assessment.get('overall_risk_level', 'medium')
            risk_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}.get(overall_risk, '⚪')
            response += f"⚠️ **Risk Assessment**: {risk_emoji} {overall_risk.title()} Risk\n"
            
            # Add specific risk categories
            risk_categories = ['weather_risks', 'storage_risks', 'quality_risks', 'market_risks']
            for category in risk_categories:
                if category in risk_assessment:
                    risk_level = risk_assessment[category].get('level', 'medium')
                    risk_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}.get(risk_level, '⚪')
                    category_name = category.replace('_', ' ').title()
                    response += f"   • {category_name}: {risk_emoji} {risk_level.title()}\n"
            response += "\n"
        
        # Harvest Timing
        timing = advice.get('harvest_timing', {})
        if timing.get('recommendations'):
            response += "⏰ **Optimal Harvest Timing**\n"
            for rec in timing['recommendations'][:3]:
                response += f"• {rec}\n"
            response += "\n"
        
        # Drying Recommendations
        drying = advice.get('drying_recommendations', {})
        if drying.get('methods'):
            response += "☀️ **Drying Recommendations**\n"
            for method in drying['methods'][:2]:
                response += f"• {method['method'].title()}: {method['description'][:80]}...\n"
            response += "\n"
        
        # Storage Guidelines
        storage = advice.get('storage_guidelines', {})
        if storage.get('storage_methods'):
            response += "🏪 **Storage Guidelines**\n"
            for method in storage['storage_methods'][:2]:
                response += f"• {method['method'].title()}: {method['description'][:80]}...\n"
            response += "\n"
        
        # Loss Prevention
        loss_prevention = advice.get('loss_prevention', {})
        if loss_prevention.get('pest_control') or loss_prevention.get('disease_prevention'):
            response += "🛡️ **Loss Prevention Strategies**\n"
            for category, strategies in loss_prevention.items():
                if strategies:
                    response += f"• {category.replace('_', ' ').title()}: {strategies[0]['strategy']}\n"
            response += "\n"
        
        # Quality Standards
        quality = advice.get('quality_standards', {})
        if quality.get('grading_criteria'):
            response += "📊 **Quality Standards**\n"
            for criterion in quality['grading_criteria'][:2]:
                response += f"• {criterion['criterion'].title()}: {criterion['description'][:80]}...\n"
            response += "\n"
        
        # Add AI enhancement note
        if advice.get('ai_enhanced'):
            response += "💡 *Enhanced with AI-powered analysis for location-specific insights*"
        else:
            response += "💡 *Advice based on agricultural best practices and local weather patterns*"
        
        return response


async def main():
    """Test the AI-enhanced harvest advisor."""
    advisor = HarvestAdvisor()
    
    # Test with different crops
    test_crops = ['maize', 'beans', 'groundnuts']
    
    for crop in test_crops:
        print(f"\n{'='*50}")
        print(f"Testing AI-Enhanced Harvest Advisor for {crop}")
        print(f"{'='*50}")
        
        advice = await advisor.get_harvest_advice(crop, "-13.9833, 33.7833", "test_user_123")
        formatted_response = advisor.format_harvest_advice(advice)
        print(formatted_response)
        
        # Show AI enhancement status
        if advice.get('ai_enhanced'):
            print(f"\n✅ AI Enhancement: Successful")
            print(f"🤖 AI Insights: {len(advice.get('ai_insights', {}).get('raw_response', ''))} characters")
            print(f"🎯 Personalized Recommendations: {len(advice.get('personalized_recommendations', []))} items")
            print(f"⚠️ Risk Assessment: {advice.get('risk_assessment', {}).get('overall_risk_level', 'unknown')} risk")
        else:
            print(f"\n❌ AI Enhancement: Failed - {advice.get('ai_error', 'Unknown error')}")


if __name__ == "__main__":
    asyncio.run(main()) 