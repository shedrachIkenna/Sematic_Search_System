"""
Document Ingestion System for Semantic Search Engine
Load documents from various sources and formats 

"""


class DocumentIngestion: 
    def __init__(self):
        # Define supported file extensions by category 
        self.supported_formats = {
            'text': ['.txt', '.md', '.markdown'],
            'code': ['.py', '.js', '.java', '.cpp', '.c', '.html', '.css', '.xml'],
            'data': ['.json', '.csv', '.tsv'],
            'document': ['.pdf']
        }

        # Flatten all supported file extensions 
        self.all_extensions = []

        for category in self.supported_formats.values():
            self.all_extensions.extend(category)
        
        # Statistics tracking 
        self.stats = {
            'total_files_found': 0,
            'files_processed': 0,
            'files_failed': 0, 
            'total_size_bytes': 0
        }