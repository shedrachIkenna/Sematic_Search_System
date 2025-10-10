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
        
    def _read_text_file(self, file_path: Path, verbose: bool = True) -> Optional[str]:
        """
        Read content from text-based files with encoding fallback 

        Args: 
            file_path: Path to the text file 
            verbose: if True, print status message 
        
        Returns: 
            str: File contents or None if failed 
        """
        # Encoding list 
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

        for encoding in encodings:
            try: 
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                return content
            except UnicodeDecodeError:
                continue
            except Exception as e: 
                if verbose:
                    print(f"  Error reading with {encoding}: {str(e)}")
                continue
        
        if verbose: 
            print(f"  Failed to decode file with any encoding")
        return None 
    
    def _read_pdf(self, file_path: Path, verbose: bool = True) -> Optional[str]:
        """
        Extract text from PDF files using multiple fallback methods 

        Args: 
            file_path: Path to the PDF file 
            verbose: If True, print status message 
        
        Returns: 
            str: Extracted text or None if failed 
        """

        # Method 1 - PyMuPDF (fitz) 
        try: 
            import fitz
            doc = fitz.open(str(file_path))
            text = ""
            for page_num, page in enumerate(doc):
                text += page.get_text()
            doc.close()

            if text.strip():
                return text
        except ImportError:
            pass
        except Exception as e:
            if verbose: 
                print(f" PyMuPDF failed: {str(e)}")
        

        # Method 2 - PyPDF2
        try: 
            import PyPDF2 
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()

                if text.strip():
                    return text
        except ImportError: 
            pass 
        except Exception as e: 
            if verbose: 
                print(f"PyPDF2 failed: {str(e)}")

        # Method 3: pdfplumber
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
            
            if text.strip():
                return text
        except ImportError:
            pass
        except Exception as e:
            if verbose:
                print(f"pdfplumber failed: {str(e)}")
    
        # Method 4: pdfminer
        try:
            from pdfminer.high_level import extract_text
            text = extract_text(str(file_path))
            if text.strip():
                return text
        except ImportError:
            pass
        except Exception as e:
            if verbose:
                print(f"pdfminer failed: {str(e)}")

        if verbose: 
            print(f"No PDF libraries available. Install one of:")
            print(f"pip install pymupdf")
            print(f"pip install PyPDF2")
            print(f"pip install pdfplumber")
            print(f"pip install pdfminer.six")
        
        return None 
    
    def load_directory(self, directory_path: str, recursive: bool = True, verbose: bool = True) -> List[Dict[str, Any]]:
        """
        Load all supported files from a directory 

        Args: 
            directory_path: Path to the directory 
            recursive: If True, search subdirectories 
            verbose: if True, print status messages

        Returns:
            List of document dictionaries with document metadata 
        """
        try: 
            directory = Path(directory_path)

            # Check if directory exists 
            if not directory.exists():
                if verbose: 
                    print(f"Error: Directory not found - {directory}")
                return []
            
            if not directory.is_dir():
                if verbose: 
                    print(f"Error: Not a directory - {directory}")
                return []
            
            if verbose: 
                print(f"\nScanning directory: {directory}")
                print(f"\nRecursive: {recursive}")
                print(f"\nSupported formats: {', '.join(self.all_extensions)}")
                print("-" * 70)
            
            # Get the list of all the files and subdirectories in the directory
            if recursive: 
                files = list(directory.rglob("*"))
            else:
                files = list(directory.glob("*"))

            # filter for files only (not directories)
            files = [f for f in files if f.is_file()]
            self.stats['total_files_found'] = len(files)

            if verbose: 
                print(f"Found {len(files)} files in total")
            
            # Select only supported files 
            supported_files = [f for f in files if self.is_supported_format(f)]
            if verbose: 
                print(f"Found {len(supported_files)} supported files\n")
            
            # Load each file 
            documents = []
            for file_path in supported_files:
                doc = self.load_single_file(str(file_path), verbose=verbose)
                if doc:
                    documents.append(doc)
            
            if verbose:
                print("\n" + "=" * 70)
                print(f"Ingestion Summary:")
                print(f"Total files found: {self.stats['total_files_found']}")
                print(f"Successfully processed: {self.stats['files_processed']}")
                print(f"Failed: {self.stats['files_failed']}")
                print(f"Total size: {round(self.stats['total_size_bytes'] / 1024, 2)} KB")
                print("=" * 70)

            return documents

        except Exception as e:
            if verbose:
                print(f"Error scanning directory: {str(e)}")
            return []

    def load_multiple_files(self, file_paths: List[str], verbose: bool = True, ) -> List[Dict[str, Any]]:
        """
        Load multiple specific files 

        Args: 
            file_paths: List of file paths to load 
            verbose: if True, print status message 
        
        Returns: 
            List of document directories with content and metadata 
        """

        if verbose:
            print(f"\nLoading {len(file_paths)} files...")
            print("-" * 70)

        documents = []
        for file_path in file_paths:
            doc = self.load_single_file(file_path, verbose=verbose)
            if doc:
                documents.append(doc)
        
        if verbose:
            print("\n" + "=" * 70)
            print(f"Ingestion Summary:")
            print(f" Requested files: {len(file_paths)}")
            print(f" Successfully processed: {self.stats['files_processed']}")
            print(f" Failed: {self.stats['files_failed']}")
            print("=" * 70)

        return documents
    
    
    