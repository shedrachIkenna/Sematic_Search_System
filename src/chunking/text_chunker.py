"""
Text Chunking System for Semantic Search Engine 
Breaking text into optimal segments for embedding
"""

from enum import Enum 
import re 
from typing import Optional, Dict, List, Any

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

    def _compile_patterns(self):
        """Compile regex patterns for text analysis"""

        # Sentence endings (Period, question mark, exclamation)
        self.sentence_pattern = re.compile(r'[.!?]+[\s\n]+')

        # Paragraphs breaks (double newline)
        self.paragraph_pattern = re.compile(r'\n\n+')

        # Common abbreviations that shouldn't be treated as sentence endings 
        self.abbreviations = re.compile(
            r'\b(?:Mr|Mrs|Ms|Dr|Prof|Sr|Jr|vs|etc|Inc|Ltd|Co|Corp)\.'
        )
    
    def chunk(self, text: str, metadata: Optional[Dict[str, Any]] = None, verbose: bool = False) -> List[Dict[str, Any]]:
        """
        Main chunking function that applies the selected strategy 

        Args:
            text: Input text to chunk 
            metadata: Optional metadata to attach to each chunk 
            verbose: If True, print processing information 
        
        Returns: 
            List of chunk dictionaries with content and metadata 
        """

        if not text or not isinstance(text, str):
            if verbose: 
                print("Invalid input: text is empty or a string")
            return []
        
        # Remove whitespace 
        text = text.strip()
        
        # Check if text length is less that minimun chunk size 
        if len(text) < self.min_chunk_size:
            if verbose: 
                print(f"Text too short: {len(text)} chars (min: {self.min_chunk_size})")
            return []
        
        # Select chunking strategy
        if self.strategy == ChunkingStrategy.FIXED_SIZE:
            chunks = self._chunk_fixed_size(text)
        elif self.strategy == ChunkingStrategy.SENTENCE:
            chunks = self._chunk_by_sentence(text)
        elif self.strategy == ChunkingStrategy.PARAGRAPH:
            chunks = self._chunk_by_paragraph(text)
        elif self.strategy == ChunkingStrategy.SEMANTIC:
            chunks = self._chunk_semantic(text)
        elif self.strategy == ChunkingStrategy.RECURSIVE:
            chunks = self._chunk_recursive(text)
        else:
            chunks = self._chunk_fixed_size(text)

        # Filter out chunks that are too small
        chunks = [c for c in chunks if len(c) >= self.min_chunk_size]

        # Build chunk dictionaries with metadata 
        chunk_dicts = []
        for i, chunk_text in enumerate(chunks):
            chunk_dict = {
                'text': chunk_text,
                'chunk_index': i,
                'chunk_size': len(chunk_text),
                'total_chunks': len(chunks),
                'strategy': self.strategy.value
            }

            # Add original metadata if provided 
            if metadata:
                chunk_dict['source_metadata'] = metadata.copy()

            chunk_dicts.append(chunk_dict)

        # Update statistics 
        self.stats['texts_chunked'] += 1
        self.stats['total_chunks_created'] += len(chunk_dicts)

        # Calculate running averages 
        n = self.stats['texts_chunked']
        total_chunks = self.stats['total_chunks_created']

        self.stats['avg_chunks_per_text'] = total_chunks / n if n > 0 else 0 

        if chunk_dicts:
            avg_size = sum(c['chunk_size'] for c in chunk_dicts) / len(chunk_dicts)
            self.stats['avg_chunk_size'] = (
                (self.stats['avg_chunk_size'] * (n - 1) + avg_size) / n
            )
        if verbose:
            print(f"Created {len(chunk_dicts)} chunks using {self.strategy.value} strategy")
            print(f"Avg chunk size: {int(self.stats['avg_chunk_size'])} chars")

        return chunk_dicts
    
    def _chunk_fixed_size(self, text: str) -> List[str]:
        """
        Chunk text into fixed-size pieces with overlap 
        Respect sentence boundaries if enabled 

        Args: 
            text: Input text 
        
        Returns: 
            List of text chunks 
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0 

        while start < len(text):
            # Calculate end position of chunk
            end = start + self.chunk_size

            # If we are at the end already, take the whole text 
            if end >= len(text):
                chunk = text[start:].strip()
                if chunk:
                    chunks.append(chunk)
                break

            # Try to break at sentence boundary if enabled 
            if self.respect_sentence_boundary:
                # Look for sentence ending between start and end of the chunk 
                search_text = text[start:end]
                sentence_matches = list(self.sentence_pattern.finditer(search_text))

                if sentence_matches:
                    # Select and use last sentence ending found 
                    last_match = sentence_matches[-1]
                    actual_end = start + last_match.end()
                
                else: 
                    # No sentence end found within the chunk, try to break at word boundary 
                    actual_end = self._find_word_boundary(text, start, end)
            
            else:
                # No sentence end found and could not break at word boundary 
                actual_end = end 

            # Extract chunk
            chunk = text[start:actual_end].strip()
            if chunk: 
                chunks.append(chunk)
            
            # Move start position to overlap position 
            next_start = actual_end - self.chunk_overlap

            # Ensure we make progress: We aren't stuck in an infinity loop 
            if next_start <= start:
                # We are stuck at the same previous start position. 
                next_start = actual_end # move start to actual end to force progress
            
            start = next_start # set next_start to start 
            
        return chunks 
    
    def _chunk_by_sentence(self, text: str) -> List[str]:
        """
        Chunk text by grouping sentences until they reach chunk_size 

        Args: 
            text: Input text 
        
        Returns: 
            List of text chunks 
        """

        sentences = self._split_sentences(text)

        if not sentences: 
            return [text]
        
        chunks = []
        current_chunk = []
        current_size = 0

        for sentence in sentences:
            sentence_size = len(sentence)

            # If adding current iter sentence exceed chunk_size, start new chunk 
            if current_size + sentence_size > self.chunk_size and current_chunk:
                # Add current chunk 
                chunk_text = ' '.join(current_chunk).strip()
                if chunk_text: 
                    chunks.append(chunk_text)

                # Handle overlap by keeping last 1 or 2 sentences 
                if self.chunk_overlap > 0 and len(current_chunk) > 1:
                    overlap_text = ' '.join(current_chunk[-2:]) # get last two items(sentences) in current_chunk list 
                    if len(overlap_text) <= self.chunk_overlap:
                        current_chunk = current_chunk[-2:]
                        current_size = len(overlap_text)
                    else:
                        current_chunk = current_chunk[-1:]
                        current_size = len(current_chunk[0])
                
                else:
                    current_chunk = []
                    current_size = 0
            
            current_chunk.append(sentence)
            current_size += sentence_size + 1  # +1 for space

        # Add remaining chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk).strip()
            if chunk_text:
                chunks.append(chunk_text)
        
        return chunks
    
    def _chunk_by_paragraph(self, text: str) -> List[str]:
        """
        Chunk text by paragraph, combining small ones 

        Args: 
            text: Input text 
        
        Returns: 
            List of text chunks 
        """

        # Split by paragraphs
        paragraphs = self.paragraph_pattern.split(text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        if not paragraphs:
            return [text]
        
        chunks = [] 
        current_chunk = []
        current_size = 0

        for para in paragraphs:
            para_size = len(para)

            # If a single paragraph exceeds the chunk_size, split it 
            if para_size > self.chunk_size:
                # Save current chunk if exists 
                if current_chunk:
                    chunk_text = '\n\n'.join(current_chunk).strip()
                    if chunk_text:
                        chunks.append(chunk_text)
                    current_chunk = []
                    current_size = 0 
                
                # Split large paragraph using fixed size strategy 
                sub_chunks = self._chunk_fixed_size(para)
                chunks.extend(sub_chunks)
                continue
            
            # if add a paragraph exceeds chunk_size, start a new chunk 
            if current_size + para_size > self.chunk_size and current_chunk:
                chunk_text = '\n\n'.join(current_chunk).strip()
                if chunk_text:
                    chunks.append(chunk_text)
                
                # Handle Overlap 
                if self.chunk_overlap > 0 and current_chunk:
                    last_para = current_chunk[:1]   
                    if len(last_para) <= self.chunk_overlap:
                        current_chunk = [last_para]
                        current_size = len(last_para) 
                    else:
                        current_chunk = []
                        current_size = 0

                else: 
                    current_chunk = []
                    current_size = 0 

            current_chunk.append(para)
            current_size += para_size + 2  # +2 for \n\n

        # Add remaining chunk 
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk).strip()
            if chunk_text:
                chunks.append(chunk_text)

        return chunks   
    
    def _chunk_semantic(self, text: str) -> List[str]:
        """
        Chunk text based on semantic boundaries (paragrapshs + sentences)

        Args: 
            text: Input text 
        
        Returns: 
            List of text chunks 
        """

        # Try paragraph based chunking first 
        paragraphs = self.paragraph_pattern.split(text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        if len(paragraphs) <= 1:
            # This means no paragraph. Fall back to sentence chunking 
            return self._chunk_by_sentence(text)
        
        # Otherwise, use paragraph chunking 
        return self._chunk_by_paragraph(text)
