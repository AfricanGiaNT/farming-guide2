"""
Historical Rainfall Handler for the Agricultural Advisor Bot.
Handles commands for historical rainfall analysis and comparison.
"""

from telegram import Update
from telegram.ext import ContextTypes
from typing import Optional
import re
import datetime
from scripts.weather_engine.enhanced_rainfall_analyzer import enhanced_rainfall_analyzer
from scripts.weather_engine.coordinate_handler import coordinate_handler
from scripts.utils.logger import logger


class HistoricalRainHandler:
    """Handler for historical rainfall analysis commands."""
    
    def __init__(self):
        """Initialize historical rain handler."""
        self.analyzer = enhanced_rainfall_analyzer
        self.coord_handler = coordinate_handler
        logger.info("Historical rain handler initialized")
    
    async def handle_rain_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /rain_history command for historical rainfall analysis.
        
        Usage:
        /rain_history <coordinates> [years]
        /rain_history Lilongwe 5
        /rain_history -13.9833, 33.7833 3
        """
        user_id = update.effective_user.id
        try:
            # Parse arguments
            if not context.args:
                await self._send_rain_history_help(update)
                return
            
            # Extract coordinates and optional years parameter
            args_text = ' '.join(context.args)
            coordinates, years = self._parse_rain_history_args(args_text)
            
            if not coordinates:
                await update.message.reply_text(
                    "❌ Could not parse coordinates. Please provide valid coordinates.\n\n"
                    "Examples:\n"
                    "• `/rain_history Lilongwe 5`\n"
                    "• `/rain_history -13.9833, 33.7833 3`\n"
                    "• `/rain_history Area 1 7`",
                    parse_mode='Markdown'
                )
                return
            
            lat, lon = coordinates
            
            # Send processing message
            processing_msg = await update.message.reply_text(
                f"🔄 Analyzing {years} years of historical rainfall data for {lat:.3f}, {lon:.3f}...\n"
                "This may take a few moments."
            )
            
            # Get historical rainfall data
            historical_data = self.analyzer.historical_api.get_historical_rainfall(
                lat, lon, years, str(user_id)
            )
            
            if not historical_data:
                await processing_msg.edit_text(
                    "❌ Unable to fetch historical rainfall data for this location.\n"
                    "This could be due to:\n"
                    "• Remote location with limited data\n"
                    "• API service temporarily unavailable\n"
                    "• Invalid coordinates\n\n"
                    "Please try again later or check your coordinates."
                )
                return
            
            # Format and send historical analysis
            response = self._format_historical_rainfall_response(historical_data, lat, lon, years)
            await processing_msg.edit_text(response, parse_mode='Markdown')
            
            logger.info(f"Historical rainfall analysis provided to user {user_id}", str(user_id))
            
        except Exception as e:
            logger.error(f"Error in rain_history command: {e}", str(user_id))
            await update.message.reply_text(
                "❌ Sorry, there was an error analyzing historical rainfall data. Please try again later."
            )
    
    async def handle_rain_compare(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /rain_compare command for comparing current with historical rainfall.
        
        Usage:
        /rain_compare <coordinates> <current_rainfall> [years]
        /rain_compare Lilongwe 25 5
        /rain_compare -13.9833, 33.7833 15.5 3
        """
        user_id = update.effective_user.id
        try:
            if len(context.args) < 2:
                await self._send_rain_compare_help(update)
                return
            
            # Parse arguments
            args_text = ' '.join(context.args)
            coordinates, current_rainfall, years = self._parse_rain_compare_args(args_text)
            
            if not coordinates:
                await update.message.reply_text(
                    "❌ Could not parse coordinates and rainfall amount.\n\n"
                    "Examples:\n"
                    "• `/rain_compare Lilongwe 25 5`\n"
                    "• `/rain_compare -13.9833, 33.7833 15.5`\n"
                    "• `/rain_compare Area 1 30`",
                    parse_mode='Markdown'
                )
                return
            
            lat, lon = coordinates
            
            # Send processing message
            processing_msg = await update.message.reply_text(
                f"🔄 Comparing {current_rainfall}mm rainfall with {years} years of historical data..."
            )
            
            # Get current month
            current_month = datetime.datetime.now().strftime('%B')
            
            # Compare with historical patterns
            comparison = self.analyzer.compare_with_historical_patterns(
                lat, lon, current_rainfall, current_month, years, str(user_id)
            )
            
            if not comparison or 'error' in comparison:
                await processing_msg.edit_text(
                    "❌ Unable to compare with historical data.\n"
                    "Please try again later."
                )
                return
            
            # Format and send comparison response
            response = self._format_rainfall_comparison_response(comparison, current_rainfall, current_month)
            await processing_msg.edit_text(response, parse_mode='Markdown')
            
            logger.info(f"Rainfall comparison provided to user {user_id}", str(user_id))
            
        except Exception as e:
            logger.error(f"Error in rain_compare command: {e}", str(user_id))
            await update.message.reply_text(
                "❌ Sorry, there was an error comparing rainfall data. Please try again later."
            )
    
    async def handle_drought_risk(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /drought_risk command for drought risk assessment.
        
        Usage:
        /drought_risk <coordinates> [years]
        /drought_risk Lilongwe 5
        /drought_risk -13.9833, 33.7833
        """
        user_id = update.effective_user.id
        try:
            if not context.args:
                await self._send_drought_risk_help(update)
                return
            
            # Parse arguments
            args_text = ' '.join(context.args)
            coordinates, years = self._parse_rain_history_args(args_text)
            
            if not coordinates:
                await update.message.reply_text(
                    "❌ Could not parse coordinates.\n\n"
                    "Examples:\n"
                    "• `/drought_risk Lilongwe 5`\n"
                    "• `/drought_risk -13.9833, 33.7833`",
                    parse_mode='Markdown'
                )
                return
            
            lat, lon = coordinates
            
            # Send processing message
            processing_msg = await update.message.reply_text(
                f"🔄 Assessing drought risk for {lat:.3f}, {lon:.3f}..."
            )
            
            # Mock current conditions (in real implementation, this would come from weather API)
            current_conditions = {
                'total_7day_rainfall': 5.0,  # Example current rainfall
                'temperature': 28,
                'humidity': 45
            }
            
            # Get drought risk assessment
            risk_assessment = self.analyzer.get_drought_risk_assessment(
                lat, lon, current_conditions, years, str(user_id)
            )
            
            if not risk_assessment or 'error' in risk_assessment:
                await processing_msg.edit_text(
                    "❌ Unable to assess drought risk.\n"
                    "Historical data may not be available for this location."
                )
                return
            
            # Format and send risk assessment
            response = self._format_drought_risk_response(risk_assessment)
            await processing_msg.edit_text(response, parse_mode='Markdown')
            
            logger.info(f"Drought risk assessment provided to user {user_id}", str(user_id))
            
        except Exception as e:
            logger.error(f"Error in drought_risk command: {e}", str(user_id))
            await update.message.reply_text(
                "❌ Sorry, there was an error assessing drought risk. Please try again later."
            )
    
    def _parse_rain_history_args(self, args_text: str) -> tuple[Optional[tuple[float, float]], int]:
        """Parse rain history command arguments."""
        # Default years
        years = 5
        
        # Extract years if specified (last token that's a number)
        parts = args_text.strip().split()
        if parts and parts[-1].isdigit():
            years = min(max(int(parts[-1]), 1), 10)  # Ensure 1-10 range
            args_text = ' '.join(parts[:-1])  # Remove years from coordinate parsing
        
        # Parse coordinates
        coordinates = self.coord_handler.parse_coordinates(args_text)
        
        return coordinates, years
    
    def _parse_rain_compare_args(self, args_text: str) -> tuple[Optional[tuple[float, float]], Optional[float], int]:
        """Parse rain compare command arguments."""
        years = 5
        current_rainfall = None
        
        parts = args_text.strip().split()
        
        # Find rainfall amount (number with optional decimal)
        rainfall_pattern = r'\b\d+\.?\d*\b'
        rainfall_matches = re.findall(rainfall_pattern, args_text)
        
        if not rainfall_matches:
            return None, None, years
        
        # Take the first number as rainfall, last as years if there are multiple
        if len(rainfall_matches) >= 2:
            current_rainfall = float(rainfall_matches[0])
            if rainfall_matches[-1] != rainfall_matches[0]:  # Different from rainfall
                years = min(max(int(float(rainfall_matches[-1])), 1), 10)
        else:
            current_rainfall = float(rainfall_matches[0])
        
        # Remove numbers from coordinate parsing
        coord_text = re.sub(rainfall_pattern, '', args_text).strip()
        coord_text = re.sub(r'\s+', ' ', coord_text)  # Clean up multiple spaces
        
        coordinates = self.coord_handler.parse_coordinates(coord_text)
        
        return coordinates, current_rainfall, years
    
    def _format_historical_rainfall_response(self, historical_data, lat: float, lon: float, years: int) -> str:
        """Format historical rainfall analysis response."""
        response = f"📊 **Historical Rainfall Analysis**\n"
        response += f"📍 Location: {lat:.3f}, {lon:.3f}\n"
        response += f"📅 Period: {years} years ({datetime.datetime.now().year - years}-{datetime.datetime.now().year - 1})\n\n"
        
        # Annual summary
        if historical_data.annual_averages:
            avg_annual = sum(historical_data.annual_averages) / len(historical_data.annual_averages)
            response += f"🌧️ **Annual Rainfall**\n"
            response += f"• Average: {avg_annual:.1f}mm per year\n"
            response += f"• Variability: {historical_data.rainfall_variability:.1f}%\n"
            response += f"• Trend: {historical_data.climate_trend.replace('_', ' ').title()}\n\n"
        
        # Seasonal patterns
        response += f"📅 **Seasonal Patterns**\n"
        if historical_data.wet_season_months:
            wet_months = ', '.join(historical_data.wet_season_months[:3])
            response += f"• Wet season: {wet_months}...\n"
        if historical_data.dry_season_months:
            dry_months = ', '.join(historical_data.dry_season_months[:3])
            response += f"• Dry season: {dry_months}...\n"
        
        # Extreme years
        if historical_data.drought_years or historical_data.flood_years:
            response += f"\n⚠️ **Extreme Weather Years**\n"
            if historical_data.drought_years:
                recent_droughts = historical_data.drought_years[-3:] if len(historical_data.drought_years) > 3 else historical_data.drought_years
                response += f"• Recent drought years: {', '.join(map(str, recent_droughts))}\n"
            if historical_data.flood_years:
                recent_floods = historical_data.flood_years[-3:] if len(historical_data.flood_years) > 3 else historical_data.flood_years
                response += f"• Recent flood years: {', '.join(map(str, recent_floods))}\n"
        
        # Current month context
        current_month = datetime.datetime.now().strftime('%B')
        if current_month in historical_data.monthly_averages:
            monthly_avg = historical_data.monthly_averages[current_month]
            response += f"\n📊 **{current_month} Average**\n"
            response += f"• Historical average: {monthly_avg:.1f}mm\n"
            response += f"• Season type: {'Wet' if current_month in historical_data.wet_season_months else 'Dry'}\n"
        
        return response
    
    def _format_rainfall_comparison_response(self, comparison: dict, current_rainfall: float, month: str) -> str:
        """Format rainfall comparison response."""
        response = f"📊 **Rainfall Comparison - {month}**\n\n"
        
        # Current vs historical
        response += f"🌧️ **Current vs Historical**\n"
        response += f"• Current rainfall: {current_rainfall}mm\n"
        response += f"• Historical average: {comparison['historical_average']:.1f}mm\n"
        response += f"• Percentage of normal: {comparison['percentage_of_normal']:.1f}%\n"
        response += f"• Status: {comparison['description']}\n\n"
        
        # Status indicator
        status_emoji = {
            'above_normal': '🟢',
            'normal': '🟡', 
            'below_normal': '🟠',
            'drought_conditions': '🔴'
        }
        emoji = status_emoji.get(comparison['status'], '⚪')
        response += f"{emoji} **Rainfall Status**: {comparison['description']}\n\n"
        
        # Agricultural implications
        if 'agricultural_implications' in comparison:
            response += f"🌾 **Agricultural Implications**\n"
            for implication in comparison['agricultural_implications']:
                response += f"• {implication}\n"
            response += "\n"
        
        # Recommendations
        if 'recommendations' in comparison:
            response += f"💡 **Recommendations**\n"
            for rec in comparison['recommendations']:
                response += f"• {rec}\n"
        
        return response
    
    def _format_drought_risk_response(self, risk_assessment: dict) -> str:
        """Format drought risk assessment response."""
        response = f"🌵 **Drought Risk Assessment**\n\n"
        
        # Risk level with emoji
        risk_level = risk_assessment['drought_risk_level']
        risk_emoji = {
            'very_high': '🔴',
            'high': '🟠', 
            'moderate': '🟡',
            'low': '🟢'
        }
        emoji = risk_emoji.get(risk_level, '⚪')
        response += f"{emoji} **Risk Level**: {risk_level.replace('_', ' ').upper()}\n\n"
        
        # Risk indicators
        indicators = risk_assessment.get('drought_indicators', {})
        response += f"📊 **Risk Indicators**\n"
        
        deficit_ratio = indicators.get('rainfall_deficit_ratio', 0)
        if deficit_ratio > 0:
            response += f"• Rainfall deficit: {deficit_ratio * 100:.1f}% below normal\n"
        
        variability = indicators.get('rainfall_variability', 0)
        response += f"• Rainfall variability: {variability:.1f}%\n"
        
        drought_freq = indicators.get('historical_drought_frequency', 0)
        response += f"• Historical drought frequency: {drought_freq * 100:.1f}%\n\n"
        
        # Historical context
        drought_years = risk_assessment.get('historical_drought_years', [])
        if drought_years:
            recent_droughts = drought_years[-3:] if len(drought_years) > 3 else drought_years
            response += f"📅 **Recent Drought Years**: {', '.join(map(str, recent_droughts))}\n\n"
        
        # Recommendations
        recommendations = risk_assessment.get('recommendations', [])
        if recommendations:
            response += f"💡 **Recommendations**\n"
            for rec in recommendations[:5]:  # Limit to top 5
                response += f"• {rec}\n"
            response += "\n"
        
        # Monitoring advice
        monitoring = risk_assessment.get('monitoring_advice', [])
        if monitoring:
            response += f"👁️ **Monitoring Advice**\n"
            for advice in monitoring[:3]:  # Limit to top 3
                response += f"• {advice}\n"
        
        return response
    
    async def _send_rain_history_help(self, update: Update) -> None:
        """Send help message for rain_history command."""
        help_text = """
🌧️ **Historical Rainfall Analysis**

**Usage:**
`/rain_history <location> [years]`

**Examples:**
• `/rain_history Lilongwe 5` - 5 years of data for Lilongwe
• `/rain_history -13.9833, 33.7833 3` - 3 years for coordinates
• `/rain_history Area 1` - Default 5 years for Area 1

**Parameters:**
• `location`: Coordinates or known location name
• `years`: Number of years (1-10, default: 5)

This command provides:
📊 Annual rainfall averages and trends
📅 Seasonal patterns (wet/dry seasons)  
⚠️ Historical drought and flood years
📈 Rainfall variability analysis
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def _send_rain_compare_help(self, update: Update) -> None:
        """Send help message for rain_compare command."""
        help_text = """
⚖️ **Compare Current with Historical Rainfall**

**Usage:**
`/rain_compare <location> <rainfall_mm> [years]`

**Examples:**
• `/rain_compare Lilongwe 25 5` - Compare 25mm with 5 years of data
• `/rain_compare -13.9833, 33.7833 15.5` - Compare 15.5mm (default 5 years)
• `/rain_compare Area 1 30` - Compare 30mm with historical average

**Parameters:**
• `location`: Coordinates or known location name
• `rainfall_mm`: Current rainfall amount in millimeters
• `years`: Historical years to compare (1-10, default: 5)

This command provides:
📊 Current vs historical comparison
🟢🟡🟠🔴 Rainfall status indicators
🌾 Agricultural implications
💡 Specific recommendations
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def _send_drought_risk_help(self, update: Update) -> None:
        """Send help message for drought_risk command."""
        help_text = """
🌵 **Drought Risk Assessment**

**Usage:**
`/drought_risk <location> [years]`

**Examples:**
• `/drought_risk Lilongwe 5` - 5 years of drought analysis
• `/drought_risk -13.9833, 33.7833` - Default 5 years
• `/drought_risk Area 1 7` - 7 years of historical context

**Parameters:**
• `location`: Coordinates or known location name  
• `years`: Historical years for analysis (1-10, default: 5)

This command provides:
🔴🟠🟡🟢 Risk level assessment
📊 Drought indicators and metrics
📅 Historical drought years
💡 Risk-specific recommendations
👁️ Monitoring guidance
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')


# Global historical rain handler instance
historical_rain_handler = HistoricalRainHandler() 