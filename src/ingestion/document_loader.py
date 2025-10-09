"""
Document Ingestion System for Semantic Search Engine
Load documents from various sources and formats 

"""

from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import mimetypes


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
            str: Category name or None if unsupported file format
        """
        ext = file_path.suffix.lower()
        for category, extensions in self.supported_formats.items():
            if ext in extensions:
                return category
        return None 
    
    def load_single_file(self, file_path: str, verbose: bool = True) -> Optional[Dict[str, Any]]:
        """
        Load a single file and extract its contents 

        Args: 
            file_path: String path to the file 
        
        Returns: 
            Dict containing file contents and metadata, or None if failed 
        """
        try: 
            file_path = Path(file_path) # Converts string to path object 

            # Check if file exists 
            if not file_path.exists():
                if verbose:
                    print(f"Error: file not found - {file_path}")
                return None 
            
            # Check if its a file 
            if not file_path.is_file():
                if verbose:
                    print(f"Error: Not a file - {file_path}")
                return None 
            
            # Check if file format is supported 
            if not self.is_supported_format(file_path):
                if verbose:
                    print(f"Warning: Unsupported format - {file_path.suffix}")
                    print(f"Supported formats: {', '.join(self.all_extensions)}")
                return None 

            # Get file stats 
            file_stats = file_path.stat()
            file_size = file_stats.st_size 

            # Check for empty files 
            if file_size == 0: 
                if verbose: 
                    print(f"Warning: Empty file - {file_path.name}")
                return None 
            
            # Determine file category
            category = self.get_file_category(file_path)

            # Read file contents based on category 
            if category == 'document' and file_path.suffix.lower() == ".pdf":
                content = self._read_pdf(file_path, verbose)
            else:
                content = self._read_text_file(file_path, verbose)

            # Validate content was extracted 
            if content is None or not content.strip():
                if verbose: 
                    print(f"Warning: No content extracted from {file_path.name}")
                return None
            
            # Buid metadata 
            metadata = {
                'filename': file_path.name,
                'file_path': str(file_path.absolute()),
                'extension': file_path.suffix,
                'category': category,
                'size_bytes': file_size,
                'size_kb': round(file_size/1024, 2),
                'modified_time': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                'mime_type': mimetypes.guess_type(str(file_path))[0],
                'character_count': len(content),
                'ingestion_time': datetime.now().isoformat()
            }

            # Update statistics 
            self.stats['files_processed'] += 1
            self.stats['total_size_bytes'] += file_size

            if verbose:
                print(f"Loaded: {file_path.name} ({metadata['size_kb']} KB, {metadata['character_count']} chars)")

            return {
                'content': content,
                'metadata': metadata
            }
        
        except Exception as e: 
            if verbose:
                print(f"Error loading {file_path}: {str(e)}")
            self.stats['files_failed'] += 1
            return None 
        

    