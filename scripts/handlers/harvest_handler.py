#!/usr/bin/env python3
"""
Harvest Command Handler - Phase 6
Telegram command handler for harvest and post-harvest advice
Enhanced with AI-powered insights and personalized recommendations
"""

import re
import asyncio
from typing import Dict, Any, Optional
from scripts.handlers.harvest_advisor import HarvestAdvisor
from scripts.utils.logger import logger


class HarvestHandler:
    """
    Telegram command handler for harvest advice
    Enhanced with AI-powered insights
    """
    
    def __init__(self):
        """Initialize the harvest handler."""
        self.harvest_advisor = HarvestAdvisor()
        logger.info("HarvestHandler initialized with AI enhancement")
    
    async def handle_harvest_command(self, message_text: str, user_id: Optional[str] = None) -> str:
        """
        Handle /harvest command with crop and optional location.
        Enhanced with AI-powered insights and personalized recommendations.
        
        Args:
            message_text: Full message text (e.g., "/harvest maize -13.9833, 33.7833")
            user_id: User identifier for personalization
            
        Returns:
            Formatted harvest advice response with AI enhancements
        """
        try:
            # Parse command and arguments
            parts = message_text.strip().split()
            
            if len(parts) < 2:
                return self._get_usage_help()
            
            crop = parts[1].lower()
            
            # Extract location if provided
            location = None
            if len(parts) > 2:
                # Join remaining parts as location
                location = ' '.join(parts[2:])
                
                # Clean up location string
                location = location.strip()
                if not location:
                    location = None
            
            # Validate crop
            if not self._is_valid_crop(crop):
                return self._get_invalid_crop_message(crop)
            
            # Get AI-enhanced harvest advice
            logger.info(f"Processing AI-enhanced harvest command for {crop} at {location}")
            advice = await self.harvest_advisor.get_harvest_advice(crop, location, user_id)
            
            # Format response with AI enhancements
            response = self.harvest_advisor.format_harvest_advice(advice)
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling harvest command: {str(e)}")
            return f"❌ Sorry, I encountered an error while processing your harvest request. Please try again."
    
    def handle_harvest_command_sync(self, message_text: str, user_id: Optional[str] = None) -> str:
        """
        Synchronous wrapper for harvest command handling.
        
        Args:
            message_text: Full message text
            user_id: User identifier for personalization
            
        Returns:
            Formatted harvest advice response
        """
        try:
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    self.handle_harvest_command(message_text, user_id)
                )
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error in sync harvest handler: {str(e)}")
            return f"❌ Sorry, I encountered an error while processing your harvest request. Please try again."
    
    def _is_valid_crop(self, crop: str) -> bool:
        """Check if the crop is supported."""
        valid_crops = [
            'maize', 'corn', 'beans', 'groundnuts', 'peanuts', 'soybeans', 'sorghum',
            'millet', 'rice', 'wheat', 'cassava', 'sweet potato', 'potato', 'tomato',
            'onion', 'cabbage', 'lettuce', 'carrot', 'pepper', 'chili', 'eggplant',
            'cucumber', 'pumpkin', 'watermelon', 'melon', 'banana', 'mango', 'papaya'
        ]
        
        return crop.lower() in valid_crops
    
    def _get_invalid_crop_message(self, crop: str) -> str:
        """Get message for invalid crop."""
        return f"""❌ **Invalid Crop: {crop.title()}**

I don't have harvest advice for {crop.title()}. 

**Supported Crops:**
🌾 **Grains**: maize, rice, wheat, sorghum, millet
🫘 **Legumes**: beans, groundnuts, soybeans
🥔 **Root Crops**: cassava, sweet potato, potato
🥬 **Vegetables**: tomato, onion, cabbage, lettuce, carrot
🌶️ **Fruits**: banana, mango, papaya, watermelon

**Usage:**
`/harvest maize` - General harvest advice for maize
`/harvest beans -13.9833, 33.7833` - Location-specific advice"""
    
    def _get_usage_help(self) -> str:
        """Get usage help message."""
        return """🌾 **Harvest & Post-Harvest Advice**

Get comprehensive harvest timing, drying, storage, and loss prevention advice for your crops.

**Usage:**
`/harvest <crop>` - General harvest advice
`/harvest <crop> <location>` - Location-specific advice

**Examples:**
`/harvest maize` - Harvest advice for maize
`/harvest beans -13.9833, 33.7833` - Location-specific bean harvest advice
`/harvest groundnuts Lilongwe` - Named location advice

**What You'll Get:**
⏰ **Optimal Harvest Timing** - When to harvest based on weather patterns
☀️ **Drying Recommendations** - Best drying methods and conditions
🏪 **Storage Guidelines** - How to store crops properly
🛡️ **Loss Prevention** - Strategies to prevent post-harvest losses
📊 **Quality Standards** - Grading and quality requirements

**Supported Crops:**
🌾 Grains: maize, rice, wheat, sorghum, millet
🫘 Legumes: beans, groundnuts, soybeans
🥔 Root Crops: cassava, sweet potato, potato
🥬 Vegetables: tomato, onion, cabbage, lettuce, carrot
🌶️ Fruits: banana, mango, papaya, watermelon"""
    
    def get_available_crops(self) -> str:
        """Get list of available crops for harvest advice."""
        crops_by_category = {
            "🌾 Grains": ["maize", "rice", "wheat", "sorghum", "millet"],
            "🫘 Legumes": ["beans", "groundnuts", "soybeans"],
            "🥔 Root Crops": ["cassava", "sweet potato", "potato"],
            "🥬 Vegetables": ["tomato", "onion", "cabbage", "lettuce", "carrot", "pepper", "chili", "eggplant", "cucumber"],
            "🌶️ Fruits": ["banana", "mango", "papaya", "watermelon", "melon", "pumpkin"]
        }
        
        response = "🌾 **Available Crops for Harvest Advice**\n\n"
        
        for category, crops in crops_by_category.items():
            response += f"**{category}:**\n"
            for crop in crops:
                response += f"• {crop.title()}\n"
            response += "\n"
        
        response += "**Usage:** `/harvest <crop> [location]`"
        
        return response


def main():
    """Test the harvest handler."""
    handler = HarvestHandler()
    
    # Test cases
    test_cases = [
        "/harvest maize",
        "/harvest beans -13.9833, 33.7833",
        "/harvest groundnuts Lilongwe",
        "/harvest invalid_crop",
        "/harvest"
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"Testing: {test_case}")
        print(f"{'='*60}")
        
        response = handler.handle_harvest_command_sync(test_case)
        print(response)


if __name__ == "__main__":
    main() 