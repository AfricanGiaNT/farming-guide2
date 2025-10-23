#!/usr/bin/env python3
"""
Detailed Maize Variety Extraction
Focus on Tables 17a and 17b specifically
"""

import pdfplumber
import re
from supabase import create_client, Client

# Configuration
SUPABASE_URL = "https://itcsdacjopedjcyhqyki.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0Y3NkYWNqb3BlZGpjeWhxeWtpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODg1MDUsImV4cCI6MjA3NjU2NDUwNX0.659SJ6mcDpeyq7mtduMneh-h9gz3vSFA-2F-oVlVJmk"

PDF_PATH = r"C:\Users\Administratior\Downloads\agriculture-resourcs\agriculture-resourcs\Guide to Agriculture Production in Malawi 2021.pdf"

def examine_maize_tables():
    """Examine Tables 17a and 17b in detail"""
    
    print("=" * 80)
    print("DETAILED EXAMINATION OF MAIZE TABLES 17a AND 17b")
    print("=" * 80)
    
    with pdfplumber.open(PDF_PATH) as pdf:
        # Look around pages 156-167 where maize tables should be
        for page_num in range(155, 170):
            if page_num >= len(pdf.pages):
                break
                
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            
            # Check if this page mentions Table 17a or 17b
            if "table 17" in text.lower() or "17a" in text.lower() or "17b" in text.lower():
                print(f"\n{'='*60}")
                print(f"PAGE {page_num + 1} - Found Table 17 reference")
                print(f"{'='*60}")
                
                # Extract text to see table references
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if "table 17" in line.lower() or "17a" in line.lower() or "17b" in line.lower():
                        print(f"Line {i+1}: {line.strip()}")
                
                # Extract all tables on this page
                tables = page.extract_tables()
                print(f"\nTables found on page {page_num + 1}: {len(tables)}")
                
                for table_idx, table in enumerate(tables):
                    if not table:
                        continue
                    
                    print(f"\nTable {table_idx + 1}:")
                    print(f"Rows: {len(table)}")
                    
                    # Show first few rows to understand structure
                    for row_idx, row in enumerate(table[:10]):  # Show first 10 rows
                        if row:
                            print(f"  Row {row_idx + 1}: {row}")
                    
                    if len(table) > 10:
                        print(f"  ... and {len(table) - 10} more rows")
                
                print(f"\nFull text preview:")
                print(text[:1000] + "..." if len(text) > 1000 else text)

def extract_maize_varieties_detailed():
    """Extract maize varieties with detailed table analysis"""
    
    print("\n" + "=" * 80)
    print("DETAILED MAIZE VARIETY EXTRACTION")
    print("=" * 80)
    
    varieties = set()
    
    with pdfplumber.open(PDF_PATH) as pdf:
        # Focus on maize section pages
        for page_num in range(155, 170):
            if page_num >= len(pdf.pages):
                break
                
            page = pdf.pages[page_num]
            text = page.extract_text() or ""
            
            # Only process pages with maize content
            if "maize" not in text.lower():
                continue
            
            print(f"\nPage {page_num + 1}: Processing maize tables")
            
            tables = page.extract_tables()
            
            for table_idx, table in enumerate(tables):
                if not table or len(table) < 2:
                    continue
                
                print(f"\n  Table {table_idx + 1}: {len(table)} rows")
                
                # Look for variety names in all columns
                for row_idx, row in enumerate(table[1:]):  # Skip header
                    if not row:
                        continue
                    
                    for cell_idx, cell in enumerate(row):
                        if cell:
                            cell_str = str(cell).strip()
                            
                            # Handle multi-variety cells
                            potential_varieties = re.split(r'[,;\n]', cell_str)
                            
                            for v in potential_varieties:
                                v = v.strip()
                                
                                # More lenient validation for maize varieties
                                if (len(v) >= 2 and len(v) <= 50 and 
                                    re.search(r'[A-Za-z]', v) and
                                    not re.search(r'^\d+$|^\d+\)$|and\s+\d+|kg|ha|t|%|mm|cm|USD|total|average|table|figure', v, re.IGNORECASE)):
                                    
                                    varieties.add(v)
                                    print(f"    Found variety: '{v}' (Row {row_idx + 2}, Col {cell_idx + 1})")
    
    print(f"\nTotal maize varieties found: {len(varieties)}")
    if varieties:
        print("All varieties:")
        for v in sorted(varieties):
            print(f"  - {v}")
    
    return varieties

def main():
    # First examine the tables in detail
    examine_maize_tables()
    
    # Then extract varieties with detailed analysis
    varieties = extract_maize_varieties_detailed()
    
    print(f"\n{'='*80}")
    print("MAIZE VARIETY EXTRACTION COMPLETE")
    print(f"Found {len(varieties)} varieties")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()


