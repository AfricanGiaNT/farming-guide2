"""
Text Chunking module for preparing documents for vector embeddings.
Week 4 implementation for Agricultural Advisor Bot.
"""

import tiktoken
from typing import List, Dict, Any, Optional
from scripts.utils.logger import logger


class TextChunker:
    """
    Handles text chunking for optimal embedding generation.
    Designed for agricultural documents with technical content.
    """
    
    def __init__(self, 
                 chunk_size: int = 1000,
                 overlap: int = 200,
                 encoding_name: str = "cl100k_base"):
        """
        Initialize the text chunker.
        
        Args:
            chunk_size: Maximum number of tokens per chunk
            overlap: Number of tokens to overlap between chunks
            encoding_name: Tiktoken encoding to use for token counting
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.encoding_name = encoding_name
        
        try:
            self.encoding = tiktoken.get_encoding(encoding_name)
            logger.info(f"TextChunker initialized with chunk_size={chunk_size}, overlap={overlap}")
        except Exception as e:
            logger.error(f"Failed to initialize tiktoken encoding: {e}")
            raise
    
    def chunk_text(self, text: str, metadata: Optional[Dict[str, Any]] = None, progress_callback=None) -> List[Dict[str, Any]]:
        """
        Split text into chunks suitable for embedding.
        
        Args:
            text: The text to chunk
            metadata: Optional metadata to include with each chunk
            progress_callback: Optional callback function for progress updates
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for chunking")
            return []
        
        try:
            # Tokenize the text
            tokens = self.encoding.encode(text)
            total_tokens = len(tokens)
            
            # If text is shorter than chunk size, return as single chunk
            if total_tokens <= self.chunk_size:
                return [{
                    'text': text,
                    'chunk_id': 0,
                    'start_token': 0,
                    'end_token': total_tokens,
                    'token_count': total_tokens,
                    'metadata': metadata or {}
                }]
            
            # Calculate maximum possible chunks (safety limit)
            max_chunks = (total_tokens // (self.chunk_size - self.overlap)) + 10
            
            # Create chunks with overlap
            chunks = []
            start = 0
            chunk_id = 0
            
            while start < total_tokens and chunk_id < max_chunks:
                # Calculate end position
                end = min(start + self.chunk_size, total_tokens)
                
                # Extract chunk tokens
                chunk_tokens = tokens[start:end]
                
                # Decode back to text
                chunk_text = self.encoding.decode(chunk_tokens)
                
                # Clean up chunk text
                chunk_text = self._clean_chunk_text(chunk_text)
                
                # Create chunk dictionary
                chunk = {
                    'text': chunk_text,
                    'chunk_id': chunk_id,
                    'start_token': start,
                    'end_token': end,
                    'token_count': len(chunk_tokens),
                    'metadata': metadata or {}
                }
                
                chunks.append(chunk)
                
                # Progress callback (every 10 chunks to avoid spam)
                if progress_callback and (chunk_id % 10 == 0 or chunk_id < 5):
                    progress_pct = (start / total_tokens) * 100
                    progress_callback(chunk_id + 1, len(chunks), progress_pct)
                
                # Move to next chunk with overlap
                # Ensure we always advance at least 1 token to prevent infinite loops
                next_start = end - self.overlap
                if next_start <= start:
                    next_start = start + max(1, self.chunk_size - self.overlap)
                
                start = next_start
                chunk_id += 1
                
                # Additional safety: if we're at the end, break
                if end >= total_tokens:
                    break
            
            # Final progress callback
            if progress_callback:
                progress_callback(len(chunks), len(chunks), 100.0)
            
            # Safety check
            if chunk_id >= max_chunks:
                logger.warning(f"Hit maximum chunk limit ({max_chunks}) - this may indicate an infinite loop")
            
            logger.info(f"Successfully chunked text into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking text: {str(e)}")
            raise
    
    def chunk_documents(self, documents: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Chunk multiple documents.
        
        Args:
            documents: Dictionary mapping document names to text content
            
        Returns:
            List of all chunks from all documents
        """
        all_chunks = []
        
        for doc_name, doc_text in documents.items():
            try:
                # Add document metadata
                doc_metadata = {
                    'source_document': doc_name,
                    'document_type': 'agricultural_guide'
                }
                
                # Chunk the document
                doc_chunks = self.chunk_text(doc_text, doc_metadata)
                
                # Add global chunk IDs
                for i, chunk in enumerate(doc_chunks):
                    chunk['global_chunk_id'] = len(all_chunks) + i
                
                all_chunks.extend(doc_chunks)
                logger.info(f"Successfully chunked document {doc_name}: {len(doc_chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Error chunking document {doc_name}: {str(e)}")
                continue
        
        return all_chunks
    
    def chunk_by_sentences(self, text: str, max_tokens: int = 1000) -> List[str]:
        """
        Chunk text by sentences while respecting token limits.
        
        Args:
            text: Text to chunk
            max_tokens: Maximum tokens per chunk
            
        Returns:
            List of text chunks
        """
        try:
            # Split into sentences (simple approach)
            sentences = self._split_into_sentences(text)
            
            chunks = []
            current_chunk = []
            current_tokens = 0
            
            for sentence in sentences:
                sentence_tokens = len(self.encoding.encode(sentence))
                
                # If adding this sentence would exceed limit, start new chunk
                if current_tokens + sentence_tokens > max_tokens and current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = [sentence]
                    current_tokens = sentence_tokens
                else:
                    current_chunk.append(sentence)
                    current_tokens += sentence_tokens
            
            # Add final chunk if not empty
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking by sentences: {str(e)}")
            return [text]  # Return original text as fallback
    
    def _clean_chunk_text(self, text: str) -> str:
        """
        Clean chunk text to ensure quality.
        
        Args:
            text: Raw chunk text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
            
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Simple cleanup without complex logic that could hang
        text = text.strip()
        
        # Remove common PDF artifacts
        text = text.replace('\n', ' ')
        text = text.replace('\t', ' ')
        text = text.replace('\r', ' ')
        
        # Remove multiple spaces
        while '  ' in text:
            text = text.replace('  ', ' ')
        
        return text
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using simple heuristics.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting (can be improved with NLTK if needed)
        import re
        
        # Split on sentence endings
        sentences = re.split(r'[.!?]+', text)
        
        # Clean up sentences
        clean_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                clean_sentences.append(sentence)
        
        return clean_sentences
    
    def get_chunk_statistics(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about chunk distribution.
        
        Args:
            chunks: List of chunks
            
        Returns:
            Dictionary with chunk statistics
        """
        if not chunks:
            return {}
        
        token_counts = [chunk['token_count'] for chunk in chunks]
        
        stats = {
            'total_chunks': len(chunks),
            'total_tokens': sum(token_counts),
            'avg_tokens_per_chunk': sum(token_counts) / len(token_counts),
            'min_tokens': min(token_counts),
            'max_tokens': max(token_counts),
            'unique_documents': len(set(chunk['metadata'].get('source_document', '') for chunk in chunks))
        }
        
        return stats 