import re 
from typing import List, Dict, Optional, Any 
import unicodedata


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
        
        def preprocess(self, text: str, verbose: bool = False) -> Optional[Dict[str, Any]]:
            """
            Main preprocessing function that applies all the cleaning steps 

            Args:
                text: Raw text to preprocess
                verbose: If True, print processing steps 
            
            Returns: 
                Dict containing cleaned text and metadata, or None if text is invalid 
            """
            # Check if the input is a text and whether the text is a string 
            if not text or not isinstance(text, str):
                if verbose:
                    print(f"Invalid input: text is empty or not a string")
                self.stats['text_rejected'] += 1 
                return None 
            
            original_length = len(text)
            cleaning_steps = []

            # Cleaning step 1: Unicode normalization 
            if self.normalize_unicode:
                text = self._normalize_unicode(text)
                cleaning_steps.append("unicode_normalized")
            
            # Cleaning step 2: Remove Urls 
            if self.remove_urls: 
                text, urls_removed = self.remove_urls(text)
                if urls_removed > 0: 
                    cleaning_steps.append(f"removed_{urls_removed}_urls")
            
            # Cleaning step 3: Remove emails 
            if self.remove_emails: 
                text, emails_removed = self._remove_emails(text)
                if emails_removed > 0:
                    cleaning_steps.append(f"removed_{emails_removed}_emails")
            
            # Cleaning step 4: Clean special characters 
            text = self._clean_special_chars(text)
            cleaning_steps.append("Special_chars_cleaned")

            # Cleaning step 5: Remove extra whitespace
            if self.remove_extra_whitespace:
                text = self._remove_extra_whitespace(text)
                cleaning_steps.append("whitespace normalized")
            
            # Cleaning step 6: Convert to lower case
            if self.lowercase:
                text = text.lower()
                cleaning_steps.append("lowercased")
            
            # Cleaning step 7: Final trim
            text = text.strip()

            # Validate minimum length 
            if len(text) < self.min_length:
                if verbose: 
                    print(f"Text too short after preprocessing: {len(text)} chars (min: {self.min_length})")
                self.stats['texts_rejected'] += 1 
                return None 

            # Update statistics 
            final_length = len(text)
            chars_removed = original_length - final_length
            self.stats['texts_processed'] += 1 
            self.stats['total_chars_removed'] += chars_removed

            # Calculate running averages 
            n = self.stats['texts_processed']
            self.stats['avg_length_before'] = ((self.stats['avg_length_before'] * (n - 1) + original_length) / n)
            self.stats['avg_length_after'] = ((self.stats['avg_length_after'] * (n - 1) + final_length) / n)

            if verbose: 
                print(f" Preprocessed: {original_length} -> {final_length} chars")
                print(f" Steps applied: {' '.join(cleaning_steps)}")

            return {
                'text': text,
                'metadata': {
                    'original_length': original_length,
                    'final_length': final_length,
                    'chars_removed': chars_removed,
                    'reduction_precentage': round((chars_removed / original_length) * 100, 2) if original_length > 0 else 0, 
                    'cleaning_steps': cleaning_steps
                }
            }

        def _normalize_unicode(self, text: str) -> str:
            """
            Normalize Unicode characters using NFC normalization 
            Converts characters to their canonical composed form 

            Args: 
                text: Input text
            
            Returns:
                Normalized text 
            """
            return unicodedata.normalize('NFC', text)

        def _remove_urls(self, text:str) -> tuple:
            """
            Remove Urls from text

            Args:
                text: Input text
            
            Returns: 
                Tuple of (cleaned_text, count_of_urls_removed)
            """  
            urls_found = self.url_pattern.findall(text)
            cleaned_text = self.url_pattern.sub(' ', text)
            return cleaned_text, len(urls_found)