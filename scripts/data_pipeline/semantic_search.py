"""
Semantic Search module that orchestrates PDF processing and vector search.
Week 4 implementation for Agricultural Advisor Bot.
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from scripts.utils.logger import logger
from .pdf_processor import PDFProcessor
from .text_chunker import TextChunker
from .embedding_generator import EmbeddingGenerator
from .vector_database import VectorDatabase


class SemanticSearch:
    """
    Semantic search system for agricultural documents.
    Coordinates PDF processing, embedding generation, and vector search.
    """
    
    def __init__(self, 
                 storage_path: str = "data/vector_db",
                 chunk_size: int = 1000,
                 overlap: int = 200,
                 embedding_model: str = "text-embedding-ada-002"):
        """
        Initialize the semantic search system.
        
        Args:
            storage_path: Path to store vector database
            chunk_size: Size of text chunks for embedding
            overlap: Overlap between chunks
            embedding_model: OpenAI embedding model to use
        """
        self.storage_path = storage_path
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.embedding_model = embedding_model
        
        # Initialize components
        self.pdf_processor = PDFProcessor()
        self.text_chunker = TextChunker(chunk_size=chunk_size, overlap=overlap)
        self.embedding_generator = EmbeddingGenerator(model=embedding_model)
        
        # Get embedding dimension
        embedding_dim = self.embedding_generator.get_embedding_dimension()
        self.vector_db = VectorDatabase(dimension=embedding_dim, storage_path=storage_path)
        
        # Try to load existing index
        self.vector_db.load_index()
        
        logger.info("SemanticSearch initialized successfully")
    
    def process_pdf_documents(self, pdf_paths: List[str], force_reprocess: bool = False) -> bool:
        """
        Process PDF documents and add them to the vector database.
        
        Args:
            pdf_paths: List of PDF file paths to process
            force_reprocess: Whether to reprocess documents that already exist
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate PDF files
            valid_pdfs = self.pdf_processor.validate_pdf_files(pdf_paths)
            if not valid_pdfs:
                logger.warning("No valid PDF files found")
                return False
            
            # Check which documents need processing
            processed_docs = self._get_processed_documents()
            docs_to_process = []
            
            for pdf_path in valid_pdfs:
                doc_name = os.path.basename(pdf_path)
                if force_reprocess or doc_name not in processed_docs:
                    docs_to_process.append(pdf_path)
                else:
                    logger.info(f"Skipping already processed document: {doc_name}")
            
            if not docs_to_process:
                logger.info("All documents already processed")
                return True
            
            # Extract text from PDFs
            logger.info(f"Processing {len(docs_to_process)} PDF documents...")
            documents = self.pdf_processor.extract_text_from_multiple_pdfs(docs_to_process)
            
            # Filter successful extractions
            successful_docs = {path: text for path, text in documents.items() if text}
            
            if not successful_docs:
                logger.error("No text extracted from any PDF")
                return False
            
            # Chunk the documents
            logger.info("Chunking documents...")
            doc_chunks = []
            for pdf_path, text in successful_docs.items():
                doc_name = os.path.basename(pdf_path)
                metadata = {
                    'source_document': doc_name,
                    'file_path': pdf_path,
                    'document_type': 'agricultural_guide'
                }
                
                chunks = self.text_chunker.chunk_text(text, metadata)
                doc_chunks.extend(chunks)
            
            if not doc_chunks:
                logger.error("No chunks generated from documents")
                return False
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(doc_chunks)} chunks...")
            texts = [chunk['text'] for chunk in doc_chunks]
            embeddings = self.embedding_generator.generate_embeddings(texts)
            
            if not embeddings:
                logger.error("No embeddings generated")
                return False
            
            # Add to vector database
            logger.info("Adding vectors to database...")
            success = self.vector_db.add_vectors(embeddings, doc_chunks)
            
            if success:
                # Save the updated index
                self.vector_db.save_index()
                logger.info(f"Successfully processed and indexed {len(successful_docs)} documents")
                return True
            else:
                logger.error("Failed to add vectors to database")
                return False
                
        except Exception as e:
            logger.error(f"Error processing PDF documents: {str(e)}")
            return False
    
    def search_documents(self, 
                        query: str, 
                        top_k: int = 5,
                        threshold: float = 0.7,
                        filter_by_document: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for relevant document chunks based on a query.
        
        Args:
            query: Search query
            top_k: Number of results to return
            threshold: Minimum similarity threshold
            filter_by_document: Optional document name to filter by
            
        Returns:
            List of search results with metadata and scores
        """
        if not query or not query.strip():
            logger.warning("Empty query provided")
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_generator.generate_query_embedding(query)
            if not query_embedding:
                logger.error("Failed to generate query embedding")
                return []
            
            # Search vector database
            results = self.vector_db.search(query_embedding, top_k, threshold)
            
            # Filter by document if specified
            if filter_by_document:
                results = [r for r in results if r.get('source_document') == filter_by_document]
            
            # Enhance results with additional context
            enhanced_results = self._enhance_search_results(results, query)
            
            logger.info(f"Search for '{query}' returned {len(enhanced_results)} results")
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []
    
    def get_document_summary(self, document_name: str) -> Dict[str, Any]:
        """
        Get a summary of a specific document in the database.
        
        Args:
            document_name: Name of the document
            
        Returns:
            Dictionary with document summary
        """
        try:
            # Get all chunks for this document
            doc_chunks = []
            for chunk in self.vector_db.metadata:
                if chunk.get('metadata', {}).get('source_document') == document_name:
                    doc_chunks.append(chunk)
            
            if not doc_chunks:
                return {}
            
            # Calculate statistics
            total_tokens = sum(chunk.get('token_count', 0) for chunk in doc_chunks)
            chunk_count = len(doc_chunks)
            
            # Get sample text
            sample_text = doc_chunks[0].get('text', '')[:200] + '...' if doc_chunks else ''
            
            summary = {
                'document_name': document_name,
                'chunk_count': chunk_count,
                'total_tokens': total_tokens,
                'sample_text': sample_text,
                'file_path': doc_chunks[0].get('metadata', {}).get('file_path', ''),
                'document_type': doc_chunks[0].get('metadata', {}).get('document_type', '')
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting document summary: {str(e)}")
            return {}
    
    def get_database_status(self) -> Dict[str, Any]:
        """
        Get the current status of the vector database.
        
        Returns:
            Dictionary with database status
        """
        try:
            stats = self.vector_db.get_database_stats()
            
            # Add component information
            stats.update({
                'chunk_size': self.chunk_size,
                'overlap': self.overlap,
                'embedding_model': self.embedding_model,
                'embedding_cache_size': self.embedding_generator.get_cache_size(),
                'processed_documents': self._get_processed_documents()
            })
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting database status: {str(e)}")
            return {}
    
    def _get_processed_documents(self) -> List[str]:
        """
        Get list of already processed documents.
        
        Returns:
            List of processed document names
        """
        try:
            documents = set()
            for chunk in self.vector_db.metadata:
                doc_name = chunk.get('metadata', {}).get('source_document', '')
                if doc_name:
                    documents.add(doc_name)
            return list(documents)
            
        except Exception as e:
            logger.error(f"Error getting processed documents: {str(e)}")
            return []
    
    def _enhance_search_results(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """
        Enhance search results with additional context and processing.
        
        Args:
            results: Raw search results
            query: Original search query
            
        Returns:
            Enhanced search results
        """
        enhanced_results = []
        
        for result in results:
            enhanced_result = result.copy()
            
            # Add query context
            enhanced_result['query'] = query
            
            # Add text preview with highlighting (simple approach)
            text = result.get('text', '')
            if len(text) > 300:
                # Try to find relevant portion
                query_words = query.lower().split()
                best_position = 0
                best_score = 0
                
                for word in query_words:
                    pos = text.lower().find(word)
                    if pos != -1:
                        score = 1
                        if pos > best_score:
                            best_score = score
                            best_position = max(0, pos - 100)
                
                if best_position > 0:
                    enhanced_result['text_preview'] = '...' + text[best_position:best_position + 250] + '...'
                else:
                    enhanced_result['text_preview'] = text[:250] + '...'
            else:
                enhanced_result['text_preview'] = text
            
            # Add relevance category
            score = result.get('score', 0)
            if score > 0.9:
                enhanced_result['relevance'] = 'high'
            elif score > 0.8:
                enhanced_result['relevance'] = 'medium'
            else:
                enhanced_result['relevance'] = 'low'
            
            enhanced_results.append(enhanced_result)
        
        return enhanced_results
    
    def clear_database(self):
        """Clear all data from the vector database."""
        try:
            self.vector_db.clear_database()
            self.embedding_generator.clear_cache()
            logger.info("Database and cache cleared")
        except Exception as e:
            logger.error(f"Error clearing database: {str(e)}")
    
    def rebuild_database(self, pdf_paths: List[str]) -> bool:
        """
        Rebuild the entire database from scratch.
        
        Args:
            pdf_paths: List of PDF files to process
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Rebuilding database from scratch...")
            
            # Clear existing database
            self.clear_database()
            
            # Process all documents
            success = self.process_pdf_documents(pdf_paths, force_reprocess=True)
            
            if success:
                logger.info("Database rebuild completed successfully")
            else:
                logger.error("Database rebuild failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Error rebuilding database: {str(e)}")
            return False 