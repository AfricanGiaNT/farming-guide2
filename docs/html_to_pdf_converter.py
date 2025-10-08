#!/usr/bin/env python3
"""
Simple HTML to PDF converter using reportlab
"""

import re
from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from html.parser import HTMLParser
import html

class HTMLToPDFParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.content = []
        self.current_text = ""
        self.in_header = False
        self.header_level = 0
        self.in_paragraph = False
        self.in_list = False
        self.in_table = False
        
    def handle_starttag(self, tag, attrs):
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.in_header = True
            self.header_level = int(tag[1])
        elif tag == 'p':
            self.in_paragraph = True
        elif tag in ['ul', 'ol']:
            self.in_list = True
        elif tag == 'br':
            self.current_text += '<br/>'
        elif tag == 'strong' or tag == 'b':
            self.current_text += '<b>'
        elif tag == 'em' or tag == 'i':
            self.current_text += '<i>'
        elif tag == 'table':
            self.in_table = True
            
    def handle_endtag(self, tag):
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            if self.current_text.strip():
                self.content.append(('header', self.header_level, self.current_text.strip()))
                self.current_text = ""
            self.in_header = False
        elif tag == 'p':
            if self.current_text.strip():
                self.content.append(('paragraph', self.current_text.strip()))
                self.current_text = ""
            self.in_paragraph = False
        elif tag in ['ul', 'ol']:
            self.in_list = False
        elif tag == 'strong' or tag == 'b':
            self.current_text += '</b>'
        elif tag == 'em' or tag == 'i':
            self.current_text += '</i>'
        elif tag == 'table':
            self.in_table = False
            
    def handle_data(self, data):
        if not self.in_table:  # Skip table content for now
            cleaned_data = data.strip()
            if cleaned_data:
                self.current_text += cleaned_data + " "

def clean_html_content(html_content):
    """Extract text content from HTML and clean it"""
    # Remove script and style elements
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Parse HTML
    parser = HTMLToPDFParser()
    parser.feed(html_content)
    
    return parser.content

def create_pdf_from_html(html_file_path, output_pdf_path):
    """Convert HTML file to PDF"""
    
    # Read HTML content
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Parse content
    content_items = clean_html_content(html_content)
    
    # Create PDF
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor='black'
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=12,
        spaceBefore=20,
        textColor='black'
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10,
        spaceBefore=15,
        textColor='black'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        textColor='black'
    )
    
    # Build story
    story = []
    
    # Add title
    story.append(Paragraph("Mlangizi wa Ulimi: AI-Powered Farming Guide", title_style))
    story.append(Paragraph("Business Plan for Agricultural Innovation Competition", heading2_style))
    story.append(Spacer(1, 20))
    
    # Process content
    for item in content_items:
        if item[0] == 'header':
            level = item[1]
            text = html.unescape(item[2])
            
            if level == 1:
                story.append(Spacer(1, 12))
                story.append(Paragraph(text, heading1_style))
            elif level == 2:
                story.append(Spacer(1, 8))
                story.append(Paragraph(text, heading2_style))
            else:
                story.append(Spacer(1, 6))
                story.append(Paragraph(text, body_style))
                
        elif item[0] == 'paragraph':
            text = html.unescape(item[1])
            # Clean up text
            text = re.sub(r'\s+', ' ', text)
            if text.strip():
                story.append(Paragraph(text, body_style))
    
    # Build PDF
    try:
        doc.build(story)
        print(f"PDF created successfully: {output_pdf_path}")
        return True
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return False

if __name__ == "__main__":
    html_file = Path("AgriAI_Companion_Business_Plan.html")
    pdf_file = "Mlangizi wa Ulimi Final.pdf"
    
    if html_file.exists():
        success = create_pdf_from_html(str(html_file), pdf_file)
        if success:
            print(f"Conversion completed: {pdf_file}")
        else:
            print("Conversion failed")
    else:
        print(f"HTML file not found: {html_file}")
