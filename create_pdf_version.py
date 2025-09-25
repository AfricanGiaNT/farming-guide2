#!/usr/bin/env python3
"""
Script to create a PDF-friendly version of the business plan
"""

import re

def clean_for_pdf(content):
    """Remove all Unicode characters that might cause PDF conversion issues"""
    
    # Remove all emojis and special Unicode characters
    content = re.sub(r'[^\x00-\x7F]+', '', content)
    
    # Replace common symbols with text equivalents
    replacements = {
        '✓': 'YES',
        '❌': 'NO', 
        '→': '->',
        '•': '-',
        '—': '--',
        '–': '-',
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
        '…': '...',
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    return content

def main():
    # Read the business plan file
    with open('/Users/trevorchimtengo/farming-guide2/docs/AgriAI_Companion_Business_Plan.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Clean for PDF
    clean_content = clean_for_pdf(content)
    
    # Write clean version
    with open('/Users/trevorchimtengo/farming-guide2/docs/AgriAI_Companion_Business_Plan_PDF.md', 'w', encoding='utf-8') as f:
        f.write(clean_content)
    
    print("✅ Successfully created PDF-friendly version!")
    print("📄 All Unicode characters removed for PDF compatibility")

if __name__ == "__main__":
    main()


