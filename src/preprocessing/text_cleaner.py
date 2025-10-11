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

        