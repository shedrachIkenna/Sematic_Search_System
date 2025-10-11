import re 
from typing import List, Dict, Optional, Any 

class TextPreprocessor:
    """
    Handles cleaning and normalization of text content for semantic search 
    Prepares text for chunking and embedding generation 
    """

    def __init__(self, 
                 lowercase: bool = False, 
                 remove_urls: bool = True, 
                 remove_emails: bool = True,
                 remove_extra_whitespace: bool = True,
                 normalize_unicode: bool = True,
                 min_length: int = 10):
        """
        Initialize text preprocessor with configuration options 

        Args: 
            lowercase: Convert text to lowercase 
            remove_urls: Remove Urls from text 
            remove_emails: Remove email address from text 
            remove_extra_whitespace: Clean up extra whitespaces and line breaks 
            normalize_unicode: Normalize unicode characters (NFC normalization)
            min_length: Minimum character count for valid text 
        
        Returns: 
            Constructor function doesn't return anything 
        """
        self.lowercase = lowercase
        self.remove_urls = remove_urls
        self.remove_emails = remove_emails
        self.remove_extra_whitespace = remove_extra_whitespace
        self.normalize_unicode = normalize_unicode
        self.min_length = min_length

        # Compile regex patterns 
        self._compile_patterns() 

        # Statistics 
        self.stats = {
            'texts_processed': 0,
            'texts_rejected': 0,
            'avg_length_before': 0,
            'avg_length_after': 0,
            'total_chars_removed': 0
        }

        def _compile_patterns(self):
            """Compile regex patterns for text processing"""
            # URL pattern (matches http://, https://, www.)
            self.url_pattern = re.compile(
                r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
                r'|www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            )

            # Email Pattern 
            self.email_pattern = re.compile(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            )

            # Multiple spaces 
            self.multiple_space_pattern = re.compile(r' {2,}')

            # Multiple line breaks
            self.multi_newline_pattern = re.compile(r'\n{3,}')
        
            # Special characters that should be replaced with space
            self.special_chars_pattern = re.compile(r'[\t\r\f\v]')
        
        
