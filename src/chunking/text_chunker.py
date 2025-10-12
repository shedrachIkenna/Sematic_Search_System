"""
Text Chunking System for Semantic Search Engine 
Breaking text into optimal segments for embedding
"""

from enum import Enum 

class ChunkingStrategy(Enum):
    """DIfferent strategies for chunking text"""
    FIXED_SIZE = "fixed_size"  # fixed character count
    SENTENCE = "sentence"   # sentence-based chunks 
    PARAGRAPH = "paragraph"   # paragraph-based chunks 
    SEMANTIC = "semantic"   # Semantic-bound detection 
    RECURSIVE = "recursive"  # Recursive splitting with fallback 


class TextChunker:
    """
    Handles intelligent text chunking for semantic search 
    Breaks text into optimal segments while preserving context 
    """

    def __init__(self, 
                 chunk_size: int = 500, 
                 chunk_overlap: int = 50,
                 strategy: ChunkingStrategy = ChunkingStrategy.FIXED_SIZE,
                 min_chunk_size: int = 50,
                 respect_sentence_boundary: bool = True
                 ):
        """
        Initialize text chunker with configurations

        Args:
            chunk_size: Targer size for each chunk in characters 
            chunk_overlap: Number of characters to overlap between chunks 
            strategy: Chunking strategy to use 
            min_chunk_size: Minimum chunk size (discard smaller chunks)
            respect_sentence_boundary: Try to break at sentence boundaries 
        """

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy = strategy
        self.min_chunk_size = min_chunk_size
        self.respect_sentence_boundary = respect_sentence_boundary

        self._compile_patterns()

        # Statistics 
        self.stats = {
            'texts_chunked': 0,
            'total_chunks_created': 0,
            'avg_chunk_size': 0,
            'avg_chunks_per_text': 0
        }

        
