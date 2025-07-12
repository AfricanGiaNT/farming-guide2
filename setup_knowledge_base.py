#!/usr/bin/env python3
"""
Knowledge Base Setup Script
Agricultural Advisor Bot - PDF Integration Helper

This script helps you:
1. Add PDFs to the knowledge base
2. Test the PDF processing pipeline
3. Verify the bot's enhanced functionality
"""

import os
import sys
import asyncio
from typing import List, Dict, Any
from pathlib import Path

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

try:
    from scripts.data_pipeline.semantic_search import SemanticSearch
    from scripts.data_pipeline.multi_document_manager import MultiDocumentManager
    from scripts.data_pipeline.knowledge_analytics import KnowledgeAnalytics
    from scripts.crop_advisor.enhanced_recommendation_engine import EnhancedRecommendationEngine
    from scripts.utils.logger import logger
    from scripts.utils.config_loader import config
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running this script from the project root directory")
    sys.exit(1)


class KnowledgeBaseSetup:
    """Setup and test the knowledge base with PDFs."""
    
    def __init__(self):
        """Initialize the setup system."""
        self.semantic_search = SemanticSearch()
        self.document_manager = MultiDocumentManager()
        self.analytics = KnowledgeAnalytics()
        self.recommendation_engine = EnhancedRecommendationEngine()
        
        # Create necessary directories
        os.makedirs("data/pdfs", exist_ok=True)
        os.makedirs("data/vector_db", exist_ok=True)
        
        print("🌾 Agricultural Advisor Bot - Knowledge Base Setup")
        print("=" * 60)
    
    def add_pdfs_to_knowledge_base(self, pdf_directory: str = "data/pdfs") -> bool:
        """
        Add all PDFs from a directory to the knowledge base.
        
        Args:
            pdf_directory: Directory containing PDF files
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Find all PDF files
            pdf_files = []
            if os.path.exists(pdf_directory):
                for file in os.listdir(pdf_directory):
                    if file.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(pdf_directory, file))
            
            if not pdf_files:
                print(f"📁 No PDF files found in {pdf_directory}")
                print(f"💡 Please add your agricultural PDF files to {pdf_directory}")
                return False
            
            print(f"📚 Found {len(pdf_files)} PDF files:")
            for pdf_file in pdf_files:
                print(f"  • {os.path.basename(pdf_file)}")
            
            # Process PDFs
            print("\n🔄 Processing PDFs...")
            success = self.semantic_search.process_pdf_documents(pdf_files)
            
            if success:
                print("✅ Successfully added PDFs to knowledge base!")
                
                # Show database status
                status = self.semantic_search.get_database_status()
                print(f"\n📊 Knowledge Base Status:")
                print(f"  • Total documents: {status['total_documents']}")
                print(f"  • Total chunks: {status['total_chunks']}")
                print(f"  • Vector database size: {status['vector_count']}")
                
                return True
            else:
                print("❌ Failed to process PDFs")
                return False
                
        except Exception as e:
            print(f"❌ Error adding PDFs: {e}")
            return False
    
    def test_pdf_search(self, test_queries: List[str] = None) -> None:
        """
        Test the PDF search functionality.
        
        Args:
            test_queries: List of test queries, uses defaults if None
        """
        if test_queries is None:
            test_queries = [
                "maize planting recommendations",
                "soil preparation techniques",
                "pest management strategies",
                "fertilizer application",
                "drought resistant crops"
            ]
        
        print("\n🔍 Testing PDF Search Functionality")
        print("-" * 40)
        
        for query in test_queries:
            print(f"\n❓ Query: '{query}'")
            results = self.semantic_search.search_documents(query, top_k=3)
            
            if results:
                print(f"✅ Found {len(results)} relevant results:")
                for i, result in enumerate(results, 1):
                    source = result.get('source_document', 'Unknown')
                    score = result.get('score', 0)
                    preview = result.get('text', '')[:100] + "..."
                    print(f"  {i}. {source} (Score: {score:.3f})")
                    print(f"     Preview: {preview}")
            else:
                print("❌ No results found")
    
    def test_enhanced_recommendations(self, location: str = "Lilongwe") -> None:
        """
        Test the enhanced recommendation system with PDF knowledge.
        
        Args:
            location: Location to test recommendations for
        """
        print(f"\n🌱 Testing Enhanced Recommendations for {location}")
        print("-" * 50)
        
        try:
            # Mock weather data for testing
            sample_weather = {
                'temperature': 25.5,
                'humidity': 65,
                'description': 'partly cloudy',
                'wind_speed': 3.2
            }
            
            sample_rainfall = {
                'current_rainfall': 45.2,
                'forecast_rainfall': 120.5,
                'seasonal_average': 850.0,
                'monthly_pattern': [20, 35, 85, 120, 45, 15, 5, 8, 25, 75, 110, 95]
            }
            
            # Generate recommendations
            recommendations = self.recommendation_engine.generate_recommendations(
                sample_rainfall, sample_weather, -13.9833, 33.7833
            )
            
            if recommendations:
                print("✅ Enhanced recommendations generated!")
                print(f"📊 Found {len(recommendations)} crop recommendations:")
                
                for i, rec in enumerate(recommendations[:3], 1):
                    crop_name = rec.get('crop_name', 'Unknown')
                    total_score = rec.get('total_score', 0)
                    confidence = rec.get('confidence', {})
                    
                    print(f"\n  {i}. {crop_name} (Score: {total_score}/125)")
                    print(f"     Confidence: {confidence.get('confidence_level', 'N/A')}")
                    
                    # Show PDF-enhanced information
                    pdf_info = rec.get('pdf_enhanced_info', {})
                    if pdf_info:
                        print(f"     📚 PDF Enhanced Info:")
                        varieties = pdf_info.get('enhanced_varieties', [])
                        if varieties:
                            print(f"       • Varieties: {', '.join(varieties[:3])}")
                        
                        practices = pdf_info.get('best_practices', [])
                        if practices:
                            print(f"       • Best Practices: {practices[0][:80]}...")
            else:
                print("❌ No recommendations generated")
                
        except Exception as e:
            print(f"❌ Error testing recommendations: {e}")
    
    def display_system_health(self) -> None:
        """Display the health status of all knowledge base components."""
        print("\n🏥 System Health Check")
        print("-" * 30)
        
        try:
            # Check PDF processing
            db_status = self.semantic_search.get_database_status()
            if db_status['total_documents'] > 0:
                print("✅ PDF Processing: Operational")
                print(f"   • Documents: {db_status['total_documents']}")
                print(f"   • Chunks: {db_status['total_chunks']}")
            else:
                print("⚠️  PDF Processing: No documents loaded")
            
            # Check vector database
            if db_status['vector_count'] > 0:
                print("✅ Vector Database: Operational")
                print(f"   • Vectors: {db_status['vector_count']}")
            else:
                print("⚠️  Vector Database: Empty")
            
            # Check analytics
            analytics_data = self.analytics.get_analytics_summary()
            if analytics_data:
                print("✅ Knowledge Analytics: Operational")
                print(f"   • Queries tracked: {analytics_data.get('total_queries', 0)}")
            else:
                print("⚠️  Knowledge Analytics: No data")
            
        except Exception as e:
            print(f"❌ Health check error: {e}")
    
    def interactive_test(self) -> None:
        """Run an interactive test session."""
        print("\n🎮 Interactive Test Mode")
        print("-" * 30)
        print("Enter search queries to test the knowledge base")
        print("Type 'quit' to exit")
        
        while True:
            try:
                query = input("\n🔍 Enter search query: ").strip()
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not query:
                    continue
                
                print(f"Searching for: '{query}'...")
                results = self.semantic_search.search_documents(query, top_k=5)
                
                if results:
                    print(f"Found {len(results)} results:")
                    for i, result in enumerate(results, 1):
                        source = result.get('source_document', 'Unknown')
                        score = result.get('score', 0)
                        text = result.get('text', '')
                        
                        print(f"\n{i}. Source: {source} (Score: {score:.3f})")
                        print(f"   Text: {text[:200]}{'...' if len(text) > 200 else ''}")
                else:
                    print("No results found")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("\n👋 Interactive test complete!")


def main():
    """Main function to run the knowledge base setup."""
    setup = KnowledgeBaseSetup()
    
    # Check if PDFs exist
    pdf_dir = "data/pdfs"
    if not os.path.exists(pdf_dir):
        print(f"📁 Creating PDF directory: {pdf_dir}")
        os.makedirs(pdf_dir, exist_ok=True)
    
    # Add PDFs if they exist
    if setup.add_pdfs_to_knowledge_base():
        # Test search functionality
        setup.test_pdf_search()
        
        # Test enhanced recommendations
        setup.test_enhanced_recommendations()
        
        # Display system health
        setup.display_system_health()
        
        # Ask if user wants interactive test
        response = input("\n🎮 Run interactive test? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            setup.interactive_test()
    
    print("\n🎉 Knowledge Base Setup Complete!")
    print("\nNext steps:")
    print("1. Add your agricultural PDFs to data/pdfs/")
    print("2. Run this script again to process them")
    print("3. Start the bot with: python main.py")


if __name__ == "__main__":
    main() 