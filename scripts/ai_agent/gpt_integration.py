"""
GPT-3.5-turbo integration for the Agricultural Advisor Bot.
Provides cost-optimized AI responses for crop recommendations.
"""
from openai import OpenAI
import json
import asyncio
from typing import Dict, List, Any, Optional
from scripts.utils.config_loader import config
from scripts.utils.logger import logger
from scripts.data_pipeline.semantic_search import SemanticSearch


class GPTIntegration:
    """Cost-optimized GPT-3.5-turbo integration for agricultural advice."""
    
    def __init__(self):
        """Initialize the GPT integration."""
        self.client = None
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 500  # Cost optimization
        self.temperature = 0.7
        self.response_cache = {}  # Simple in-memory cache
        
        # Initialize PDF knowledge search
        self.pdf_search = None
        self._initialize_pdf_search()
        
        # Initialize OpenAI client
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client with API key."""
        try:
            api_key = config.get_required("OPENAI_API_KEY")
            self.client = OpenAI(api_key=api_key)
            logger.info("OpenAI GPT-3.5-turbo client initialized successfully")
        except ValueError as e:
            logger.error(f"OpenAI API key not found: {e}")
            raise
    
    def _initialize_pdf_search(self):
        """Initialize PDF semantic search system."""
        try:
            self.pdf_search = SemanticSearch()
            logger.info("PDF semantic search initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PDF search: {e}")
            self.pdf_search = None
    
    async def enhance_crop_recommendations(self, 
                                         recommendations: Dict[str, Any],
                                         weather_data: Dict[str, Any],
                                         location: str,
                                         user_id: str) -> Dict[str, Any]:
        """
        Enhance crop recommendations with AI-generated insights and PDF knowledge.
        
        Args:
            recommendations: Raw crop recommendations
            weather_data: Current weather data
            location: Location string
            user_id: User ID for logging
            
        Returns:
            Enhanced recommendations with AI insights and PDF knowledge
        """
        logger.info(f"Enhancing crop recommendations with AI and PDF knowledge for user {user_id}")
        
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(recommendations, weather_data, location)
            
            # Check cache first (cost optimization)
            if cache_key in self.response_cache:
                logger.info(f"Using cached AI response for user {user_id}")
                return self.response_cache[cache_key]
            
            # Search PDF knowledge for relevant information
            pdf_context = await self._get_pdf_context(recommendations, location, user_id)
            
            # Prepare prompt for GPT-3.5-turbo with PDF context
            prompt = self._create_enhanced_prompt(recommendations, weather_data, location, pdf_context)
            
            # Get AI response
            ai_response = await self._get_ai_response(prompt, user_id)
            
            # Parse and integrate AI insights
            enhanced_recommendations = self._integrate_ai_insights(
                recommendations, ai_response, user_id
            )
            
            # Add PDF knowledge metadata
            if pdf_context:
                enhanced_recommendations['pdf_knowledge_used'] = True
                enhanced_recommendations['pdf_sources'] = [
                    result.get('source_document', 'unknown') 
                    for result in pdf_context
                ]
            else:
                enhanced_recommendations['pdf_knowledge_used'] = False
            
            # Cache the response
            self.response_cache[cache_key] = enhanced_recommendations
            
            return enhanced_recommendations
            
        except Exception as e:
            logger.error(f"Error enhancing recommendations with AI: {e}", user_id)
            # Return original recommendations as fallback
            return recommendations
    
    async def _get_pdf_context(self, recommendations: Dict[str, Any], location: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Get relevant PDF context for crop recommendations.
        
        Args:
            recommendations: Crop recommendations
            location: Location string
            user_id: User ID for logging
            
        Returns:
            List of relevant PDF chunks
        """
        if not self.pdf_search:
            logger.warning("PDF search not available")
            return []
        
        try:
            # Extract top crop names for PDF search
            top_crops = recommendations.get('recommendations', [])[:2]
            if not top_crops:
                return []
            
            # Create search queries for PDF knowledge
            search_queries = []
            for crop_rec in top_crops:
                crop_name = crop_rec.get('crop_data', {}).get('name', '')
                if crop_name:
                    search_queries.append(f"{crop_name} cultivation {location}")
                    search_queries.append(f"{crop_name} farming practices")
            
            # Search PDF knowledge
            all_pdf_results = []
            for query in search_queries[:3]:  # Limit to 3 queries for cost control
                try:
                    results = self.pdf_search.search_documents(
                        query=query,
                        top_k=2,
                        threshold=0.75
                    )
                    all_pdf_results.extend(results)
                except Exception as e:
                    logger.warning(f"PDF search failed for query '{query}': {e}")
                    continue
            
            # Remove duplicates and limit results
            unique_results = []
            seen_texts = set()
            for result in all_pdf_results:
                text = result.get('text', '')
                if text not in seen_texts:
                    unique_results.append(result)
                    seen_texts.add(text)
                    if len(unique_results) >= 3:  # Limit to 3 unique results
                        break
            
            logger.info(f"Found {len(unique_results)} relevant PDF knowledge chunks for user {user_id}")
            return unique_results
            
        except Exception as e:
            logger.error(f"Error getting PDF context: {e}")
            return []
    
    def _create_enhanced_prompt(self, 
                              recommendations: Dict[str, Any],
                              weather_data: Dict[str, Any],
                              location: str,
                              pdf_context: List[Dict[str, Any]]) -> str:
        """Create enhanced prompt with PDF knowledge context."""
        
        # Extract key data points
        top_crops = recommendations.get('recommendations', [])[:3]
        env_summary = recommendations.get('environmental_summary', {})
        
        # Start with basic prompt
        prompt = f"""As an agricultural advisor for {location}, enhance these crop recommendations with practical insights:

CURRENT CONDITIONS:
- Rainfall: {env_summary.get('total_7day_rainfall', 0)}mm (7 days)
- Temperature: {env_summary.get('current_temperature', 25)}°C
- Season: {env_summary.get('current_season', 'unknown')}

TOP CROPS:
"""
        
        for i, crop in enumerate(top_crops, 1):
            crop_name = crop.get('crop_data', {}).get('name', 'Unknown')
            score = crop.get('total_score', 0)
            prompt += f"{i}. {crop_name} (Score: {score}/100)\n"
        
        # Add PDF knowledge context if available
        if pdf_context:
            prompt += "\nRELEVANT AGRICULTURAL KNOWLEDGE:\n"
            for i, context in enumerate(pdf_context, 1):
                text_preview = context.get('text_preview', context.get('text', ''))[:200]
                source = context.get('source_document', 'Agricultural Guide')
                prompt += f"{i}. From {source}: {text_preview}...\n"
        
        prompt += """
Based on current conditions and available knowledge, provide:
1. Risk assessment (drought, pest, market)
2. Timing recommendations (when to plant/harvest)
3. Specific farming tips for current conditions

Keep response under 200 words, focus on actionable advice."""
        
        return prompt

    async def generate_actionable_advice(self, 
                                       crop_data: Dict[str, Any],
                                       weather_conditions: Dict[str, Any],
                                       user_id: str) -> List[str]:
        """
        Generate specific, actionable advice for the user.
        
        Args:
            crop_data: Crop recommendation data
            weather_conditions: Current weather conditions
            user_id: User ID for logging
            
        Returns:
            List of actionable advice items
        """
        try:
            # Create focused prompt for actionable advice
            prompt = self._create_advice_prompt(crop_data, weather_conditions)
            
            # Get AI response
            ai_response = await self._get_ai_response(prompt, user_id)
            
            # Parse advice items
            advice_items = self._parse_advice_response(ai_response)
            
            return advice_items
            
        except Exception as e:
            logger.error(f"Error generating actionable advice: {e}", user_id)
            return self._get_fallback_advice(crop_data)
    
    def _create_advice_prompt(self, 
                            crop_data: Dict[str, Any],
                            weather_conditions: Dict[str, Any]) -> str:
        """Create focused prompt for actionable advice."""
        
        crop_name = crop_data.get('crop_data', {}).get('name', 'Unknown')
        current_temp = weather_conditions.get('temperature', 25)
        humidity = weather_conditions.get('humidity', 50)
        
        prompt = f"""For {crop_name} cultivation in current conditions (temp: {current_temp}°C, humidity: {humidity}%):

Give 3 specific, actionable steps a farmer should take this week:

1. [Immediate action needed]
2. [Preparation for next phase]
3. [Monitoring/maintenance task]

Each step should be:
- Specific and measurable
- Relevant to current weather
- Achievable with basic resources

Format as bullet points, max 20 words each."""
        
        return prompt
    
    async def _get_ai_response(self, prompt: str, user_id: str) -> str:
        """
        Get response from GPT-3.5-turbo with error handling.
        
        Args:
            prompt: The prompt to send
            user_id: User ID for logging
            
        Returns:
            AI response text
        """
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a practical agricultural advisor specializing in Malawi farming. Give concise, actionable advice."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
            )
            
            ai_text = response.choices[0].message.content.strip()
            logger.info(f"AI response generated successfully for user {user_id}")
            return ai_text
            
        except Exception as e:
            logger.error(f"Error getting AI response: {e}", user_id)
            raise
    
    def _integrate_ai_insights(self, 
                             recommendations: Dict[str, Any],
                             ai_response: str,
                             user_id: str) -> Dict[str, Any]:
        """
        Integrate AI insights into the recommendations structure.
        
        Args:
            recommendations: Original recommendations
            ai_response: AI-generated insights
            user_id: User ID for logging
            
        Returns:
            Enhanced recommendations with AI insights
        """
        enhanced = recommendations.copy()
        
        # Add AI insights section
        enhanced['ai_insights'] = {
            'enhanced_advice': ai_response,
            'generation_timestamp': logger.get_timestamp(),
            'confidence_level': 'high'
        }
        
        # Parse AI response for specific enhancements
        if 'risk' in ai_response.lower():
            enhanced['risk_assessment'] = self._extract_risk_info(ai_response)
        
        if 'timing' in ai_response.lower():
            enhanced['timing_advice'] = self._extract_timing_info(ai_response)
        
        logger.info(f"AI insights integrated for user {user_id}")
        return enhanced
    
    def _extract_risk_info(self, ai_response: str) -> Dict[str, Any]:
        """Extract risk assessment information from AI response."""
        return {
            'risk_level': 'moderate',  # Default
            'risk_factors': ['weather_dependent'],
            'mitigation_strategies': ['monitor_conditions']
        }
    
    def _extract_timing_info(self, ai_response: str) -> Dict[str, Any]:
        """Extract timing information from AI response."""
        return {
            'optimal_planting_window': 'current_season',
            'harvest_timeline': 'seasonal',
            'critical_periods': ['planting', 'flowering']
        }
    
    def _parse_advice_response(self, ai_response: str) -> List[str]:
        """Parse AI response into actionable advice items."""
        advice_items = []
        
        # Split by bullet points or numbered lists
        lines = ai_response.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('•') or line.startswith('-') or 
                        line.startswith('1.') or line.startswith('2.') or line.startswith('3.')):
                # Clean up the line
                cleaned = line.lstrip('•-123. ').strip()
                if cleaned:
                    advice_items.append(cleaned)
        
        return advice_items[:5]  # Limit to 5 items max
    
    def _get_fallback_advice(self, crop_data: Dict[str, Any]) -> List[str]:
        """Provide fallback advice when AI fails."""
        crop_name = crop_data.get('crop_data', {}).get('name', 'crops')
        
        return [
            f"Monitor weather conditions for {crop_name} cultivation",
            "Prepare soil according to crop requirements",
            "Ensure proper water management system"
        ]
    
    def _generate_cache_key(self, 
                          recommendations: Dict[str, Any],
                          weather_data: Dict[str, Any],
                          location: str) -> str:
        """Generate cache key for response caching."""
        # Create hash based on key parameters
        key_data = {
            'location': location,
            'temperature': weather_data.get('temperature', 25),
            'rainfall': recommendations.get('environmental_summary', {}).get('total_7day_rainfall', 0),
            'top_crop': recommendations.get('recommendations', [{}])[0].get('crop_data', {}).get('name', 'none')
        }
        
        return str(hash(json.dumps(key_data, sort_keys=True)))
    
    def clear_cache(self):
        """Clear the response cache."""
        self.response_cache.clear()
        logger.info("AI response cache cleared")


# Global instance
gpt_integration = GPTIntegration() 