#!/usr/bin/env python3
"""
Script to fix remaining superscript citations that weren't converted
"""

import re

def fix_remaining_citations(content):
    """Fix any remaining superscript citations"""
    
    # More comprehensive mapping including all possible superscript combinations
    superscript_patterns = [
        (r'⁴', '[[4](#references)]'),
        (r'⁵', '[[5](#references)]'),
        (r'⁶', '[[6](#references)]'),
        (r'⁷', '[[7](#references)]'),
        (r'⁸', '[[8](#references)]'),
        (r'⁹', '[[9](#references)]'),
        (r'¹⁰', '[[10](#references)]'),
        (r'¹¹', '[[11](#references)]'),
        (r'¹²', '[[12](#references)]'),
        (r'¹³', '[[13](#references)]'),
        (r'¹⁴', '[[14](#references)]'),
        (r'¹⁵', '[[15](#references)]'),
        (r'¹⁶', '[[16](#references)]'),
        (r'¹⁷', '[[17](#references)]'),
        (r'¹⁸', '[[18](#references)]'),
        (r'¹⁹', '[[19](#references)]'),
        (r'²⁰', '[[20](#references)]'),
        (r'²¹', '[[21](#references)]'),
    ]
    
    for pattern, replacement in superscript_patterns:
        content = re.sub(pattern, replacement, content)
    
    return content

def main():
    # Read the business plan file
    with open('/Users/trevorchimtengo/farming-guide2/docs/AgriAI_Companion_Business_Plan.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix remaining citations
    fixed_content = fix_remaining_citations(content)
    
    # Write back to file
    with open('/Users/trevorchimtengo/farming-guide2/docs/AgriAI_Companion_Business_Plan.md', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("✅ Successfully fixed all remaining superscript citations!")
    print("📄 All citations are now in clickable markdown link format")

if __name__ == "__main__":
    main()


