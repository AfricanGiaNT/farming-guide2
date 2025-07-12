#!/usr/bin/env python3
"""
Local Demo Script for Agricultural Advisor Bot
Demonstrates enhanced capabilities without requiring Telegram or PDFs
"""

import os
import sys
import asyncio
from datetime import datetime

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

try:
    from scripts.crop_advisor.enhanced_recommendation_engine import EnhancedRecommendationEngine
    from scripts.weather_engine.weather_api import WeatherAPI
    from scripts.data_pipeline.semantic_search import SemanticSearch
    from scripts.utils.logger import logger
    from scripts.utils.config_loader import config
    
    # Try to import rainfall analyzer - might not exist
    try:
        from scripts.weather_engine.rainfall_analyzer import RainfallAnalyzer
        RAINFALL_ANALYZER_AVAILABLE = True
    except ImportError:
        RAINFALL_ANALYZER_AVAILABLE = False
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running this script from the project root directory")
    sys.exit(1)


class BotDemo:
    """Local demonstration of the Agricultural Advisor Bot capabilities."""
    
    def __init__(self):
        """Initialize the demo system."""
        print("🌾 Agricultural Advisor Bot - Local Demo")
        print("=" * 50)
        
        # Initialize components
        self.recommendation_engine = EnhancedRecommendationEngine()
        self.weather_api = WeatherAPI()
        
        # Initialize rainfall analyzer if available
        if RAINFALL_ANALYZER_AVAILABLE:
            self.rainfall_analyzer = RainfallAnalyzer()
            print("✅ Rainfall analyzer initialized")
        else:
            self.rainfall_analyzer = None
            print("⚠️  Rainfall analyzer not available (using mock data)")
            
        self.semantic_search = SemanticSearch()
        
        print("✅ All components initialized successfully!")
    
    def demo_enhanced_recommendations(self):
        """Demonstrate enhanced crop recommendations."""
        print("\n🌱 Enhanced Crop Recommendations Demo")
        print("-" * 40)
        
        # Mock data for Lilongwe, Malawi
        sample_weather = {
            'temperature': 24.5,
            'humidity': 68,
            'description': 'scattered clouds',
            'wind_speed': 2.8,
            'pressure': 1013.2,
            'visibility': 10000
        }
        
        sample_rainfall = {
            'current_rainfall': 42.3,
            'forecast_rainfall': 145.7,
            'seasonal_average': 820.5,
            'monthly_pattern': [15, 28, 75, 125, 48, 12, 3, 5, 22, 68, 102, 88],
            'drought_risk': 'low',
            'flood_risk': 'medium'
        }
        
        print("📊 Sample Data:")
        print(f"  • Location: Lilongwe, Malawi (-13.9833, 33.7833)")
        print(f"  • Current Temperature: {sample_weather['temperature']}°C")
        print(f"  • Current Rainfall: {sample_rainfall['current_rainfall']}mm")
        print(f"  • Forecast Rainfall: {sample_rainfall['forecast_rainfall']}mm")
        print(f"  • Seasonal Average: {sample_rainfall['seasonal_average']}mm")
        
        # Generate recommendations
        print("\n🔄 Generating enhanced recommendations...")
        recommendations = self.recommendation_engine.generate_recommendations(
            sample_rainfall, sample_weather, -13.9833, 33.7833
        )
        
        if recommendations:
            print(f"✅ Generated {len(recommendations)} crop recommendations!")
            print("\n🏆 Top Recommendations:")
            
            for i, rec in enumerate(recommendations[:5], 1):
                crop_name = rec.get('crop_name', 'Unknown')
                variety = rec.get('variety', 'Standard')
                total_score = rec.get('total_score', 0)
                confidence = rec.get('confidence', {})
                
                print(f"\n{i}. {crop_name} - {variety}")
                print(f"   Score: {total_score}/125 points")
                print(f"   Confidence: {confidence.get('confidence_level', 'N/A')}")
                
                # Show score breakdown
                score_components = rec.get('score_components', {})
                print(f"   Score Breakdown:")
                for component, score in score_components.items():
                    print(f"     • {component}: {score} points")
                
                # Show recommendations
                planting_calendar = rec.get('planting_calendar', {})
                if planting_calendar:
                    current_month = datetime.now().month
                    current_advice = planting_calendar.get(f'month_{current_month}', {})
                    if current_advice:
                        print(f"   📅 Current Month Advice: {current_advice.get('recommendation', 'Monitor conditions')}")
        else:
            print("❌ No recommendations generated")
    
    def demo_weather_analysis(self):
        """Demonstrate weather analysis capabilities."""
        print("\n🌤️ Weather Analysis Demo")
        print("-" * 30)
        
        # Mock weather data
        sample_weather = {
            'temperature': 24.5,
            'humidity': 68,
            'description': 'scattered clouds',
            'wind_speed': 2.8
        }
        
        print("📈 Weather Analysis:")
        print(f"  • Temperature: {sample_weather['temperature']}°C")
        print(f"  • Humidity: {sample_weather['humidity']}%")
        print(f"  • Conditions: {sample_weather['description'].title()}")
        print(f"  • Wind Speed: {sample_weather['wind_speed']} m/s")
        
        # Analyze suitability
        if sample_weather['temperature'] >= 20 and sample_weather['temperature'] <= 30:
            temp_status = "✅ Optimal for most crops"
        elif sample_weather['temperature'] < 20:
            temp_status = "⚠️ Cool - consider cold-tolerant varieties"
        else:
            temp_status = "⚠️ Hot - ensure adequate irrigation"
        
        if sample_weather['humidity'] >= 60 and sample_weather['humidity'] <= 80:
            humidity_status = "✅ Good humidity levels"
        elif sample_weather['humidity'] < 60:
            humidity_status = "⚠️ Low humidity - increase irrigation"
        else:
            humidity_status = "⚠️ High humidity - monitor for fungal diseases"
        
        print(f"\n🎯 Agricultural Assessment:")
        print(f"  • Temperature: {temp_status}")
        print(f"  • Humidity: {humidity_status}")
    
    def demo_rainfall_analysis(self):
        """Demonstrate rainfall analysis capabilities."""
        print("\n🌧️ Rainfall Analysis Demo")
        print("-" * 30)
        
        # Mock rainfall data
        sample_rainfall = {
            'current_rainfall': 42.3,
            'forecast_rainfall': 145.7,
            'seasonal_average': 820.5,
            'monthly_pattern': [15, 28, 75, 125, 48, 12, 3, 5, 22, 68, 102, 88]
        }
        
        print("📊 Rainfall Analysis:")
        print(f"  • Current Month: {sample_rainfall['current_rainfall']}mm")
        print(f"  • Forecast (3-month): {sample_rainfall['forecast_rainfall']}mm")
        print(f"  • Seasonal Average: {sample_rainfall['seasonal_average']}mm")
        
        # Analyze patterns
        monthly_pattern = sample_rainfall['monthly_pattern']
        wet_months = [i+1 for i, rainfall in enumerate(monthly_pattern) if rainfall > 50]
        dry_months = [i+1 for i, rainfall in enumerate(monthly_pattern) if rainfall < 20]
        
        print(f"\n🎯 Pattern Analysis:")
        print(f"  • Wet Season: Months {', '.join(map(str, wet_months))}")
        print(f"  • Dry Season: Months {', '.join(map(str, dry_months))}")
        
        # Planting recommendations
        if sample_rainfall['current_rainfall'] > 40:
            print(f"  • Current Status: ✅ Good for planting")
        else:
            print(f"  • Current Status: ⚠️ Monitor soil moisture")
            
        if not RAINFALL_ANALYZER_AVAILABLE:
            print(f"  • Note: Using mock data (rainfall analyzer not available)")
    
    def demo_knowledge_base(self):
        """Demonstrate knowledge base capabilities."""
        print("\n📚 Knowledge Base Demo")
        print("-" * 25)
        
        # Check database status
        status = self.semantic_search.get_database_status()
        print("📊 Knowledge Base Status:")
        print(f"  • Total Documents: {status.get('total_documents', 0)}")
        print(f"  • Total Chunks: {status.get('total_chunks', 0)}")
        print(f"  • Vector Database: {status.get('vector_count', 0)} vectors")
        
        if status.get('total_documents', 0) == 0:
            print("\n💡 Knowledge Base Enhancement:")
            print("  • Add agricultural PDFs to data/pdfs/")
            print("  • Run: python setup_knowledge_base.py")
            print("  • Benefit: PDF-enhanced recommendations")
            print("  • Example PDFs: crop guides, pest management, soil prep")
        else:
            print("\n✅ Knowledge Base Active!")
            print("  • PDF search available")
            print("  • Enhanced recommendations with document context")
    
    def demo_confidence_scoring(self):
        """Demonstrate confidence scoring system."""
        print("\n🎯 Confidence Scoring Demo")
        print("-" * 30)
        
        # Mock recommendation for confidence analysis
        sample_recommendation = {
            'crop_id': 'maize',
            'variety': 'SC627',
            'total_score': 95,
            'score_components': {
                'rainfall_score': 38,
                'temperature_score': 22,
                'seasonal_score': 18,
                'humidity_score': 8,
                'soil_score': 9
            },
            'data_sources': ['weather_api', 'crop_database'],
            'timestamp': datetime.now().isoformat()
        }
        
        # Calculate confidence
        confidence_scorer = self.recommendation_engine.confidence_scorer
        confidence_result = confidence_scorer.calculate_confidence(sample_recommendation)
        
        print("📊 Confidence Analysis:")
        print(f"  • Confidence Score: {confidence_result.get('confidence_score', 0):.3f}")
        print(f"  • Confidence Level: {confidence_result.get('confidence_level', 'N/A')}")
        print(f"  • Data Quality: {confidence_result.get('data_quality', 'N/A')}")
        
        recommendations = confidence_result.get('recommendations', [])
        if recommendations:
            print(f"  • Improvement Suggestions:")
            for rec in recommendations[:3]:
                print(f"    • {rec}")
    
    def demo_system_health(self):
        """Demonstrate system health monitoring."""
        print("\n🏥 System Health Demo")
        print("-" * 25)
        
        print("🔍 Component Status:")
        
        # Check each component
        components = [
            ("Enhanced Recommendation Engine", self.recommendation_engine),
            ("Weather API", self.weather_api),
            ("Semantic Search", self.semantic_search)
        ]
        
        # Add rainfall analyzer if available
        if RAINFALL_ANALYZER_AVAILABLE and self.rainfall_analyzer:
            components.append(("Rainfall Analyzer", self.rainfall_analyzer))
        
        for name, component in components:
            try:
                if hasattr(component, 'get_status'):
                    status = component.get_status()
                    print(f"  • {name}: ✅ {status}")
                else:
                    print(f"  • {name}: ✅ Operational")
            except Exception as e:
                print(f"  • {name}: ❌ Error: {e}")
                
        if not RAINFALL_ANALYZER_AVAILABLE:
            print(f"  • Rainfall Analyzer: ⚠️ Not available (using mock data)")
    
    def interactive_demo(self):
        """Run an interactive demonstration."""
        print("\n🎮 Interactive Demo Mode")
        print("-" * 30)
        
        demos = {
            '1': ('Enhanced Recommendations', self.demo_enhanced_recommendations),
            '2': ('Weather Analysis', self.demo_weather_analysis),
            '3': ('Rainfall Analysis', self.demo_rainfall_analysis),
            '4': ('Knowledge Base Status', self.demo_knowledge_base),
            '5': ('Confidence Scoring', self.demo_confidence_scoring),
            '6': ('System Health', self.demo_system_health),
            '7': ('All Demos', self.run_all_demos)
        }
        
        while True:
            print("\n🎯 Available Demos:")
            for key, (name, _) in demos.items():
                print(f"  {key}. {name}")
            print("  q. Quit")
            
            choice = input("\nSelect demo (1-7, q): ").strip().lower()
            
            if choice in ['q', 'quit', 'exit']:
                break
            
            if choice in demos:
                print(f"\n🔄 Running {demos[choice][0]}...")
                demos[choice][1]()
            else:
                print("❌ Invalid choice. Please try again.")
        
        print("\n👋 Demo complete!")
    
    def run_all_demos(self):
        """Run all demonstration functions."""
        print("\n🚀 Running All Demos")
        print("=" * 30)
        
        self.demo_enhanced_recommendations()
        self.demo_weather_analysis()
        self.demo_rainfall_analysis()
        self.demo_knowledge_base()
        self.demo_confidence_scoring()
        self.demo_system_health()


def main():
    """Main function to run the bot demo."""
    try:
        demo = BotDemo()
        
        print("\n🎯 Demo Options:")
        print("1. Run interactive demo")
        print("2. Run all demos")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            demo.interactive_demo()
        elif choice == '2':
            demo.run_all_demos()
        elif choice == '3':
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice. Running all demos...")
            demo.run_all_demos()
        
        print("\n🎉 Agricultural Advisor Bot Demo Complete!")
        print("\nNext steps:")
        print("• Add PDFs to data/pdfs/ for enhanced knowledge base")
        print("• Start the Telegram bot with: python main.py")
        print("• Test with real weather data and locations")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        print("Please ensure all dependencies are installed and configurations are correct")


if __name__ == "__main__":
    main() 