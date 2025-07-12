"""
PDF Processing module for extracting text from agricultural PDFs.
Week 4 implementation for Agricultural Advisor Bot.
"""

import PyPDF2
import os
from typing import List, Optional, Dict, Any
from scripts.utils.logger import logger


class PDFProcessor:
    """
    Handles PDF text extraction for agricultural documents.
    Optimized for processing farming guides and research papers.
    """
    
    def __init__(self):
        """Initialize the PDF processor."""
        self.supported_formats = ['.pdf']
        logger.info("PDFProcessor initialized successfully")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text content from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content as string
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If file is not a valid PDF
            Exception: For other PDF processing errors
        """
        try:
            # Validate file existence
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            # Validate file format
            if not pdf_path.lower().endswith('.pdf'):
                raise ValueError(f"File must be a PDF: {pdf_path}")
            
            # Extract text using PyPDF2
            text_content = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Check if PDF is encrypted
                if pdf_reader.is_encrypted:
                    logger.warning(f"PDF is encrypted: {pdf_path}")
                    try:
                        pdf_reader.decrypt("")  # Try with empty password
                    except Exception:
                        raise ValueError(f"Cannot decrypt PDF: {pdf_path}")
                
                # Extract text from all pages
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    text_content += page_text + "\n"
            
            # Clean up extracted text
            text_content = self._clean_text(text_content)
            
            logger.info(f"Successfully extracted {len(text_content)} characters from {pdf_path}")
            return text_content
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {str(e)}")
            raise
    
    def extract_text_from_multiple_pdfs(self, pdf_paths: List[str]) -> Dict[str, str]:
        """
        Extract text from multiple PDF files.
        
        Args:
            pdf_paths: List of PDF file paths
            
        Returns:
            Dictionary mapping file paths to extracted text
        """
        results = {}
        
        for pdf_path in pdf_paths:
            try:
                text = self.extract_text_from_pdf(pdf_path)
                results[pdf_path] = text
                logger.info(f"Successfully processed: {pdf_path}")
            except Exception as e:
                logger.error(f"Failed to process {pdf_path}: {str(e)}")
                results[pdf_path] = ""
        
        return results
    
    def get_pdf_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract metadata from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing PDF metadata
        """
        try:
            metadata = {}
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Basic metadata
                metadata['num_pages'] = len(pdf_reader.pages)
                metadata['is_encrypted'] = pdf_reader.is_encrypted
                metadata['file_size'] = os.path.getsize(pdf_path)
                
                # Document info
                if pdf_reader.metadata:
                    metadata['title'] = pdf_reader.metadata.get('/Title', '')
                    metadata['author'] = pdf_reader.metadata.get('/Author', '')
                    metadata['subject'] = pdf_reader.metadata.get('/Subject', '')
                    metadata['creator'] = pdf_reader.metadata.get('/Creator', '')
                
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {pdf_path}: {str(e)}")
            return {}
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove special characters that might interfere with processing
        text = text.replace('\x00', '')  # Remove null bytes
        text = text.replace('\ufeff', '')  # Remove BOM
        
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text.strip()
    
    def validate_pdf_files(self, pdf_paths: List[str]) -> List[str]:
        """
        Validate a list of PDF files and return valid ones.
        
        Args:
            pdf_paths: List of PDF file paths to validate
            
        Returns:
            List of valid PDF file paths
        """
        valid_files = []
        
        for pdf_path in pdf_paths:
            try:
                if os.path.exists(pdf_path) and pdf_path.lower().endswith('.pdf'):
                    # Try to open and read metadata
                    self.get_pdf_metadata(pdf_path)
                    valid_files.append(pdf_path)
                    logger.info(f"Valid PDF: {pdf_path}")
                else:
                    logger.warning(f"Invalid PDF path: {pdf_path}")
            except Exception as e:
                logger.error(f"PDF validation failed for {pdf_path}: {str(e)}")
        
        return valid_files 