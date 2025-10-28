#!/usr/bin/env python3
"""
Crop Section Analyzer
Analyzes a specific crop section to find variety tables and structure
"""

import pdfplumber
import re
import sys
from typing import List, Dict, Tuple

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

class CropSectionAnalyzer:
    """
    Analyzes crop sections to identify variety tables and structure
    """
    
    def __init__(self):
        self.pdf_path = PDF_PATH
        
        # Crop sections with page ranges
        self.crop_sections = {
            "rice": {"pages": (168, 175), "keywords": ["rice", "oryza sativa"]},
            "groundnut": {"pages": (189, 200), "keywords": ["groundnut", "arachis hypogaea"]},
            "cassava": {"pages": (219, 230), "keywords": ["cassava", "manihot esculenta"]},
            "potato": {"pages": (226, 240), "keywords": ["potato", "solanum tuberosum"]},
            "tobacco": {"pages": (231, 270), "keywords": ["tobacco", "nicotiana"]},
            "soybean": {"pages": (195, 210), "keywords": ["soybean", "soyabean", "glycine max"]},
            "sweet potato": {"pages": (224, 235), "keywords": ["sweet potato", "sweetpotato", "ipomoea batatas"]},
            "sunflower": {"pages": (214, 225), "keywords": ["sunflower", "helianthus annuus"]},
            "sesame": {"pages": (216, 225), "keywords": ["sesame", "sesamum indicum"]},
        }
    
    def analyze_crop(self, crop_name: str) -> Dict:
        """Analyze a specific crop section"""
        
        if crop_name not in self.crop_sections:
            print(f"Crop '{crop_name}' not found in sections")
            return {}
        
        section = self.crop_sections[crop_name]
        start_page, end_page = section["pages"]
        keywords = section["keywords"]
        
        print(f"=" * 80)
        print(f"ANALYZING CROP: {crop_name.upper()}")
        print(f"Pages: {start_page}-{end_page}")
        print(f"Keywords: {', '.join(keywords)}")
        print(f"=" * 80)
        
        analysis = {
            "crop_name": crop_name,
            "pages": (start_page, end_page),
            "variety_tables": [],
            "text_sections": [],
            "potential_varieties": set(),
            "table_references": []
        }
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num in range(start_page - 1, min(end_page, len(pdf.pages))):
                page = pdf.pages[page_num]
                text = page.extract_text() or ""
                
                # Check if this page is about the crop
                is_crop_page = any(keyword in text.lower() for keyword in keywords)
                if not is_crop_page:
                    continue
                
                print(f"\nPage {page_num + 1}: Found {crop_name} content")
                
                # Look for table references
                table_refs = re.findall(r'table\s+\d+[a-z]?', text.lower())
                if table_refs:
                    print(f"  Table references: {table_refs}")
                    analysis["table_references"].extend(table_refs)
                
                # Extract tables
                tables = page.extract_tables()
                print(f"  Tables found: {len(tables)}")
                
                for table_idx, table in enumerate(tables):
                    if not table or len(table) < 2:
                        continue
                    
                    print(f"\n  Table {table_idx + 1}: {len(table)} rows")
                    
                    # Check if this looks like a variety table
                    header_row = table[0]
                    if header_row and any(word in str(header_row).lower() for word in ["variety", "cultivar"]):
                        print(f"    *** VARIETY TABLE FOUND ***")
                        print(f"    Columns: {header_row}")
                        
                        table_info = {
                            "page": page_num + 1,
                            "table_index": table_idx + 1,
                            "rows": len(table),
                            "columns": header_row,
                            "varieties": []
                        }
                        
                        # Extract potential variety names
                        for row_idx, row in enumerate(table[1:], 1):
                            if row and len(row) > 0:
                                variety_cell = str(row[0]).strip()
                                if variety_cell and len(variety_cell) > 2:
                                    table_info["varieties"].append(variety_cell)
                        
                        analysis["variety_tables"].append(table_info)
                        print(f"    Potential varieties: {len(table_info['varieties'])}")
                        if table_info["varieties"]:
                            print(f"    Sample: {table_info['varieties'][:5]}")
                    
                    # Show first few rows for analysis
                    print(f"    First 3 rows:")
                    for row_idx, row in enumerate(table[:3]):
                        if row:
                            print(f"      Row {row_idx + 1}: {row}")
                
                # Look for variety text sections
                variety_patterns = [
                    r'(?:varieties?|cultivars?)\s+(?:include|are|such as|available)[\s:]+([^.]+)',
                    r'recommended\s+varieties?[\s:]+([^.]+)',
                    r'released\s+varieties?[\s:]+([^.]+)',
                ]
                
                for pattern in variety_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        analysis["text_sections"].append({
                            "page": page_num + 1,
                            "pattern": pattern,
                            "content": match.strip()
                        })
                        print(f"  Text section found: {match.strip()[:50]}...")
        
        return analysis
    
    def generate_extraction_plan(self, analysis: Dict) -> str:
        """Generate extraction plan based on analysis"""
        
        if not analysis:
            return "No analysis data available"
        
        plan = f"\n{'='*80}\n"
        plan += f"EXTRACTION PLAN FOR {analysis['crop_name'].upper()}\n"
        plan += f"{'='*80}\n"
        
        plan += f"\nPages to process: {analysis['pages'][0]}-{analysis['pages'][1]}\n"
        
        if analysis["variety_tables"]:
            plan += f"\nVARIETY TABLES FOUND: {len(analysis['variety_tables'])}\n"
            for i, table in enumerate(analysis["variety_tables"], 1):
                plan += f"\nTable {i}:\n"
                plan += f"  Page: {table['page']}\n"
                plan += f"  Rows: {table['rows']}\n"
                plan += f"  Columns: {table['columns']}\n"
                plan += f"  Varieties: {len(table['varieties'])}\n"
        else:
            plan += f"\nNO VARIETY TABLES FOUND\n"
            plan += f"Will need to extract from text sections\n"
        
        if analysis["text_sections"]:
            plan += f"\nTEXT SECTIONS: {len(analysis['text_sections'])}\n"
            for section in analysis["text_sections"][:3]:  # Show first 3
                plan += f"  Page {section['page']}: {section['content'][:50]}...\n"
        
        plan += f"\nNEXT STEPS:\n"
        plan += f"1. Create structured_{analysis['crop_name']}_extractor.py\n"
        plan += f"2. Configure page ranges: {analysis['pages'][0]}-{analysis['pages'][1]}\n"
        if analysis["variety_tables"]:
            plan += f"3. Focus on variety tables on pages: {', '.join(set(str(t['page']) for t in analysis['variety_tables']))}\n"
        plan += f"4. Test extraction in preview mode\n"
        plan += f"5. Execute full extraction\n"
        
        return plan

def main():
    if len(sys.argv) < 3 or sys.argv[1] != "--crop":
        print("Usage: python scripts/analyze_crop_section.py --crop <crop_name>")
        print("\nAvailable crops:")
        analyzer = CropSectionAnalyzer()
        for crop in analyzer.crop_sections.keys():
            print(f"  - {crop}")
        return
    
    crop_name = sys.argv[2]
    analyzer = CropSectionAnalyzer()
    
    # Analyze the crop
    analysis = analyzer.analyze_crop(crop_name)
    
    if analysis:
        # Generate extraction plan
        plan = analyzer.generate_extraction_plan(analysis)
        print(plan)
        
        # Save analysis to file
        with open(f"analysis_{crop_name}.txt", "w") as f:
            f.write(plan)
        print(f"\nAnalysis saved to: analysis_{crop_name}.txt")

if __name__ == "__main__":
    main()



