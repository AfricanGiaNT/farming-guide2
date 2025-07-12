"""
Week 4 PDF Processing Tests - Agricultural Advisor Bot
Testing incremental development of PDF knowledge integration.
"""

import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock
from scripts.data_pipeline.pdf_processor import PDFProcessor
from scripts.data_pipeline.text_chunker import TextChunker
from scripts.data_pipeline.embedding_generator import EmbeddingGenerator
from scripts.data_pipeline.vector_database import VectorDatabase
from scripts.data_pipeline.semantic_search import SemanticSearch


class TestWeek4PDFProcessing(unittest.TestCase):
    """Test suite for Week 4 PDF processing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_data_dir = "test_data"
        os.makedirs(self.test_data_dir, exist_ok=True)
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up test files
        if os.path.exists(self.test_data_dir):
            import shutil
            shutil.rmtree(self.test_data_dir)
    
    def test_pdf_processor_initialization(self):
        """Test that PDFProcessor initializes correctly."""
        processor = PDFProcessor()
        self.assertIsNotNone(processor)
        self.assertTrue(hasattr(processor, 'extract_text_from_pdf'))
    
    def test_pdf_text_extraction_file_not_found(self):
        """Test PDF text extraction with non-existent file."""
        processor = PDFProcessor()
        
        # Test with non-existent file
        with self.assertRaises(FileNotFoundError):
            processor.extract_text_from_pdf("non_existent_file.pdf")
    
    def test_pdf_text_extraction_invalid_format(self):
        """Test PDF text extraction with invalid file format."""
        processor = PDFProcessor()
        
        # Create a dummy non-PDF file
        dummy_file = os.path.join(self.test_data_dir, "text_file.txt")
        with open(dummy_file, 'w') as f:
            f.write("This is not a PDF file")
        
        # Test with non-PDF file
        with self.assertRaises(ValueError):
            processor.extract_text_from_pdf(dummy_file)
    
    def test_text_chunker_initialization(self):
        """Test TextChunker initialization."""
        # Mock tiktoken to avoid network calls
        with patch('scripts.data_pipeline.text_chunker.tiktoken.get_encoding') as mock_encoding:
            mock_encoder = MagicMock()
            mock_encoder.encode.return_value = [1, 2, 3, 4, 5]
            mock_encoder.decode.return_value = "test text"
            mock_encoding.return_value = mock_encoder
            
            chunker = TextChunker()
            self.assertIsNotNone(chunker)
            self.assertTrue(hasattr(chunker, 'chunk_text'))
    
    def test_text_chunking_functionality_simple(self):
        """Test text chunking with simple mock approach."""
        # Mock tiktoken completely to avoid any chunking logic issues
        with patch('scripts.data_pipeline.text_chunker.tiktoken.get_encoding') as mock_encoding:
            mock_encoder = MagicMock()
            # Mock to return a small number of tokens to avoid infinite loops
            mock_encoder.encode.return_value = [1, 2, 3, 4, 5]  # Only 5 tokens
            mock_encoder.decode.return_value = "Short test text"
            mock_encoding.return_value = mock_encoder
            
            chunker = TextChunker(chunk_size=10, overlap=2)  # Small chunks
            text = "Short test text"
            
            # Test chunking
            chunks = chunker.chunk_text(text)
            self.assertIsInstance(chunks, list)
            self.assertEqual(len(chunks), 1)  # Should be 1 chunk since text is short
            
            # Verify chunk structure
            chunk = chunks[0]
            self.assertIn('text', chunk)
            self.assertIn('chunk_id', chunk)
            self.assertIn('token_count', chunk)
            self.assertEqual(chunk['text'], "Short test text")
    
    def test_text_chunking_empty_text(self):
        """Test text chunking with empty text."""
        # Mock tiktoken to avoid network calls
        with patch('scripts.data_pipeline.text_chunker.tiktoken.get_encoding') as mock_encoding:
            mock_encoder = MagicMock()
            mock_encoder.encode.return_value = []
            mock_encoder.decode.return_value = ""
            mock_encoding.return_value = mock_encoder
            
            chunker = TextChunker(chunk_size=1000, overlap=200)
            empty_text = ""
            chunks = chunker.chunk_text(empty_text)
            
            self.assertEqual(len(chunks), 0)
    
    def test_embedding_generator_initialization(self):
        """Test EmbeddingGenerator initialization."""
        generator = EmbeddingGenerator()
        self.assertIsNotNone(generator)
        self.assertTrue(hasattr(generator, 'generate_embeddings'))
    
    def test_vector_database_initialization(self):
        """Test VectorDatabase initialization."""
        db = VectorDatabase(dimension=1536)  # OpenAI embedding dimension
        self.assertIsNotNone(db)
        self.assertTrue(hasattr(db, 'add_vectors'))
        self.assertTrue(hasattr(db, 'search'))
    
    def test_semantic_search_initialization(self):
        """Test SemanticSearch initialization."""
        # Mock tiktoken to avoid network calls in SemanticSearch initialization
        with patch('scripts.data_pipeline.text_chunker.tiktoken.get_encoding') as mock_encoding:
            mock_encoder = MagicMock()
            mock_encoder.encode.return_value = [1, 2, 3, 4, 5]
            mock_encoder.decode.return_value = "test text"
            mock_encoding.return_value = mock_encoder
            
            search = SemanticSearch()
            self.assertIsNotNone(search)
            self.assertTrue(hasattr(search, 'search_documents'))


class TestWeek4Integration(unittest.TestCase):
    """Integration tests for Week 4 PDF knowledge system."""
    
    def test_embedding_generation_mock(self):
        """Test embedding generation with mock data."""
        generator = EmbeddingGenerator()
        
        # Mock the OpenAI API call
        with patch.object(generator, '_call_embedding_api') as mock_api:
            mock_api.return_value = [[0.1, 0.2, 0.3] * 512]  # Mock 1536-dim embedding
            
            test_texts = ["Test agricultural text about maize cultivation"]
            embeddings = generator.generate_embeddings(test_texts)
            
            self.assertEqual(len(embeddings), 1)
            self.assertEqual(len(embeddings[0]), 1536)
    
    def test_vector_database_operations(self):
        """Test vector database add and search operations."""
        db = VectorDatabase(dimension=3)  # Small dimension for testing
        
        # Test adding vectors
        test_embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        test_chunks = [
            {'text': 'Test chunk 1', 'metadata': {'source': 'test1'}},
            {'text': 'Test chunk 2', 'metadata': {'source': 'test2'}}
        ]
        
        success = db.add_vectors(test_embeddings, test_chunks)
        self.assertTrue(success)
        
        # Test search
        query_embedding = [0.1, 0.2, 0.3]
        results = db.search(query_embedding, top_k=2, threshold=0.0)
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
    
    def test_semantic_search_database_status(self):
        """Test semantic search database status."""
        # Mock tiktoken to avoid network calls
        with patch('scripts.data_pipeline.text_chunker.tiktoken.get_encoding') as mock_encoding:
            mock_encoder = MagicMock()
            mock_encoder.encode.return_value = [1, 2, 3, 4, 5]
            mock_encoder.decode.return_value = "test text"
            mock_encoding.return_value = mock_encoder
            
            search = SemanticSearch()
            
            status = search.get_database_status()
            self.assertIsInstance(status, dict)
            self.assertIn('total_vectors', status)
            self.assertIn('dimension', status)
            self.assertIn('embedding_model', status)


if __name__ == '__main__':
    unittest.main() 