#!/usr/bin/env python3
"""
Varieties Extraction Runner
Milestone 1: Execute Extraction Process

This script runs the complete varieties extraction process from PDFs to database.
"""

import os
import sys
import argparse
import logging
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Import our modules
from scripts.varieties_extraction.comprehensive_varieties_parser import ComprehensiveVarietiesParser
from scripts.varieties_extraction.database_manager import VarietiesDatabaseManager
from scripts.varieties_extraction.test_extraction import VarietiesExtractionTester

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'varieties_extraction_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run varieties extraction."""
    parser = argparse.ArgumentParser(description='Run varieties extraction from agricultural PDFs')
    parser.add_argument('--pdf-dir', default='data/pdfs', help='Directory containing PDFs')
    parser.add_argument('--db-path', default='data/agricultural_documents.db', help='Database path')
    parser.add_argument('--openai-key', help='OpenAI API key for AI extraction')
    parser.add_argument('--test-only', action='store_true', help='Run tests only, no extraction')
    parser.add_argument('--reset-db', action='store_true', help='Reset database before extraction')
    parser.add_argument('--validate-only', action='store_true', help='Validate database schema only')
    
    args = parser.parse_args()
    
    print("🌾 VARIETIES EXTRACTION SYSTEM")
    print("=" * 50)
    print(f"PDF Directory: {args.pdf_dir}")
    print(f"Database Path: {args.db_path}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        # Initialize database manager
        print("\n🏗️  Initializing database...")
        db_manager = VarietiesDatabaseManager(args.db_path)
        
        # Reset database if requested
        if args.reset_db:
            print("⚠️  Resetting database...")
            success = db_manager.reset_database()
            if not success:
                print("❌ Failed to reset database")
                return 1
            print("✅ Database reset completed")
        
        # Validate schema if requested
        if args.validate_only:
            print("\n🔍 Validating database schema...")
            validation = db_manager.validate_schema()
            if validation['valid']:
                print("✅ Schema validation passed")
                print(f"   Schema version: {validation.get('schema_version', 'Unknown')}")
                print(f"   Tables: {len(validation.get('tables', {}))}")
                print(f"   Indexes: {len(validation.get('indexes', []))}")
                print(f"   Views: {len(validation.get('views', []))}")
            else:
                print("❌ Schema validation failed")
                for error in validation.get('errors', []):
                    print(f"   Error: {error}")
            return 0
        
        # Run tests if requested
        if args.test_only:
            print("\n🧪 Running test suite...")
            tester = VarietiesExtractionTester(args.pdf_dir, args.db_path)
            test_results = tester.run_full_test()
            
            print(f"\n📊 Test Results:")
            print(f"   Tests Passed: {test_results['tests_passed']}")
            print(f"   Tests Failed: {test_results['tests_failed']}")
            print(f"   Success Rate: {test_results['success_rate']:.2%}")
            
            if test_results['success_rate'] >= 0.8:
                print("✅ Test suite PASSED")
                return 0
            else:
                print("❌ Test suite FAILED")
                return 1
        
        # Ensure database schema exists
        print("\n🏗️  Ensuring database schema...")
        schema_created = db_manager.create_complete_schema()
        if not schema_created:
            print("❌ Failed to create database schema")
            return 1
        print("✅ Database schema ready")
        
        # Initialize parser
        print("\n📚 Initializing varieties parser...")
        parser_instance = ComprehensiveVarietiesParser(
            pdf_directory=args.pdf_dir,
            db_path=args.db_path,
            openai_api_key=args.openai_key
        )
        print("✅ Parser initialized")
        
        # Run extraction
        print("\n🚀 Starting varieties extraction...")
        extraction_results = parser_instance.extract_from_all_pdfs()
        
        if extraction_results['success']:
            print("✅ Extraction completed successfully!")
            print(f"   Session ID: {extraction_results['session_id']}")
            print(f"   PDFs processed: {extraction_results['total_pdfs']}")
            print(f"   Total varieties extracted: {extraction_results['total_varieties']}")
            
            # Show detailed results
            print(f"\n📄 PDF Processing Results:")
            for pdf_file, result in extraction_results['results'].items():
                status = "✅" if result.get('success', False) else "❌"
                crops = result.get('crops_found', [])
                varieties = result.get('varieties_count', 0)
                print(f"   {status} {pdf_file}: {len(crops)} crops, {varieties} varieties")
                if crops:
                    print(f"      Crops: {', '.join(crops[:5])}{'...' if len(crops) > 5 else ''}")
            
            # Show database summary
            print(f"\n📊 Database Summary:")
            summary = parser_instance.get_extraction_summary()
            print(f"   Total crops: {summary.get('total_crops', 0)}")
            print(f"   Total varieties: {summary.get('total_varieties', 0)}")
            
            if summary.get('varieties_by_crop'):
                print(f"\n🌱 Top crops by variety count:")
                sorted_crops = sorted(summary['varieties_by_crop'].items(), 
                                    key=lambda x: x[1], reverse=True)
                for crop, count in sorted_crops[:10]:
                    print(f"   {crop}: {count} varieties")
            
            print(f"\n🎉 Varieties extraction completed successfully!")
            print(f"   Database: {args.db_path}")
            print(f"   Session: {extraction_results['session_id']}")
            
        else:
            print(f"❌ Extraction failed: {extraction_results.get('error', 'Unknown error')}")
            return 1
        
    except Exception as e:
        logger.error(f"Fatal error during extraction: {e}")
        print(f"❌ Fatal error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
