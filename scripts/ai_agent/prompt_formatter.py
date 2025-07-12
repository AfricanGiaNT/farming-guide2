"""
Prompt formatter for the Agricultural Advisor Bot.
Provides cost-optimized prompts for different agricultural scenarios.
"""
from typing import Dict, List, Any, Optional
from scripts.utils.logger import logger


class PromptFormatter:
    """Cost-optimized prompt formatter for agricultural AI queries."""
    
    def __init__(self):
        """Initialize the prompt formatter."""
        self.system_prompt = (
            "You are a practical agricultural advisor specializing in Malawi farming. "
            "Provide concise, actionable advice focused on local conditions and resources."
        )
        
        self.max_prompt_length = 800  # Token optimization
        self.response_length = 200    # Response optimization
    
    def format_crop_analysis_prompt(self, 
                                  crop_data: Dict[str, Any],
                                  weather_data: Dict[str, Any],
                                  location: str) -> str:
        """
        Format prompt for crop analysis and recommendations.
        
        Args:
            crop_data: Crop recommendation data
            weather_data: Weather conditions
            location: Location string
            
        Returns:
            Formatted prompt for AI analysis
        """
        
        # Extract key information
        top_crops = crop_data.get('recommendations', [])[:3]
        env_summary = crop_data.get('environmental_summary', {})
        
        prompt = f"""Analyze crop recommendations for {location}:

CONDITIONS:
- Rainfall: {env_summary.get('total_7day_rainfall', 0)}mm (7-day)
- Temperature: {env_summary.get('current_temperature', 25)}°C
- Season: {env_summary.get('current_season', 'unknown')}

RECOMMENDED CROPS:
"""
        
        for i, crop in enumerate(top_crops, 1):
            crop_name = crop.get('crop_data', {}).get('name', 'Unknown')
            score = crop.get('total_score', 0)
            suitability = crop.get('suitability_level', 'unknown')
            prompt += f"{i}. {crop_name} ({suitability}, {score}/100)\n"
        
        prompt += f"""
Provide in {self.response_length} words:
1. Risk assessment (weather, pest, market)
2. Timing recommendations (planting/harvesting)
3. Specific tips for current conditions

Focus on actionable advice farmers can implement immediately."""
        
        return self._optimize_prompt_length(prompt)
    
    def format_weather_impact_prompt(self, 
                                   weather_data: Dict[str, Any],
                                   crop_name: str,
                                   location: str) -> str:
        """
        Format prompt for weather impact analysis on specific crops.
        
        Args:
            weather_data: Current weather conditions
            crop_name: Name of the crop
            location: Location string
            
        Returns:
            Formatted prompt for weather impact analysis
        """
        
        temp = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 50)
        rainfall = weather_data.get('rainfall', 0)
        
        prompt = f"""Weather impact on {crop_name} in {location}:

CURRENT CONDITIONS:
- Temperature: {temp}°C
- Humidity: {humidity}%
- Recent rainfall: {rainfall}mm

Provide specific guidance:
1. How current weather affects {crop_name}
2. Immediate actions needed (this week)
3. Preparations for next 2 weeks

Keep response under {self.response_length} words, focus on practical steps."""
        
        return self._optimize_prompt_length(prompt)
    
    def format_seasonal_advice_prompt(self, 
                                    season: str,
                                    location: str,
                                    crop_preferences: List[str] = None) -> str:
        """
        Format prompt for seasonal farming advice.
        
        Args:
            season: Current season
            location: Location string
            crop_preferences: Optional list of preferred crops
            
        Returns:
            Formatted prompt for seasonal advice
        """
        
        crop_focus = ""
        if crop_preferences:
            crop_focus = f"Focus on: {', '.join(crop_preferences[:3])}"
        
        prompt = f"""Seasonal farming advice for {season} in {location}:

{crop_focus}

Provide:
1. Priority activities for this season
2. Crops to plant/harvest now
3. Preparation for next season

Maximum {self.response_length} words. Give specific, actionable steps."""
        
        return self._optimize_prompt_length(prompt)
    
    def format_problem_solving_prompt(self, 
                                    problem_description: str,
                                    crop_context: str,
                                    location: str) -> str:
        """
        Format prompt for agricultural problem solving.
        
        Args:
            problem_description: Description of the farming problem
            crop_context: Crop-related context
            location: Location string
            
        Returns:
            Formatted prompt for problem solving
        """
        
        prompt = f"""Agricultural problem in {location}:

PROBLEM: {problem_description}
CROP CONTEXT: {crop_context}

Provide:
1. Root cause analysis
2. Immediate solutions
3. Prevention strategies

Keep response practical and under {self.response_length} words."""
        
        return self._optimize_prompt_length(prompt)
    
    def format_variety_selection_prompt(self, 
                                      crop_name: str,
                                      varieties: List[Dict[str, Any]],
                                      conditions: Dict[str, Any]) -> str:
        """
        Format prompt for crop variety selection advice.
        
        Args:
            crop_name: Name of the crop
            varieties: List of available varieties
            conditions: Current growing conditions
            
        Returns:
            Formatted prompt for variety selection
        """
        
        varieties_text = []
        for variety in varieties[:3]:  # Limit to top 3
            name = variety.get('name', 'Unknown')
            tolerance = variety.get('drought_tolerance', 'moderate')
            maturity = variety.get('maturity_days', 'unknown')
            varieties_text.append(f"{name} (drought: {tolerance}, maturity: {maturity} days)")
        
        prompt = f"""Select best {crop_name} variety:

AVAILABLE VARIETIES:
{chr(10).join(varieties_text)}

CONDITIONS:
- Rainfall: {conditions.get('rainfall', 0)}mm
- Temperature: {conditions.get('temperature', 25)}°C

Recommend the best variety with reasons. Maximum {self.response_length} words."""
        
        return self._optimize_prompt_length(prompt)
    
    def format_market_timing_prompt(self, 
                                  crop_name: str,
                                  harvest_timeline: str,
                                  location: str) -> str:
        """
        Format prompt for market timing advice.
        
        Args:
            crop_name: Name of the crop
            harvest_timeline: Expected harvest timeline
            location: Location string
            
        Returns:
            Formatted prompt for market timing
        """
        
        prompt = f"""Market timing for {crop_name} in {location}:

HARVEST TIMELINE: {harvest_timeline}

Provide:
1. Optimal selling periods
2. Market preparation steps
3. Price optimization strategies

Focus on practical market access. Maximum {self.response_length} words."""
        
        return self._optimize_prompt_length(prompt)
    
    def format_emergency_response_prompt(self, 
                                       emergency_type: str,
                                       crop_affected: str,
                                       severity: str) -> str:
        """
        Format prompt for emergency agricultural situations.
        
        Args:
            emergency_type: Type of emergency (drought, flood, pest, etc.)
            crop_affected: Affected crop
            severity: Severity level
            
        Returns:
            Formatted emergency response prompt
        """
        
        prompt = f"""EMERGENCY: {emergency_type} affecting {crop_affected}

SEVERITY: {severity}

Provide immediate response:
1. Urgent actions (next 24-48 hours)
2. Damage mitigation steps
3. Recovery planning

Maximum {self.response_length} words. Focus on emergency actions."""
        
        return self._optimize_prompt_length(prompt)
    
    def _optimize_prompt_length(self, prompt: str) -> str:
        """
        Optimize prompt length for cost efficiency.
        
        Args:
            prompt: Original prompt
            
        Returns:
            Optimized prompt
        """
        if len(prompt) <= self.max_prompt_length:
            return prompt
        
        # Truncate while preserving structure
        lines = prompt.split('\n')
        optimized_lines = []
        current_length = 0
        
        for line in lines:
            if current_length + len(line) > self.max_prompt_length:
                break
            optimized_lines.append(line)
            current_length += len(line)
        
        optimized_prompt = '\n'.join(optimized_lines)
        logger.info(f"Prompt optimized: {len(prompt)} -> {len(optimized_prompt)} chars")
        
        return optimized_prompt
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for AI interactions."""
        return self.system_prompt
    
    def get_max_response_length(self) -> int:
        """Get maximum response length setting."""
        return self.response_length
    
    def validate_prompt(self, prompt: str) -> bool:
        """
        Validate prompt for cost optimization.
        
        Args:
            prompt: Prompt to validate
            
        Returns:
            True if prompt is optimized
        """
        return len(prompt) <= self.max_prompt_length


# Global instance
prompt_formatter = PromptFormatter() 