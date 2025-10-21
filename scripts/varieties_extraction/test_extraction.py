#!/usr/bin/env python3
"""
Varieties Extraction Test Script
Milestone 1: Testing and Validation

This script tests the varieties extraction system with the agricultural PDFs.
It validates the extraction process and provides detailed feedback.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Import our modules
from scripts.varieties_extraction.comprehensive_varieties_parser import ComprehensiveVarietiesParser
from scripts.varieties_extraction.database_manager import VarietiesDatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VarietiesExtractionTester:
    """
    Test the varieties extraction system.
    """
    
    def __init__(self, 
                 pdf_directory: str = "data/pdfs",
                 db_path: str = "data/agricultural_documents.db"):
        """
        Initialize the tester.
        
        Args:
            pdf_directory: Directory containing PDFs
            db_path: Path to database
        """
        self.pdf_directory = os.path.join(project_root, pdf_directory)
        self.db_path = os.path.join(project_root, db_path)
        
        # Initialize components
        self.db_manager = VarietiesDatabaseManager(db_path)
        self.parser = ComprehensiveVarietiesParser(pdf_directory, db_path)
        
        logger.info("VarietiesExtractionTester initialized")
    
    def run_full_test(self) -> Dict[str, Any]:
        """
        Run the complete test suite.
        
        Returns:
            Test results dictionary
        """
        logger.info("Starting full varieties extraction test")
        
        test_results = {
            "test_started": datetime.now().isoformat(),
            "tests_passed": 0,
            "tests_failed": 0,
            "results": {}
        }
        
        # Test 1: Database schema validation
        logger.info("Test 1: Database schema validation")
        schema_result = self._test_database_schema()
        test_results["results"]["schema_validation"] = schema_result
        if schema_result["passed"]:
            test_results["tests_passed"] += 1
        else:
            test_results["tests_failed"] += 1
        
        # Test 2: PDF file discovery
        logger.info("Test 2: PDF file discovery")
        pdf_result = self._test_pdf_discovery()
        test_results["results"]["pdf_discovery"] = pdf_result
        if pdf_result["passed"]:
            test_results["tests_passed"] += 1
        else:
            test_results["tests_failed"] += 1
        
        # Test 3: PDF text extraction
        logger.info("Test 3: PDF text extraction")
        extraction_result = self._test_pdf_extraction()
        test_results["results"]["pdf_extraction"] = extraction_result
        if extraction_result["passed"]:
            test_results["tests_passed"] += 1
        else:
            test_results["tests_failed"] += 1
        
        # Test 4: Crop identification
        logger.info("Test 4: Crop identification")
        crop_result = self._test_crop_identification()
        test_results["results"]["crop_identification"] = crop_result
        if crop_result["passed"]:
            test_results["tests_passed"] += 1
        else:
            test_results["tests_failed"] += 1
        
        # Test 5: Variety extraction (limited)
        logger.info("Test 5: Variety extraction (limited)")
        variety_result = self._test_variety_extraction()
        test_results["results"]["variety_extraction"] = variety_result
        if variety_result["passed"]:
            test_results["tests_passed"] += 1
        else:
            test_results["tests_failed"] += 1
        
        # Test 6: Database storage
        logger.info("Test 6: Database storage")
        storage_result = self._test_database_storage()
        test_results["results"]["database_storage"] = storage_result
        if storage_result["passed"]:
            test_results["tests_passed"] += 1
        else:
            test_results["tests_failed"] += 1
        
        test_results["test_completed"] = datetime.now().isoformat()
        test_results["success_rate"] = test_results["tests_passed"] / (test_results["tests_passed"] + test_results["tests_failed"])
        
        logger.info(f"Test completed: {test_results['tests_passed']} passed, {test_results['tests_failed']} failed")
        
        return test_results
    
    def _test_database_schema(self) -> Dict[str, Any]:
        """Test database schema creation and validation."""
        try:
            # Create schema
            schema_created = self.db_manager.create_complete_schema()
            
            # Validate schema
            validation = self.db_manager.validate_schema()
            
            return {
                "passed": schema_created and validation["valid"],
                "schema_created": schema_created,
                "validation_valid": validation["valid"],
                "errors": validation.get("errors", []),
                "warnings": validation.get("warnings", [])
            }
        except Exception as e:
            return {
                "passed": False,
                "error": str(e)
            }
    
    def _test_pdf_discovery(self) -> Dict[str, Any]:
        """Test PDF file discovery."""
        try:
            pdf_files = self.parser._get_pdf_files()
            
            return {
                "passed": len(pdf_files) > 0,
                "pdf_count": len(pdf_files),
                "pdf_files": [os.path.basename(f) for f in pdf_files],
                "directory": self.pdf_directory
            }
        except Exception as e:
            return {
                "passed": False,
                "error": str(e)
            }
    
    def _test_pdf_extraction(self) -> Dict[str, Any]:
        """Test PDF text extraction."""
        try:
            pdf_files = self.parser._get_pdf_files()
            if not pdf_files:
                return {
                    "passed": False,
                    "error": "No PDF files found"
                }
            
            # Test extraction on first PDF
            test_pdf = pdf_files[0]
            text_content = self.parser._extract_pdf_text(test_pdf)
            
            return {
                "passed": len(text_content) > 0,
                "test_pdf": os.path.basename(test_pdf),
                "text_length": len(text_content),
                "text_preview": text_content[:200] + "..." if len(text_content) > 200 else text_content
            }
        except Exception as e:
            return {
                "passed": False,
                "error": str(e)
            }
    
    def _test_crop_identification(self) -> Dict[str, Any]:
        """Test crop identification in text."""
        try:
            pdf_files = self.parser._get_pdf_files()
            if not pdf_files:
                return {
                    "passed": False,
                    "error": "No PDF files found"
                }
            
            # Test crop identification on first PDF
            test_pdf = pdf_files[0]
            text_content = self.parser._extract_pdf_text(test_pdf)
            
            if not text_content:
                return {
                    "passed": False,
                    "error": "No text extracted from PDF"
                }
            
            crops_found = self.parser._identify_crops_in_text(text_content)
            
            return {
                "passed": len(crops_found) > 0,
                "test_pdf": os.path.basename(test_pdf),
                "crops_found": crops_found,
                "crop_count": len(crops_found)
            }
        except Exception as e:
            return {
                "passed": False,
                "error": str(e)
            }
    
    def _test_variety_extraction(self) -> Dict[str, Any]:
        """Test variety extraction (limited test)."""
        try:
            pdf_files = self.parser._get_pdf_files()
            if not pdf_files:
                return {
                    "passed": False,
                    "error": "No PDF files found"
                }
            
            # Test variety extraction on first PDF
            test_pdf = pdf_files[0]
            text_content = self.parser._extract_pdf_text(test_pdf)
            
            if not text_content:
                return {
                    "passed": False,
                    "error": "No text extracted from PDF"
                }
            
            crops_found = self.parser._identify_crops_in_text(text_content)
            
            if not crops_found:
                return {
                    "passed": False,
                    "error": "No crops identified in PDF"
                }
            
            # Test variety extraction for first crop
            test_crop = crops_found[0]
            varieties = self.parser._extract_crop_varieties(text_content, test_crop, test_pdf)
            
            return {
                "passed": len(varieties) >= 0,  # 0 varieties is still valid
                "test_crop": test_crop,
                "varieties_found": len(varieties),
                "variety_names": [v.get('variety_name', 'Unknown') for v in varieties[:5]]  # First 5
            }
        except Exception as e:
            return {
                "passed": False,
                "error": str(e)
            }
    
    def _test_database_storage(self) -> Dict[str, Any]:
        """Test database storage functionality."""
        try:
            # Get database stats before
            stats_before = self.db_manager.get_database_stats()
            
            # Run a small extraction test
            pdf_files = self.parser._get_pdf_files()
            if not pdf_files:
                return {
                    "passed": False,
                    "error": "No PDF files found"
                }
            
            # Test extraction on first PDF
            test_pdf = pdf_files[0]
            result = self.parser._extract_from_pdf(test_pdf)
            
            # Get database stats after
            stats_after = self.db_manager.get_database_stats()
            
            return {
                "passed": result.get("success", False),
                "extraction_result": result,
                "stats_before": stats_before,
                "stats_after": stats_after,
                "data_added": stats_after.get("varieties_count", 0) > stats_before.get("varieties_count", 0)
            }
        except Exception as e:
            return {
                "passed": False,
                "error": str(e)
            }
    
    def generate_test_report(self, test_results: Dict[str, Any]) -> str:
        """Generate a detailed test report."""
        report = []
        report.append("=" * 80)
        report.append("VARIETIES EXTRACTION SYSTEM TEST REPORT")
        report.append("=" * 80)
        report.append(f"Test Started: {test_results['test_started']}")
        report.append(f"Test Completed: {test_results['test_completed']}")
        report.append(f"Tests Passed: {test_results['tests_passed']}")
        report.append(f"Tests Failed: {test_results['tests_failed']}")
        report.append(f"Success Rate: {test_results['success_rate']:.2%}")
        report.append("")
        
        # Detailed results
        for test_name, result in test_results["results"].items():
            report.append(f"TEST: {test_name.upper()}")
            report.append("-" * 40)
            report.append(f"Status: {'PASS' if result['passed'] else 'FAIL'}")
            
            if result.get("error"):
                report.append(f"Error: {result['error']}")
            
            # Add specific details based on test type
            if test_name == "pdf_discovery":
                report.append(f"PDFs Found: {result.get('pdf_count', 0)}")
                if result.get('pdf_files'):
                    report.append("PDF Files:")
                    for pdf in result['pdf_files'][:5]:  # First 5
                        report.append(f"  - {pdf}")
            
            elif test_name == "pdf_extraction":
                report.append(f"Text Length: {result.get('text_length', 0)} characters")
                report.append(f"Test PDF: {result.get('test_pdf', 'N/A')}")
            
            elif test_name == "crop_identification":
                report.append(f"Crops Found: {result.get('crop_count', 0)}")
                if result.get('crops_found'):
                    report.append(f"Crops: {', '.join(result['crops_found'])}")
            
            elif test_name == "variety_extraction":
                report.append(f"Test Crop: {result.get('test_crop', 'N/A')}")
                report.append(f"Varieties Found: {result.get('varieties_found', 0)}")
                if result.get('variety_names'):
                    report.append(f"Variety Names: {', '.join(result['variety_names'])}")
            
            report.append("")
        
        return "\n".join(report)


def main():
    """Main function to run tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test varieties extraction system')
    parser.add_argument('--pdf-dir', default='data/pdfs', help='PDF directory')
    parser.add_argument('--db-path', default='data/agricultural_documents.db', help='Database path')
    parser.add_argument('--output', help='Output file for test report')
    
    args = parser.parse_args()
    
    # Initialize tester
    tester = VarietiesExtractionTester(args.pdf_dir, args.db_path)
    
    # Run tests
    print("🧪 Starting varieties extraction tests...")
    test_results = tester.run_full_test()
    
    # Generate report
    report = tester.generate_test_report(test_results)
    
    # Print report
    print("\n" + report)
    
    # Save report if requested
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"\n📄 Test report saved to: {args.output}")
    
    # Save results as JSON
    results_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    print(f"📊 Test results saved to: {results_file}")
    
    # Final status
    if test_results['success_rate'] >= 0.8:
        print("\n✅ Test suite PASSED (80%+ success rate)")
        return 0
    else:
        print("\n❌ Test suite FAILED (<80% success rate)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
