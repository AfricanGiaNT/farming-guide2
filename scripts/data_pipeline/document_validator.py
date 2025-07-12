#!/usr/bin/env python3
"""
Document Quality Validator
Validates documents before adding to the knowledge base.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import re

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

class DocumentValidator:
    """Validate documents for quality and relevance."""
    
    def __init__(self):
        """Initialize validator."""
        self.agricultural_keywords = [
            'crop', 'soil', 'plant', 'farming', 'agriculture', 'harvest',
            'seed', 'fertilizer', 'irrigation', 'pest', 'disease', 'yield',
            'groundnut', 'maize', 'beans', 'cassava', 'sweet potato',
            'malawi', 'africa', 'tropical', 'rainfall', 'climate'
        ]
        
    def validate_document(self, file_path: Path) -> Dict[str, Any]:
        """Validate a single document."""
        validation_result = {
            "filename": file_path.name,
            "is_valid": True,
            "issues": [],
            "quality_score": 0,
            "recommendations": []
        }
        
        try:
            # Check if file exists
            if not file_path.exists():
                validation_result["is_valid"] = False
                validation_result["issues"].append("File does not exist")
                return validation_result
            
            # Check file size
            file_size = file_path.stat().st_size
            if file_size < 1000:  # Very small file
                validation_result["issues"].append("File too small (< 1KB)")
                validation_result["quality_score"] -= 20
            elif file_size > 50 * 1024 * 1024:  # Very large file
                validation_result["issues"].append("File very large (> 50MB)")
                validation_result["quality_score"] -= 10
            else:
                validation_result["quality_score"] += 20
            
            # Check file extension
            if file_path.suffix.lower() != '.pdf':
                validation_result["issues"].append("File is not a PDF")
                validation_result["quality_score"] -= 30
            else:
                validation_result["quality_score"] += 10
            
            # Check filename for agricultural relevance
            filename_lower = file_path.name.lower()
            agricultural_terms_in_name = sum(1 for keyword in self.agricultural_keywords 
                                           if keyword in filename_lower)
            
            if agricultural_terms_in_name > 0:
                validation_result["quality_score"] += 30
                validation_result["recommendations"].append(f"Contains {agricultural_terms_in_name} agricultural terms in filename")
            else:
                validation_result["issues"].append("Filename doesn't suggest agricultural content")
                validation_result["quality_score"] -= 10
            
            # Basic content validation (if we can extract text)
            try:
                from scripts.data_pipeline.pdf_processor import PDFProcessor
                pdf_processor = PDFProcessor()
                text = pdf_processor.extract_text_from_pdf(str(file_path))
                
                if not text:
                    validation_result["issues"].append("Could not extract any text from PDF")
                    validation_result["quality_score"] -= 40
                else:
                    # Check text length
                    text_length = len(text)
                    if text_length < 500:
                        validation_result["issues"].append("Very little text content")
                        validation_result["quality_score"] -= 30
                    elif text_length > 10000:
                        validation_result["quality_score"] += 30
                        validation_result["recommendations"].append("Document has substantial content")
                    else:
                        validation_result["quality_score"] += 10
                    
                    # Check for agricultural keywords in content
                    text_lower = text.lower()
                    agricultural_terms_in_content = sum(1 for keyword in self.agricultural_keywords 
                                                      if keyword in text_lower)
                    
                    if agricultural_terms_in_content >= 10:
                        validation_result["quality_score"] += 40
                        validation_result["recommendations"].append(f"High agricultural relevance ({agricultural_terms_in_content} terms)")
                    elif agricultural_terms_in_content >= 5:
                        validation_result["quality_score"] += 30
                        validation_result["recommendations"].append(f"Good agricultural relevance ({agricultural_terms_in_content} terms)")
                    elif agricultural_terms_in_content >= 2:
                        validation_result["quality_score"] += 20
                        validation_result["recommendations"].append(f"Moderate agricultural relevance ({agricultural_terms_in_content} terms)")
                    else:
                        validation_result["issues"].append("Low agricultural content relevance")
                        validation_result["quality_score"] -= 20
                    
                    # Check for Malawi-specific content
                    malawi_terms = ['malawi', 'lilongwe', 'blantyre', 'mzuzu', 'zomba', 'southern africa']
                    malawi_mentions = sum(1 for term in malawi_terms if term in text_lower)
                    if malawi_mentions > 0:
                        validation_result["quality_score"] += 20
                        validation_result["recommendations"].append(f"Contains Malawi-specific content ({malawi_mentions} mentions)")
                    
                    # Check for technical agricultural terms
                    technical_terms = ['nitrogen', 'phosphorus', 'potassium', 'ph', 'hectare', 'kg/ha', 'varieties']
                    technical_mentions = sum(1 for term in technical_terms if term in text_lower)
                    if technical_mentions >= 3:
                        validation_result["quality_score"] += 15
                        validation_result["recommendations"].append("Contains technical agricultural information")
                    
                    # Check for quality indicators
                    quality_indicators = ['research', 'study', 'ministry', 'department', 'university', 'extension']
                    quality_mentions = sum(1 for term in quality_indicators if term in text_lower)
                    if quality_mentions >= 2:
                        validation_result["quality_score"] += 10
                        validation_result["recommendations"].append("Appears to be from authoritative source")
                
            except Exception as e:
                validation_result["issues"].append(f"Could not extract text: {e}")
                validation_result["quality_score"] -= 30
            
            # Final validation
            if validation_result["quality_score"] < 30:
                validation_result["is_valid"] = False
                validation_result["recommendations"].append("Quality score too low - review before adding")
            elif validation_result["quality_score"] >= 80:
                validation_result["recommendations"].append("High quality document - recommended for addition")
            
            return validation_result
            
        except Exception as e:
            validation_result["is_valid"] = False
            validation_result["issues"].append(f"Validation error: {e}")
            return validation_result
    
    def validate_directory(self, directory: str = "data/pdfs/") -> List[Dict[str, Any]]:
        """Validate all documents in directory."""
        directory = Path(directory)
        results = []
        
        if not directory.exists():
            print(f"Directory {directory} does not exist")
            return results
        
        pdf_files = list(directory.glob("*.pdf"))
        if not pdf_files:
            print(f"No PDF files found in {directory}")
            return results
        
        for pdf_file in pdf_files:
            result = self.validate_document(pdf_file)
            results.append(result)
        
        return results
    
    def get_validation_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get summary of validation results."""
        if not results:
            return {"total": 0, "valid": 0, "invalid": 0, "average_score": 0}
        
        total = len(results)
        valid = sum(1 for r in results if r["is_valid"])
        invalid = total - valid
        average_score = sum(r["quality_score"] for r in results) / total
        
        return {
            "total": total,
            "valid": valid,
            "invalid": invalid,
            "average_score": round(average_score, 2)
        }

if __name__ == "__main__":
    print("📋 Document Quality Validator")
    print("=" * 50)
    
    validator = DocumentValidator()
    results = validator.validate_directory()
    
    if not results:
        print("No documents to validate")
        sys.exit(0)
    
    print(f"\nValidation Results:")
    print("-" * 30)
    
    for result in results:
        status = "✅ VALID" if result["is_valid"] else "❌ INVALID"
        print(f"\n{status} - {result['filename']}")
        print(f"  Quality Score: {result['quality_score']}")
        
        if result["issues"]:
            print(f"  Issues:")
            for issue in result["issues"]:
                print(f"    ⚠️  {issue}")
        
        if result["recommendations"]:
            print(f"  Recommendations:")
            for rec in result["recommendations"]:
                print(f"    💡 {rec}")
    
    # Show summary
    summary = validator.get_validation_summary(results)
    print(f"\n📊 Summary:")
    print(f"  Total documents: {summary['total']}")
    print(f"  Valid: {summary['valid']}")
    print(f"  Invalid: {summary['invalid']}")
    print(f"  Average quality score: {summary['average_score']}")
    
    if summary['invalid'] > 0:
        print(f"\n⚠️  {summary['invalid']} documents need review before processing")
    else:
        print(f"\n✅ All documents passed validation!") 