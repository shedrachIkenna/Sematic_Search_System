from pathlib import Path 
import unittest
import tempfile
import shutil
from pathlib import Path

# Import the class to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.ingestion.document_loader import DocumentIngestion

class TestDocumentIngestion(unittest.TestCase):
    """Comprehensive test suite for DocumentIngestion class"""
    
    def setUp(self):
        """Set up test fixtures before each test"""
        self.ingestion = DocumentIngestion()
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after each test"""
        # Remove temporary directory and all contents
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def create_test_file(self, filename: str, content: str) -> Path:
        """Helper method to create a test file"""
        file_path = Path(self.test_dir) / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    
    # Test initialization
    def test_initialization(self):
        """Test that DocumentIngestion initializes correctly"""
        self.assertIsNotNone(self.ingestion.supported_formats)
        self.assertIsNotNone(self.ingestion.all_extensions)
        self.assertIsNotNone(self.ingestion.stats)
        self.assertEqual(self.ingestion.stats['files_processed'], 0)
    
    # Test supported format checking
    def test_is_supported_format_text(self):
        """Test that text files are recognized as supported"""
        test_path = Path("test.txt")
        self.assertTrue(self.ingestion.is_supported_format(test_path))
    
    def test_is_supported_format_markdown(self):
        """Test that markdown files are recognized as supported"""
        test_path = Path("test.md")
        self.assertTrue(self.ingestion.is_supported_format(test_path))
    
    def test_is_supported_format_code(self):
        """Test that code files are recognized as supported"""
        test_path = Path("test.py")
        self.assertTrue(self.ingestion.is_supported_format(test_path))
    
    def test_is_supported_format_unsupported(self):
        """Test that unsupported files are correctly identified"""
        test_path = Path("test.exe")
        self.assertFalse(self.ingestion.is_supported_format(test_path))
    
    # Test category detection
    def test_get_file_category_text(self):
        """Test category detection for text files"""
        test_path = Path("test.txt")
        self.assertEqual(self.ingestion.get_file_category(test_path), 'text')
    
    def test_get_file_category_code(self):
        """Test category detection for code files"""
        test_path = Path("test.py")
        self.assertEqual(self.ingestion.get_file_category(test_path), 'code')
    
    def test_get_file_category_data(self):
        """Test category detection for data files"""
        test_path = Path("test.json")
        self.assertEqual(self.ingestion.get_file_category(test_path), 'data')
    
    def test_get_file_category_unsupported(self):
        """Test category detection for unsupported files"""
        test_path = Path("test.exe")
        self.assertIsNone(self.ingestion.get_file_category(test_path))
    
    # Test single file loading
    def test_load_single_file_success(self):
        """Test successful loading of a single file"""
        content = "This is a test document with some content."
        file_path = self.create_test_file("test.txt", content)
        
        result = self.ingestion.load_single_file(str(file_path), verbose=False)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['content'], content)
        self.assertEqual(result['metadata']['filename'], "test.txt")
        self.assertEqual(result['metadata']['character_count'], len(content))
        self.assertEqual(self.ingestion.stats['files_processed'], 1)
    
    def test_load_single_file_nonexistent(self):
        """Test loading a non-existent file"""
        result = self.ingestion.load_single_file("nonexistent.txt", verbose=False)
        self.assertIsNone(result)
    
    def test_load_single_file_empty(self):
        """Test loading an empty file"""
        file_path = self.create_test_file("empty.txt", "")
        result = self.ingestion.load_single_file(str(file_path), verbose=False)
        self.assertIsNone(result)
    
    def test_load_single_file_unsupported_format(self):
        """Test loading a file with unsupported format"""
        file_path = Path(self.test_dir) / "test.exe"
        with open(file_path, 'wb') as f:
            f.write(b"binary content")
        
        result = self.ingestion.load_single_file(str(file_path), verbose=False)
        self.assertIsNone(result)
    
    def test_load_single_file_metadata(self):
        """Test that metadata is correctly populated"""
        content = "Test content"
        file_path = self.create_test_file("test.txt", content)
        
        result = self.ingestion.load_single_file(str(file_path), verbose=False)
        
        self.assertIn('filename', result['metadata'])
        self.assertIn('filepath', result['metadata'])
        self.assertIn('extension', result['metadata'])
        self.assertIn('category', result['metadata'])
        self.assertIn('size_bytes', result['metadata'])
        self.assertIn('character_count', result['metadata'])
        self.assertEqual(result['metadata']['extension'], '.txt')
        self.assertEqual(result['metadata']['category'], 'text')
    
    # Test directory loading
    def test_load_directory_success(self):
        """Test loading files from a directory"""
        self.create_test_file("file1.txt", "Content 1")
        self.create_test_file("file2.md", "Content 2")
        self.create_test_file("file3.py", "print('hello')")
        
        documents = self.ingestion.load_directory(self.test_dir, verbose=False)
        
        self.assertEqual(len(documents), 3)
        self.assertEqual(self.ingestion.stats['files_processed'], 3)
    
    def test_load_directory_nonexistent(self):
        """Test loading from a non-existent directory"""
        documents = self.ingestion.load_directory("/nonexistent/path", verbose=False)
        self.assertEqual(len(documents), 0)
    
    def test_load_directory_recursive(self):
        """Test recursive directory loading"""
        # Create subdirectory
        subdir = Path(self.test_dir) / "subdir"
        subdir.mkdir()
        
        self.create_test_file("file1.txt", "Content 1")
        
        subfile = subdir / "file2.txt"
        with open(subfile, 'w') as f:
            f.write("Content 2")
        
        # Test recursive (should find both files)
        self.ingestion.reset_statistics()
        documents = self.ingestion.load_directory(self.test_dir, recursive=True, verbose=False)
        self.assertEqual(len(documents), 2)
        
        # Test non-recursive (should find only top-level file)
        self.ingestion.reset_statistics()
        documents = self.ingestion.load_directory(self.test_dir, recursive=False, verbose=False)
        self.assertEqual(len(documents), 1)
    
    def test_load_directory_mixed_formats(self):
        """Test loading directory with mixed supported and unsupported files"""
        self.create_test_file("supported.txt", "Content")
        
        # Create unsupported file
        unsupported = Path(self.test_dir) / "unsupported.exe"
        with open(unsupported, 'wb') as f:
            f.write(b"binary")
        
        documents = self.ingestion.load_directory(self.test_dir, verbose=False)
        self.assertEqual(len(documents), 1)
    
    # Test multiple file loading
    def test_load_multiple_files_success(self):
        """Test loading multiple specific files"""
        file1 = self.create_test_file("file1.txt", "Content 1")
        file2 = self.create_test_file("file2.md", "Content 2")
        
        documents = self.ingestion.load_multiple_files(
            [str(file1), str(file2)], 
            verbose=False
        )
        
        self.assertEqual(len(documents), 2)
        self.assertEqual(self.ingestion.stats['files_processed'], 2)
    
    def test_load_multiple_files_partial_failure(self):
        """Test loading multiple files with some failures"""
        file1 = self.create_test_file("file1.txt", "Content 1")
        
        documents = self.ingestion.load_multiple_files(
            [str(file1), "nonexistent.txt"],
            verbose=False
        )
        
        self.assertEqual(len(documents), 1)
        self.assertEqual(self.ingestion.stats['files_processed'], 1)
        self.assertEqual(self.ingestion.stats['files_failed'], 1)
    
    # Test statistics
    def test_statistics_tracking(self):
        """Test that statistics are correctly tracked"""
        file1 = self.create_test_file("file1.txt", "A" * 100)
        file2 = self.create_test_file("file2.txt", "B" * 200)
        
        self.ingestion.load_multiple_files([str(file1), str(file2)], verbose=False)
        
        stats = self.ingestion.get_statistics()
        self.assertEqual(stats['files_processed'], 2)
        self.assertGreater(stats['total_size_bytes'], 0)
    
    def test_reset_statistics(self):
        """Test that statistics can be reset"""
        file_path = self.create_test_file("test.txt", "Content")
        self.ingestion.load_single_file(str(file_path), verbose=False)
        
        self.assertEqual(self.ingestion.stats['files_processed'], 1)
        
        self.ingestion.reset_statistics()
        self.assertEqual(self.ingestion.stats['files_processed'], 0)
        self.assertEqual(self.ingestion.stats['total_size_bytes'], 0)
    
    # Test text file reading with different encodings
    def test_read_text_file_utf8(self):
        """Test reading UTF-8 encoded file"""
        content = "Hello 世界 🌍"
        file_path = self.create_test_file("utf8.txt", content)
        
        result = self.ingestion.load_single_file(str(file_path), verbose=False)
        self.assertIsNotNone(result)
        self.assertEqual(result['content'], content)
    
    # Test edge cases
    def test_load_file_with_special_characters(self):
        """Test loading file with special characters in content"""
        content = "Special chars: @#$%^&*(){}[]|\\:;<>?/~`"
        file_path = self.create_test_file("special.txt", content)
        
        result = self.ingestion.load_single_file(str(file_path), verbose=False)
        self.assertIsNotNone(result)
        self.assertEqual(result['content'], content)
    
    def test_load_large_file(self):
        """Test loading a large file"""
        content = "A" * 1000000  # 1MB of text
        file_path = self.create_test_file("large.txt", content)
        
        result = self.ingestion.load_single_file(str(file_path), verbose=False)
        self.assertIsNotNone(result)
        self.assertEqual(len(result['content']), 1000000)

if __name__ == "__main__":
    unittest.main()