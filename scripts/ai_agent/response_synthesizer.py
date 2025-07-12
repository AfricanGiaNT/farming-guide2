"""
Response synthesizer for the Agricultural Advisor Bot.
Combines traditional crop recommendations with AI-generated insights.
"""
from typing import Dict, List, Any, Optional
from scripts.ai_agent.gpt_integration import gpt_integration
from scripts.ai_agent.prompt_formatter import prompt_formatter
from scripts.utils.logger import logger


class ResponseSynthesizer:
    """Combines traditional recommendations with AI insights."""
    
    def __init__(self):
        """Initialize the response synthesizer."""
        self.gpt = gpt_integration
        self.prompt_formatter = prompt_formatter
        self.enable_ai_enhancement = True
        
    async def synthesize_crop_recommendations(self, 
                                            recommendations: Dict[str, Any],
                                            weather_data: Dict[str, Any],
                                            location: str,
                                            user_id: str) -> str:
        """
        Synthesize comprehensive crop recommendations with AI enhancement.
        
        Args:
            recommendations: Base crop recommendations
            weather_data: Current weather data
            location: Location string
            user_id: User ID for logging
            
        Returns:
            Synthesized recommendation message
        """
        logger.info(f"Synthesizing crop recommendations for user {user_id}")
        
        try:
            # Get AI enhancement if enabled
            if self.enable_ai_enhancement:
                enhanced_recommendations = await self.gpt.enhance_crop_recommendations(
                    recommendations, weather_data, location, user_id
                )
            else:
                enhanced_recommendations = recommendations
            
            # Format the comprehensive response
            response = self._format_enhanced_response(
                enhanced_recommendations, weather_data, location, user_id
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error synthesizing recommendations: {e}", user_id)
            # Fallback to traditional formatting
            return self._format_basic_response(recommendations, weather_data, location)
    
    async def generate_actionable_summary(self, 
                                        crop_data: Dict[str, Any],
                                        weather_data: Dict[str, Any],
                                        user_id: str) -> List[str]:
        """
        Generate actionable summary points using AI.
        
        Args:
            crop_data: Crop recommendation data
            weather_data: Weather conditions
            user_id: User ID for logging
            
        Returns:
            List of actionable recommendations
        """
        try:
            if self.enable_ai_enhancement:
                advice_items = await self.gpt.generate_actionable_advice(
                    crop_data, weather_data, user_id
                )
            else:
                advice_items = self._generate_basic_advice(crop_data)
            
            return advice_items
            
        except Exception as e:
            logger.error(f"Error generating actionable summary: {e}", user_id)
            return self._generate_basic_advice(crop_data)
    
    def _format_enhanced_response(self, 
                                recommendations: Dict[str, Any],
                                weather_data: Dict[str, Any],
                                location: str,
                                user_id: str) -> str:
        """
        Format enhanced response with AI insights.
        
        Args:
            recommendations: Enhanced recommendations with AI insights
            weather_data: Weather data
            location: Location string
            user_id: User ID for logging
            
        Returns:
            Formatted response message
        """
        
        # Get base response structure
        base_response = self._format_basic_response(recommendations, weather_data, location)
        
        # Add AI insights if available
        ai_insights = recommendations.get('ai_insights', {})
        if ai_insights:
            enhanced_advice = ai_insights.get('enhanced_advice', '')
            
            # Insert AI insights into the response
            ai_section = f"\n🤖 **AI INSIGHTS:**\n{enhanced_advice}\n"
            
            # Find insertion point (before "NEXT STEPS" section)
            if "💡 **NEXT STEPS:**" in base_response:
                insertion_point = base_response.find("💡 **NEXT STEPS:**")
                enhanced_response = (
                    base_response[:insertion_point] + 
                    ai_section + 
                    base_response[insertion_point:]
                )
            else:
                enhanced_response = base_response + ai_section
        else:
            enhanced_response = base_response
        
        # Add risk assessment if available
        risk_assessment = recommendations.get('risk_assessment', {})
        if risk_assessment:
            risk_level = risk_assessment.get('risk_level', 'moderate')
            risk_factors = risk_assessment.get('risk_factors', [])
            
            risk_emoji = {'low': '🟢', 'moderate': '🟡', 'high': '🔴'}.get(risk_level, '🟡')
            
            risk_section = f"\n⚠️ **RISK ASSESSMENT:** {risk_emoji} {risk_level.title()}\n"
            if risk_factors:
                risk_section += f"• Key risks: {', '.join(risk_factors)}\n"
            
            enhanced_response += risk_section
        
        logger.info(f"Enhanced response generated for user {user_id}")
        return enhanced_response
    
    def _format_basic_response(self, 
                             recommendations: Dict[str, Any],
                             weather_data: Dict[str, Any],
                             location: str) -> str:
        """
        Format basic response without AI enhancement.
        
        Args:
            recommendations: Base recommendations
            weather_data: Weather data
            location: Location string
            
        Returns:
            Basic formatted response
        """
        
        # Get environmental summary
        env_summary = recommendations.get('environmental_summary', {})
        
        # Build basic response
        response = f"""🌾 **Crop Recommendations for {location}**

🌤️ **Current Conditions:**
• Temperature: {env_summary.get('current_temperature', 25):.1f}°C
• Recent rainfall: {env_summary.get('total_7day_rainfall', 0):.1f}mm
• Forecast: {env_summary.get('forecast_7day_rainfall', 0):.1f}mm (7 days)
• Season: {env_summary.get('current_season', 'unknown').replace('_', ' ').title()}

"""
        
        # Add top recommendations
        top_recommendations = recommendations.get('recommendations', [])[:3]
        if top_recommendations:
            response += "🏆 **Top Recommendations:**\n"
            
            for i, rec in enumerate(top_recommendations, 1):
                crop_data = rec.get('crop_data', {})
                suitability = rec.get('suitability_level', 'unknown')
                score = rec.get('total_score', 0)
                
                suitability_emoji = {
                    'excellent': '🟢',
                    'good': '🟡',
                    'fair': '🟠',
                    'poor': '🔴'
                }.get(suitability, '⚪')
                
                response += f"\n{i}. **{crop_data.get('name', 'Unknown')}** {suitability_emoji}\n"
                response += f"   Score: {score:.0f}/100 ({suitability})\n"
                
                # Add best variety if available
                varieties = rec.get('recommended_varieties', [])
                if varieties:
                    best_variety = varieties[0]['variety_data'].get('name', 'Unknown')
                    response += f"   Best variety: {best_variety}\n"
        
        # Add timing advice
        planting_calendar = recommendations.get('planting_calendar', [])
        if planting_calendar:
            response += "\n📅 **Planting Timing:**\n"
            for timing in planting_calendar[:2]:
                crop_name = timing.get('crop_name', 'Unknown')
                if timing.get('season_match'):
                    response += f"• {crop_name}: Optimal planting time now\n"
                else:
                    response += f"• {crop_name}: Prepare for upcoming season\n"
        
        # Add basic next steps
        response += "\n💡 **Next Steps:**\n"
        response += "• Monitor weather conditions\n"
        response += "• Prepare soil for planting\n"
        response += "• Ensure water management systems\n"
        
        return response
    
    def _generate_basic_advice(self, crop_data: Dict[str, Any]) -> List[str]:
        """
        Generate basic advice without AI enhancement.
        
        Args:
            crop_data: Crop recommendation data
            
        Returns:
            List of basic advice items
        """
        
        advice = []
        
        # Get top crop
        top_crops = crop_data.get('recommendations', [])
        if top_crops:
            top_crop = top_crops[0]
            crop_name = top_crop.get('crop_data', {}).get('name', 'crops')
            advice.append(f"Focus on {crop_name} cultivation this season")
        
        # Add environmental advice
        env_summary = crop_data.get('environmental_summary', {})
        rainfall = env_summary.get('total_7day_rainfall', 0)
        
        if rainfall > 50:
            advice.append("Take advantage of good rainfall conditions")
        elif rainfall < 10:
            advice.append("Implement water conservation measures")
        
        # Add seasonal advice
        season = env_summary.get('current_season', 'unknown')
        if season == 'rainy_season':
            advice.append("Prepare for main planting season")
        elif season == 'dry_season':
            advice.append("Focus on drought-resistant varieties")
        
        # Add general advice
        advice.extend([
            "Monitor weather forecasts regularly",
            "Ensure proper soil preparation",
            "Plan irrigation systems if needed"
        ])
        
        return advice[:5]  # Limit to 5 items
    
    def format_weather_impact_response(self, 
                                     weather_data: Dict[str, Any],
                                     crop_name: str,
                                     location: str) -> str:
        """
        Format weather impact response for a specific crop.
        
        Args:
            weather_data: Current weather conditions
            crop_name: Name of the crop
            location: Location string
            
        Returns:
            Weather impact response
        """
        
        temp = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 50)
        rainfall = weather_data.get('rainfall', 0)
        
        response = f"""🌦️ **Weather Impact on {crop_name}** ({location})

**Current Conditions:**
• Temperature: {temp}°C
• Humidity: {humidity}%
• Recent rainfall: {rainfall}mm

**Impact Assessment:**
"""
        
        # Temperature impact
        if temp > 35:
            response += "• 🔥 High temperature stress - provide shade/irrigation\n"
        elif temp < 15:
            response += "• 🧊 Cool temperatures - monitor for growth delays\n"
        else:
            response += "• 🌡️ Temperature conditions favorable\n"
        
        # Rainfall impact
        if rainfall > 100:
            response += "• 💧 Excessive rainfall - ensure proper drainage\n"
        elif rainfall < 5:
            response += "• 🌵 Low rainfall - increase irrigation frequency\n"
        else:
            response += "• 💧 Adequate rainfall conditions\n"
        
        # Add recommendations
        response += "\n**Immediate Actions:**\n"
        response += "• Monitor crop health daily\n"
        response += "• Adjust irrigation schedule\n"
        response += "• Prepare for weather changes\n"
        
        return response
    
    def set_ai_enhancement(self, enabled: bool):
        """
        Enable or disable AI enhancement.
        
        Args:
            enabled: Whether to enable AI enhancement
        """
        self.enable_ai_enhancement = enabled
        logger.info(f"AI enhancement {'enabled' if enabled else 'disabled'}")
    
    def get_synthesis_stats(self) -> Dict[str, Any]:
        """
        Get synthesis statistics.
        
        Returns:
            Statistics about response synthesis
        """
        return {
            'ai_enhancement_enabled': self.enable_ai_enhancement,
            'cache_size': len(self.gpt.response_cache),
            'total_syntheses': 0  # Would track this in production
        }


# Global instance
response_synthesizer = ResponseSynthesizer() 