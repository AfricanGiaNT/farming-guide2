#!/usr/bin/env python3
"""
Demo AI-Enhanced Harvest Advisor - Phase 6
Demonstrates the AI-enhanced harvest advisor with mock AI responses
"""

import asyncio
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from scripts.handlers.harvest_advisor import HarvestAdvisor
from scripts.handlers.harvest_handler import HarvestHandler
from scripts.utils.logger import logger


class MockAIHarvestAdvisor(HarvestAdvisor):
    """Mock version of HarvestAdvisor that uses predefined AI responses."""
    
    def __init__(self):
        """Initialize with mock AI responses."""
        super().__init__()
        self.mock_ai_responses = {
            'maize': {
                'raw_response': """
                Risk Assessment:
                • Weather risks: Medium - monitor for late rains during harvest
                • Storage risks: Low - ensure proper drying before storage
                • Quality risks: Medium - handle carefully to prevent damage
                
                Timing Optimization:
                • Harvest when kernels are hard and dry (20-25% moisture)
                • Avoid harvesting during rainy periods
                • Complete harvest within 2-3 weeks of maturity
                
                Quality Enhancement:
                • Use clean, dry containers for collection
                • Remove damaged or diseased ears immediately
                • Sort by size and quality for better market value
                
                Market Timing:
                • Sell early harvest for premium prices
                • Store surplus for off-season sales
                • Monitor local market prices weekly
                
                Resource Optimization:
                • Use family labor efficiently during peak harvest
                • Invest in basic drying equipment for quality
                • Plan storage space based on expected yield
                """,
                'personalized_recommendations': [
                    "Check maize moisture content daily before harvest",
                    "Prepare drying area with raised platforms",
                    "Organize storage containers by harvest date"
                ]
            },
            'beans': {
                'raw_response': """
                Risk Assessment:
                • Weather risks: High - beans are sensitive to moisture
                • Storage risks: High - prone to fungal growth
                • Quality risks: Medium - handle gently to prevent bruising
                
                Timing Optimization:
                • Harvest when pods are dry and brown
                • Avoid harvesting when dew is present
                • Complete harvest in morning hours
                
                Quality Enhancement:
                • Thresh carefully to avoid seed damage
                • Clean thoroughly to remove debris
                • Grade by size and color for better prices
                
                Market Timing:
                • Sell fresh beans immediately after harvest
                • Store dried beans in airtight containers
                • Target local markets for best prices
                
                Resource Optimization:
                • Use manual threshing for small plots
                • Invest in moisture meters for quality control
                • Plan harvest timing with family availability
                """,
                'personalized_recommendations': [
                    "Harvest beans only when pods are completely dry",
                    "Use clean tarps for threshing to maintain quality",
                    "Store in cool, dry location with good ventilation"
                ]
            },
            'groundnuts': {
                'raw_response': """
                Risk Assessment:
                • Weather risks: Medium - avoid harvesting in wet soil
                • Storage risks: High - very prone to aflatoxin
                • Quality risks: High - handle with extreme care
                
                Timing Optimization:
                • Harvest when leaves turn yellow and dry
                • Ensure soil is dry before digging
                • Complete harvest before heavy rains
                
                Quality Enhancement:
                • Dig carefully to avoid damaging pods
                • Dry immediately after harvest
                • Sort and remove damaged pods
                
                Market Timing:
                • Sell fresh groundnuts for immediate consumption
                • Process into oil or paste for value addition
                • Store properly to prevent aflatoxin contamination
                
                Resource Optimization:
                • Use family labor for careful harvesting
                • Invest in proper drying racks
                • Plan processing for value addition
                """,
                'personalized_recommendations': [
                    "Test soil moisture before starting harvest",
                    "Use wooden tools to avoid pod damage",
                    "Dry groundnuts on raised platforms immediately"
                ]
            }
        }
    
    async def _get_ai_response(self, prompt: str, user_id: str) -> str:
        """Return mock AI response based on crop."""
        # Extract crop from prompt
        crop = None
        for test_crop in ['maize', 'beans', 'groundnuts']:
            if test_crop in prompt.lower():
                crop = test_crop
                break
        
        if crop and crop in self.mock_ai_responses:
            return self.mock_ai_responses[crop]['raw_response']
        
        # Fallback response
        return """
        Risk Assessment:
        • Weather risks: Monitor local conditions
        • Storage risks: Use proper containers
        
        Timing Optimization:
        • Harvest at optimal maturity
        • Avoid adverse weather conditions
        
        Quality Enhancement:
        • Handle crops carefully
        • Maintain proper drying conditions
        """


async def demo_ai_harvest_enhancement():
    """Demonstrate the AI-enhanced harvest advisor."""
    print("🚀 AI-Enhanced Harvest Advisor Demo")
    print("=" * 60)
    
    # Initialize mock advisor
    advisor = MockAIHarvestAdvisor()
    handler = HarvestHandler()
    
    # Replace handler's advisor with mock version
    handler.harvest_advisor = advisor
    
    # Demo cases
    demo_cases = [
        {
            'crop': 'maize',
            'location': '-13.9833, 33.7833',
            'user_id': 'demo_user_001',
            'description': 'Maize harvest in Lilongwe area'
        },
        {
            'crop': 'beans',
            'location': 'Lilongwe',
            'user_id': 'demo_user_002',
            'description': 'Bean harvest in Lilongwe'
        },
        {
            'crop': 'groundnuts',
            'location': '-13.9833, 33.7833',
            'user_id': 'demo_user_003',
            'description': 'Groundnut harvest in Lilongwe area'
        }
    ]
    
    for i, demo_case in enumerate(demo_cases, 1):
        print(f"\n🎯 Demo {i}: {demo_case['description']}")
        print("=" * 50)
        
        try:
            # Get AI-enhanced advice
            print(f"📋 Generating AI-enhanced harvest advice for {demo_case['crop']}...")
            advice = await advisor.get_harvest_advice(
                demo_case['crop'],
                demo_case['location'],
                demo_case['user_id']
            )
            
            # Check AI enhancement
            if advice.get('ai_enhanced'):
                print("✅ AI Enhancement: Successful")
                
                # Show AI insights
                ai_insights = advice.get('ai_insights', {})
                if ai_insights.get('raw_response'):
                    print(f"🤖 AI Analysis: {len(ai_insights['raw_response'])} characters")
                
                # Show personalized recommendations
                personalized = advice.get('personalized_recommendations', [])
                print(f"🎯 Personalized Recommendations: {len(personalized)} items")
                
                # Show risk assessment
                risk_assessment = advice.get('risk_assessment', {})
                if risk_assessment.get('overall_risk_level'):
                    print(f"⚠️ Overall Risk: {risk_assessment['overall_risk_level']}")
                
            else:
                print(f"❌ AI Enhancement: Failed - {advice.get('ai_error', 'Unknown error')}")
            
            # Format and display response
            print(f"\n📄 AI-Enhanced Harvest Advice:")
            print("-" * 40)
            formatted_response = advisor.format_harvest_advice(advice)
            print(formatted_response)
            
            # Test handler
            print(f"\n📱 Testing Handler Integration:")
            print("-" * 40)
            command = f"/harvest {demo_case['crop']} {demo_case['location']}"
            response = await handler.handle_harvest_command(command, demo_case['user_id'])
            
            if "AI-Enhanced Analysis" in response:
                print("✅ Handler AI Integration: Successful")
            else:
                print("❌ Handler AI Integration: Missing")
            
        except Exception as e:
            print(f"❌ Demo failed: {str(e)}")
            logger.error(f"Demo {i} failed: {str(e)}")
    
    print(f"\n🎉 AI Enhancement Demo Complete!")
    print("=" * 60)


def main():
    """Run the AI enhancement demo."""
    print("🚀 Starting AI-Enhanced Harvest Advisor Demo")
    print("=" * 60)
    
    try:
        # Run demo
        asyncio.run(demo_ai_harvest_enhancement())
        
        print("\n🎯 Demo Completed Successfully!")
        print("\n💡 Key Features Demonstrated:")
        print("   • AI-powered risk assessment")
        print("   • Personalized recommendations")
        print("   • Enhanced timing optimization")
        print("   • Quality enhancement strategies")
        print("   • Market timing advice")
        print("   • Resource optimization")
        
    except Exception as e:
        print(f"\n❌ Demo Failed: {str(e)}")
        logger.error(f"Demo failed: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 