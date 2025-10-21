#!/usr/bin/env python3
"""
Comprehensive Varieties Parser for Agricultural PDFs
Milestone 1: Data Extraction Pipeline

This module extracts detailed crop variety information from agricultural PDFs
specifically designed for the varieties database implementation.

Features:
- Extracts crop varieties, farming processes, rainfall requirements
- Handles multiple PDF formats and structures
- Provides structured data for database storage
- Includes confidence scoring and validation
"""

import os
import sys
import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import re
import hashlib

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

try:
    import PyPDF2
except ImportError:
    print("❌ PyPDF2 not installed. Install with: pip install PyPDF2")
    sys.exit(1)

try:
    import openai
    from openai import OpenAI
except ImportError:
    print("❌ OpenAI not installed. Install with: pip install openai")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveVarietiesParser:
    """
    Comprehensive parser for extracting crop variety information from agricultural PDFs.
    Designed specifically for the varieties database implementation.
    """
    
    def __init__(self, 
                 pdf_directory: str = "data/pdfs",
                 db_path: str = "data/agricultural_documents.db",
                 openai_api_key: str = None):
        """
        Initialize the varieties parser.
        
        Args:
            pdf_directory: Directory containing agricultural PDFs
            db_path: Path to SQLite database
            openai_api_key: OpenAI API key for AI extraction
        """
        self.pdf_directory = os.path.join(project_root, pdf_directory)
        self.db_path = os.path.join(project_root, db_path)
        self.session_id = f"extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize OpenAI client
        if openai_api_key:
            self.openai_client = OpenAI(api_key=openai_api_key)
        else:
            # Try to load from environment
            try:
                self.openai_client = OpenAI()
            except Exception as e:
                logger.warning(f"OpenAI client not initialized: {e}")
                self.openai_client = None
        
        # Crop priority list (most important crops first)
        self.priority_crops = [
            'maize', 'groundnut', 'soybean', 'bean', 'rice', 'sorghum',
            'cassava', 'sweet_potato', 'cowpea', 'pigeon_pea', 'tobacco',
            'cotton', 'sunflower', 'sesame', 'onion', 'tomato', 'lettuce'
        ]
        
        # Initialize database
        self._init_database()
        
        logger.info(f"ComprehensiveVarietiesParser initialized with session: {self.session_id}")
    
    def _init_database(self):
        """Initialize database tables for varieties extraction."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Create crops table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS crops (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crop_name TEXT NOT NULL UNIQUE,
                    scientific_name TEXT,
                    local_name TEXT,
                    category TEXT,
                    general_description TEXT,
                    overview_image_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create varieties table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS varieties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crop_id INTEGER,
                    variety_name TEXT NOT NULL,
                    type TEXT,
                    maturity_days INTEGER,
                    drought_tolerance TEXT,
                    disease_resistance TEXT,
                    yield_potential TEXT,
                    planting_months TEXT,
                    harvest_months TEXT,
                    min_rainfall_mm INTEGER,
                    max_rainfall_mm INTEGER,
                    optimal_temperature_min REAL,
                    optimal_temperature_max REAL,
                    soil_requirements TEXT,
                    spacing_requirements TEXT,
                    fertilizer_requirements TEXT,
                    pest_management TEXT,
                    disease_management TEXT,
                    harvesting_guidelines TEXT,
                    storage_requirements TEXT,
                    source_document TEXT,
                    extraction_confidence REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (crop_id) REFERENCES crops (id)
                )
            """)
            
            # Create farming processes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS farming_processes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    variety_id INTEGER,
                    process_type TEXT,
                    step_number INTEGER,
                    step_description TEXT,
                    timing TEXT,
                    tools_required TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (variety_id) REFERENCES varieties (id)
                )
            """)
            
            # Create extraction sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS extraction_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE,
                    pdf_files TEXT,
                    total_varieties_extracted INTEGER,
                    extraction_status TEXT,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)
            
            # Create indexes for performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_crops_name ON crops(crop_name)",
                "CREATE INDEX IF NOT EXISTS idx_varieties_crop_id ON varieties(crop_id)",
                "CREATE INDEX IF NOT EXISTS idx_varieties_name ON varieties(variety_name)",
                "CREATE INDEX IF NOT EXISTS idx_varieties_type ON varieties(type)",
                "CREATE INDEX IF NOT EXISTS idx_farming_processes_variety_id ON farming_processes(variety_id)",
                "CREATE INDEX IF NOT EXISTS idx_extraction_sessions_id ON extraction_sessions(session_id)"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            conn.commit()
            logger.info("Database tables initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def extract_from_all_pdfs(self) -> Dict[str, Any]:
        """
        Extract varieties data from all PDFs in the directory.
        
        Returns:
            Dictionary with extraction results and statistics
        """
        logger.info("Starting comprehensive varieties extraction from all PDFs")
        
        # Get all PDF files
        pdf_files = self._get_pdf_files()
        if not pdf_files:
            logger.error("No PDF files found in directory")
            return {"success": False, "error": "No PDF files found"}
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        # Initialize extraction session
        self._start_extraction_session(pdf_files)
        
        total_varieties = 0
        extraction_results = {}
        
        # Process each PDF
        for pdf_file in pdf_files:
            logger.info(f"Processing PDF: {pdf_file}")
            try:
                result = self._extract_from_pdf(pdf_file)
                extraction_results[pdf_file] = result
                total_varieties += result.get('varieties_count', 0)
                
            except Exception as e:
                logger.error(f"Error processing {pdf_file}: {e}")
                extraction_results[pdf_file] = {"success": False, "error": str(e)}
        
        # Complete extraction session
        self._complete_extraction_session(total_varieties)
        
        return {
            "success": True,
            "session_id": self.session_id,
            "total_pdfs": len(pdf_files),
            "total_varieties": total_varieties,
            "results": extraction_results
        }
    
    def _get_pdf_files(self) -> List[str]:
        """Get list of all PDF files in the directory."""
        pdf_files = []
        if os.path.exists(self.pdf_directory):
            for file in os.listdir(self.pdf_directory):
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(self.pdf_directory, file))
        return pdf_files
    
    def _extract_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract varieties data from a single PDF.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with extraction results
        """
        logger.info(f"Extracting varieties from: {os.path.basename(pdf_path)}")
        
        try:
            # Extract text from PDF
            text_content = self._extract_pdf_text(pdf_path)
            if not text_content:
                return {"success": False, "error": "No text extracted from PDF"}
            
            # Identify crops in the document
            crops_found = self._identify_crops_in_text(text_content)
            logger.info(f"Found crops in {os.path.basename(pdf_path)}: {crops_found}")
            
            varieties_extracted = 0
            
            # Extract varieties for each crop
            for crop in crops_found:
                crop_varieties = self._extract_crop_varieties(text_content, crop, pdf_path)
                if crop_varieties:
                    varieties_extracted += len(crop_varieties)
            
            return {
                "success": True,
                "pdf_file": os.path.basename(pdf_path),
                "crops_found": crops_found,
                "varieties_count": varieties_extracted,
                "text_length": len(text_content)
            }
            
        except Exception as e:
            logger.error(f"Error extracting from {pdf_path}: {e}")
            return {"success": False, "error": str(e)}
    
    def _extract_pdf_text(self, pdf_path: str) -> str:
        """Extract text content from PDF file."""
        try:
            text_content = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Check if PDF is encrypted
                if pdf_reader.is_encrypted:
                    try:
                        pdf_reader.decrypt("")
                    except Exception:
                        logger.warning(f"PDF is encrypted and cannot be decrypted: {pdf_path}")
                        return ""
                
                # Extract text from all pages
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    text_content += page_text + "\n"
            
            # Clean up text
            text_content = self._clean_text(text_content)
            logger.info(f"Extracted {len(text_content)} characters from {os.path.basename(pdf_path)}")
            return text_content
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
            return ""
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers
        text = re.sub(r'Page \d+', '', text)
        text = re.sub(r'\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Normalize line breaks
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        return text.strip()
    
    def _identify_crops_in_text(self, text: str) -> List[str]:
        """Identify which crops are mentioned in the text."""
        text_lower = text.lower()
        crops_found = []
        
        # Check for each priority crop
        for crop in self.priority_crops:
            crop_patterns = self._get_crop_patterns(crop)
            for pattern in crop_patterns:
                if re.search(pattern, text_lower):
                    crops_found.append(crop)
                    break
        
        return crops_found
    
    def _get_crop_patterns(self, crop: str) -> List[str]:
        """Get regex patterns for identifying a crop in text."""
        patterns = {
            'maize': [r'\bmaize\b', r'\bcorn\b', r'\bzea mays\b'],
            'groundnut': [r'\bgroundnut\b', r'\bpeanut\b', r'\barachis hypogaea\b'],
            'soybean': [r'\bsoybean\b', r'\bsoya\b', r'\bglycine max\b'],
            'bean': [r'\bbean\b', r'\bcommon bean\b', r'\bphaseolus vulgaris\b'],
            'rice': [r'\brice\b', r'\boryza sativa\b'],
            'sorghum': [r'\bsorghum\b', r'\bsorghum bicolor\b'],
            'cassava': [r'\bcassava\b', r'\bmanihot esculenta\b'],
            'sweet_potato': [r'\bsweet potato\b', r'\bipomoea batatas\b'],
            'cowpea': [r'\bcowpea\b', r'\bvigna unguiculata\b'],
            'pigeon_pea': [r'\bpigeon pea\b', r'\bcajanus cajan\b'],
            'tobacco': [r'\btobacco\b', r'\bnicotiana tabacum\b'],
            'cotton': [r'\bcotton\b', r'\bgossypium\b'],
            'sunflower': [r'\bsunflower\b', r'\bhelianthus annuus\b'],
            'sesame': [r'\bsesame\b', r'\bsesamum indicum\b'],
            'onion': [r'\bonion\b', r'\ballium cepa\b'],
            'tomato': [r'\btomato\b', r'\bsolanum lycopersicum\b'],
            'lettuce': [r'\blettuce\b', r'\blactuca sativa\b']
        }
        
        return patterns.get(crop, [rf'\b{crop}\b'])
    
    def _extract_crop_varieties(self, text: str, crop: str, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract variety information for a specific crop.
        
        Args:
            text: Full text content
            crop: Crop name
            pdf_path: Source PDF path
            
        Returns:
            List of variety dictionaries
        """
        logger.info(f"Extracting varieties for {crop} from {os.path.basename(pdf_path)}")
        
        # Use AI extraction if available
        if self.openai_client:
            return self._ai_extract_varieties(text, crop, pdf_path)
        else:
            # Fallback to pattern-based extraction
            return self._pattern_extract_varieties(text, crop, pdf_path)
    
    def _ai_extract_varieties(self, text: str, crop: str, pdf_path: str) -> List[Dict[str, Any]]:
        """Use AI to extract variety information."""
        try:
            prompt = f"""
            Extract detailed variety information for {crop} from the following agricultural text.
            
            Return a JSON array of varieties with the following structure:
            [
                {{
                    "variety_name": "exact variety name",
                    "type": "hybrid|open_pollinated|other",
                    "maturity_days": number,
                    "drought_tolerance": "excellent|good|moderate|poor",
                    "disease_resistance": ["disease1", "disease2"],
                    "yield_potential": "high|medium|low",
                    "planting_months": ["month1", "month2"],
                    "harvest_months": ["month1", "month2"],
                    "min_rainfall_mm": number,
                    "max_rainfall_mm": number,
                    "optimal_temperature_min": number,
                    "optimal_temperature_max": number,
                    "soil_requirements": "description",
                    "spacing_requirements": "description",
                    "fertilizer_requirements": "description",
                    "pest_management": "description",
                    "disease_management": "description",
                    "harvesting_guidelines": "description",
                    "storage_requirements": "description"
                }}
            ]
            
            Only extract information that is explicitly mentioned in the text.
            If information is not available, use null for that field.
            
            Text to analyze:
            {text[:4000]}  # Limit text length for API
            
            Return only valid JSON, no additional text.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2000
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content.strip()
            
            # Clean response (remove markdown formatting if present)
            if ai_response.startswith('```json'):
                ai_response = ai_response[7:]
            if ai_response.endswith('```'):
                ai_response = ai_response[:-3]
            
            varieties = json.loads(ai_response)
            
            # Add source information and save to database
            for variety in varieties:
                variety['source_document'] = os.path.basename(pdf_path)
                variety['extraction_confidence'] = 0.8  # AI extraction confidence
                self._save_variety_to_db(crop, variety)
            
            logger.info(f"AI extracted {len(varieties)} varieties for {crop}")
            return varieties
            
        except Exception as e:
            logger.error(f"AI extraction failed for {crop}: {e}")
            # Fallback to pattern extraction
            return self._pattern_extract_varieties(text, crop, pdf_path)
    
    def _pattern_extract_varieties(self, text: str, crop: str, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract varieties using pattern matching (fallback method)."""
        varieties = []
        
        # Look for variety names (common patterns)
        variety_patterns = [
            r'\b([A-Z]{2,3}\d{2,4})\b',  # SC403, DK8053, etc.
            r'\b([A-Z][a-z]+\d+)\b',      # Chalimbana1, etc.
            r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b',  # Local White, etc.
        ]
        
        for pattern in variety_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                variety = {
                    'variety_name': match,
                    'type': 'unknown',
                    'maturity_days': None,
                    'drought_tolerance': None,
                    'disease_resistance': [],
                    'yield_potential': None,
                    'planting_months': [],
                    'harvest_months': [],
                    'min_rainfall_mm': None,
                    'max_rainfall_mm': None,
                    'optimal_temperature_min': None,
                    'optimal_temperature_max': None,
                    'soil_requirements': None,
                    'spacing_requirements': None,
                    'fertilizer_requirements': None,
                    'pest_management': None,
                    'disease_management': None,
                    'harvesting_guidelines': None,
                    'storage_requirements': None,
                    'source_document': os.path.basename(pdf_path),
                    'extraction_confidence': 0.3  # Pattern extraction confidence
                }
                
                varieties.append(variety)
                self._save_variety_to_db(crop, variety)
        
        logger.info(f"Pattern extraction found {len(varieties)} varieties for {crop}")
        return varieties
    
    def _save_variety_to_db(self, crop_name: str, variety_data: Dict[str, Any]):
        """Save variety data to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get or create crop
            cursor.execute("SELECT id FROM crops WHERE crop_name = ?", (crop_name,))
            crop_result = cursor.fetchone()
            
            if crop_result:
                crop_id = crop_result[0]
            else:
                cursor.execute("""
                    INSERT INTO crops (crop_name, category) 
                    VALUES (?, ?)
                """, (crop_name, 'other'))
                crop_id = cursor.lastrowid
            
            # Insert variety
            cursor.execute("""
                INSERT INTO varieties (
                    crop_id, variety_name, type, maturity_days, drought_tolerance,
                    disease_resistance, yield_potential, planting_months, harvest_months,
                    min_rainfall_mm, max_rainfall_mm, optimal_temperature_min, optimal_temperature_max,
                    soil_requirements, spacing_requirements, fertilizer_requirements,
                    pest_management, disease_management, harvesting_guidelines, storage_requirements,
                    source_document, extraction_confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                crop_id,
                variety_data.get('variety_name'),
                variety_data.get('type'),
                variety_data.get('maturity_days'),
                variety_data.get('drought_tolerance'),
                json.dumps(variety_data.get('disease_resistance', [])),
                variety_data.get('yield_potential'),
                json.dumps(variety_data.get('planting_months', [])),
                json.dumps(variety_data.get('harvest_months', [])),
                variety_data.get('min_rainfall_mm'),
                variety_data.get('max_rainfall_mm'),
                variety_data.get('optimal_temperature_min'),
                variety_data.get('optimal_temperature_max'),
                variety_data.get('soil_requirements'),
                variety_data.get('spacing_requirements'),
                variety_data.get('fertilizer_requirements'),
                variety_data.get('pest_management'),
                variety_data.get('disease_management'),
                variety_data.get('harvesting_guidelines'),
                variety_data.get('storage_requirements'),
                variety_data.get('source_document'),
                variety_data.get('extraction_confidence')
            ))
            
            conn.commit()
            logger.debug(f"Saved variety {variety_data.get('variety_name')} for {crop_name}")
            
        except Exception as e:
            logger.error(f"Error saving variety to database: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def _start_extraction_session(self, pdf_files: List[str]):
        """Start a new extraction session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO extraction_sessions (session_id, pdf_files, extraction_status)
                VALUES (?, ?, ?)
            """, (self.session_id, json.dumps([os.path.basename(f) for f in pdf_files]), 'in_progress'))
            conn.commit()
        except Exception as e:
            logger.error(f"Error starting extraction session: {e}")
        finally:
            conn.close()
    
    def _complete_extraction_session(self, total_varieties: int):
        """Complete the extraction session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE extraction_sessions 
                SET total_varieties_extracted = ?, extraction_status = 'completed', completed_at = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (total_varieties, self.session_id))
            conn.commit()
            logger.info(f"Extraction session {self.session_id} completed with {total_varieties} varieties")
        except Exception as e:
            logger.error(f"Error completing extraction session: {e}")
        finally:
            conn.close()
    
    def get_extraction_summary(self) -> Dict[str, Any]:
        """Get summary of extraction results."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get crop counts
            cursor.execute("SELECT COUNT(*) FROM crops")
            total_crops = cursor.fetchone()[0]
            
            # Get variety counts
            cursor.execute("SELECT COUNT(*) FROM varieties")
            total_varieties = cursor.fetchone()[0]
            
            # Get varieties by crop
            cursor.execute("""
                SELECT c.crop_name, COUNT(v.id) as variety_count
                FROM crops c
                LEFT JOIN varieties v ON c.id = v.crop_id
                GROUP BY c.crop_name
                ORDER BY variety_count DESC
            """)
            varieties_by_crop = dict(cursor.fetchall())
            
            # Get extraction sessions
            cursor.execute("""
                SELECT session_id, total_varieties_extracted, extraction_status, started_at
                FROM extraction_sessions
                ORDER BY started_at DESC
                LIMIT 5
            """)
            recent_sessions = cursor.fetchall()
            
            return {
                "total_crops": total_crops,
                "total_varieties": total_varieties,
                "varieties_by_crop": varieties_by_crop,
                "recent_sessions": recent_sessions
            }
            
        except Exception as e:
            logger.error(f"Error getting extraction summary: {e}")
            return {}
        finally:
            conn.close()


def main():
    """Main function to run varieties extraction."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract crop varieties from agricultural PDFs')
    parser.add_argument('--pdf-dir', default='data/pdfs', help='Directory containing PDFs')
    parser.add_argument('--db-path', default='data/agricultural_documents.db', help='Database path')
    parser.add_argument('--openai-key', help='OpenAI API key')
    
    args = parser.parse_args()
    
    # Initialize parser
    parser_instance = ComprehensiveVarietiesParser(
        pdf_directory=args.pdf_dir,
        db_path=args.db_path,
        openai_api_key=args.openai_key
    )
    
    # Run extraction
    print("🚀 Starting comprehensive varieties extraction...")
    results = parser_instance.extract_from_all_pdfs()
    
    if results['success']:
        print(f"✅ Extraction completed successfully!")
        print(f"📊 Session ID: {results['session_id']}")
        print(f"📄 PDFs processed: {results['total_pdfs']}")
        print(f"🌾 Total varieties extracted: {results['total_varieties']}")
        
        # Show summary
        summary = parser_instance.get_extraction_summary()
        print(f"\n📈 Database Summary:")
        print(f"   Total crops: {summary.get('total_crops', 0)}")
        print(f"   Total varieties: {summary.get('total_varieties', 0)}")
        
        if summary.get('varieties_by_crop'):
            print(f"\n🌱 Varieties by crop:")
            for crop, count in list(summary['varieties_by_crop'].items())[:10]:
                print(f"   {crop}: {count} varieties")
    else:
        print(f"❌ Extraction failed: {results.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
