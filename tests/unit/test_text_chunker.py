import unittest
import re
from unittest.mock import Mock, patch
from src.chunking.text_chunker import TextChunker


class TestChunkFixedSize(unittest.TestCase):
    """Unit tests for the _chunk_fixed_size method"""

    def setUp(self):
        """Set up test fixtures"""
        self.chunker = TextChunker(chunk_size=50, chunk_overlap=10)
        self.chunker.sentence_pattern = re.compile(r'[.!?]+\s*')
        self.chunker.respect_sentence_boundary = True

    def test_text_shorter_than_chunk_size(self):
        """Test that text shorter than chunk_size returns single chunk"""
        text = "This is a short text."
        result = self.chunker._chunk_fixed_size(text)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], text)

    def test_text_exactly_chunk_size(self):
        """Test that text exactly equal to chunk_size returns single chunk"""
        text = "a" * 50
        result = self.chunker._chunk_fixed_size(text)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], text)

    def test_basic_chunking_without_sentence_boundary(self):
        """Test basic chunking when sentence boundary is disabled"""
        self.chunker.respect_sentence_boundary = False
        text = "a" * 120
        result = self.chunker._chunk_fixed_size(text)
        
        # Should create multiple chunks with overlap
        self.assertGreater(len(result), 1)
        self.assertEqual(len(result[0]), 50)

    def test_chunking_with_sentence_boundary(self):
        """Test chunking respects sentence boundaries"""
        text = "First sentence here. Second sentence here. Third sentence here. Fourth sentence here."
        result = self.chunker._chunk_fixed_size(text)
        
        # All chunks should end with sentence endings (or be the last chunk)
        for i, chunk in enumerate(result[:-1]):
            # Check that chunk ends with punctuation followed by optional whitespace
            self.assertRegex(chunk.rstrip(), r'[.!?]$')

    def test_chunking_with_overlap(self):
        """Test that chunks have proper overlap"""
        text = "This is sentence one. This is sentence two. This is sentence three. This is sentence four."
        result = self.chunker._chunk_fixed_size(text)
        
        if len(result) > 1:
            # Verify overlap exists between consecutive chunks
            for i in range(len(result) - 1):
                # Check that some content from end of chunk i appears in chunk i+1
                chunk1_end = result[i][-10:]  # Last 10 chars
                chunk2 = result[i + 1]
                # At least some overlap should exist
                self.assertTrue(any(word in chunk2 for word in chunk1_end.split() if len(word) > 3))

    def test_no_sentence_boundary_fallback_to_word_boundary(self):
        """Test fallback to word boundary when no sentence ending found"""
        self.chunker.respect_sentence_boundary = True
        self.chunker._find_word_boundary = Mock(return_value=45)
        
        # Text with no sentence endings within chunk size
        text = "a" * 120
        result = self.chunker._chunk_fixed_size(text)
        
        # Should call _find_word_boundary
        self.chunker._find_word_boundary.assert_called()

    def test_empty_chunks_are_filtered(self):
        """Test that empty chunks are not included in results"""
        text = "     First sentence.     Second sentence.     "
        result = self.chunker._chunk_fixed_size(text)
        
        # All chunks should have content (strip removes whitespace)
        for chunk in result:
            self.assertTrue(len(chunk) > 0)
            self.assertNotEqual(chunk, "")

    def test_progress_guarantee_prevents_infinite_loop(self):
        """Test that progress is guaranteed even in edge cases"""
        self.chunker.chunk_size = 5
        self.chunker.chunk_overlap = 10  # Overlap larger than chunk size
        self.chunker.respect_sentence_boundary = False
        
        text = "abcdefghijklmnopqrstuvwxyz"
        result = self.chunker._chunk_fixed_size(text)
        
        # Should complete without infinite loop
        self.assertGreater(len(result), 0)
        # All text should be covered
        combined = "".join(result)
        self.assertGreaterEqual(len(combined), len(text.strip()))

    def test_last_chunk_handling(self):
        """Test that the last chunk is properly extracted"""
        text = "Sentence one. Sentence two. Sentence three."
        result = self.chunker._chunk_fixed_size(text)
        
        # Last chunk should contain the end of the text
        last_chunk = result[-1]
        self.assertTrue("three" in last_chunk)

    def test_multiple_sentence_endings_in_chunk(self):
        """Test that last sentence ending is selected when multiple exist"""
        self.chunker.chunk_size = 60
        text = "First. Second. Third. Fourth. Fifth. Sixth. Seventh. Eighth."
        result = self.chunker._chunk_fixed_size(text)
        
        # Should break at the last sentence ending within chunk size
        if len(result) > 1:
            # First chunk should contain multiple sentences
            self.assertGreater(result[0].count('.'), 0)

    def test_whitespace_handling(self):
        """Test proper handling of leading/trailing whitespace"""
        text = "   First sentence.   Second sentence.   Third sentence.   "
        result = self.chunker._chunk_fixed_size(text)
        
        # Chunks should be stripped of leading/trailing whitespace
        for chunk in result:
            self.assertEqual(chunk, chunk.strip())

    def test_large_overlap_with_sentence_boundary(self):
        """Test chunking with large overlap and sentence boundaries"""
        self.chunker.chunk_overlap = 40
        text = "A" * 30 + ". " + "B" * 30 + ". " + "C" * 30 + "."
        result = self.chunker._chunk_fixed_size(text)
        
        # Should still produce valid chunks
        self.assertGreater(len(result), 0)
        for chunk in result:
            self.assertTrue(len(chunk) > 0)

    def test_no_sentence_pattern_matches(self):
        """Test behavior when no sentence patterns are found"""
        self.chunker.respect_sentence_boundary = True
        self.chunker._find_word_boundary = Mock(return_value=45)
        
        text = "NoSentenceEndingsHereJustALongStringOfTextWithoutAnyPunctuation" * 3
        result = self.chunker._chunk_fixed_size(text)
        
        # Should fallback to word boundary or fixed size
        self.assertGreater(len(result), 0)


if __name__ == '__main__':
    unittest.main()