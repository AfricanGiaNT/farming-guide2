#!/usr/bin/env python3
"""
Targeted Chapter 3 Extraction Runner
Runs the targeted extraction specifically for Chapter 3 of the agriculture guide
"""

import argparse
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.varieties_extraction.targeted_chapter3_extractor import TargetedChapter3Extractor
from scripts.varieties_extraction.database_manager import VarietiesDatabaseManager
from scripts.utils.logger import BotLogger

logger = BotLogger()

def main():
    parser = argparse.ArgumentParser(description='Extract crop varieties from Chapter 3 of agriculture guide')
    parser.add_argument('--pdf-path', default='data/pdfs/Guide to Agriculture Production in Malawi 2021.pdf',
                       help='Path to the agriculture guide PDF')
    parser.add_argument('--db-path', default='data/agricultural_documents.db',
                       help='Path to SQLite database')
    parser.add_argument('--openai-key', help='OpenAI API key for AI extraction')
    parser.add_argument('--reset-db', action='store_true',
                       help='Reset database before extraction')
    parser.add_argument('--test-only', action='store_true',
                       help='Test extraction on first few crops only')
    
    args = parser.parse_args()
    
    # Validate PDF path
    if not os.path.exists(args.pdf_path):
        logger.error(f"PDF file not found: {args.pdf_path}")
        return 1
    
    # Initialize database manager
    db_manager = VarietiesDatabaseManager(args.db_path)
    
    # Reset database if requested
    if args.reset_db:
        logger.info("Resetting database...")
        db_manager.reset_database()
    
    # Initialize database schema
    db_manager.create_complete_schema()
    
    # Initialize extractor
    extractor = TargetedChapter3Extractor(db_manager, args.openai_key)
    
    # Run extraction
    logger.info("Starting targeted Chapter 3 extraction...")
    results = extractor.run_extraction(args.pdf_path)
    
    # Print results
    print("\n" + "="*50)
    print("EXTRACTION RESULTS")
    print("="*50)
    print(f"Session ID: {results['session_id']}")
    print(f"Crops Processed: {results['crops_processed']}")
    print(f"Varieties Extracted: {results['varieties_extracted']}")
    
    if results['errors']:
        print(f"Errors: {len(results['errors'])}")
        for error in results['errors'][:5]:  # Show first 5 errors
            print(f"  - {error}")
        if len(results['errors']) > 5:
            print(f"  ... and {len(results['errors']) - 5} more errors")
    
    print("="*50)
    
    # Show sample of extracted data
    print("\nSAMPLE EXTRACTED DATA:")
    crops = db_manager.get_all_crops()
    if crops:
        print(f"\nCrops in database: {len(crops)}")
        for crop in crops[:5]:  # Show first 5 crops
            print(f"  - {crop['crop_name']} ({crop['category']})")
            
            # Get varieties for this crop
            varieties = db_manager.get_varieties_by_crop_id(crop['id'])
            print(f"    Varieties: {len(varieties)}")
            for variety in varieties[:3]:  # Show first 3 varieties
                print(f"      * {variety['variety_name']}")
    
    return 0

if __name__ == "__main__":
    exit(main())
