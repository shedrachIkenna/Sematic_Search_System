"""
Document Ingestion System for Semantic Search Engine
Load documents from various sources and formats 

"""

from pathlib import Path
from typing import List, Dict, Optional


class DocumentIngestion: 
    def __init__(self):
        # Define supported file extensions by category 
        self.supported_formats = {
            'text': ['.txt', '.md', '.markdown'],
            'code': ['.py', '.js', '.java', '.cpp', '.c', '.html', '.css', '.xml'],
            'data': ['.json', '.csv', '.tsv'],
            'document': ['.pdf']
        }

        # All supported file extensions 
        self.all_extensions = []

        # Compile all supported file extentions 
        for category in self.supported_formats.values():
            self.all_extensions.extend(category)
        
        # Statistics tracking 
        self.stats = {
            'total_files_found': 0,
            'files_processed': 0,
            'files_failed': 0, 
            'total_size_bytes': 0
        }
    
    def is_supported_format(self, file_path: Path) -> bool:
        """
        Check if a file format is supported 

        Args:
            file_path: Path to the file 
        
        Returns: 
            bool: True if format is supported, False otherwise 

        """
        return file_path.suffix.lower() in self.all_extensions

    def get_file_category(self, file_path: Path) -> Optional[str]: 
        """
        Determine the category of a file based on its extension 

        Args: 
            file_path: Path to the file 
        
        Returns:
            str: Category name or None if unsupported 

        """

        ext = file_path.suffix.lower()
        for category, extensions in self.supported_formats.items():
            if ext in extensions:
                return category
        return None