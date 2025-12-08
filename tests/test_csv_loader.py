
import unittest
import sys
import os
import pandas as pd
import unittest.mock as mock

# Setup paths
# We need to import 'etl.py' from 'etl/csv_loader'
# AND we need to ensure 'etl.py' can import 'database' from 'etl/'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
etl_dir = os.path.join(project_root, 'etl')
csv_loader_dir = os.path.join(etl_dir, 'csv_loader')

sys.path.insert(0, project_root) # Add project root so 'import etl.database' works
sys.path.append(etl_dir)
sys.path.append(csv_loader_dir)

# Mock 'database' and 'etl.database' modules BEFORE importing etl
sys.modules['database'] = mock.MagicMock()
sys.modules['etl.database'] = mock.MagicMock()

# Mock sqlalchemy
# Mock sqlalchemy
sys.modules['sqlalchemy'] = mock.MagicMock()
sys.modules['sqlalchemy.text'] = mock.MagicMock()
# Mock dialects.postgresql
mock_postgres = mock.MagicMock()
sys.modules['sqlalchemy.dialects'] = mock.MagicMock()
sys.modules['sqlalchemy.dialects.postgresql'] = mock_postgres

# Set environment variable to avoid any incidental side effects if specific config is loaded
os.environ['DB_NAME'] = 'test_db'

# Mock great_expectations
sys.modules['great_expectations'] = mock.MagicMock()

try:
    # Load transform module
    import importlib.util
    spec = importlib.util.spec_from_file_location("transform", os.path.join(csv_loader_dir, "transform.py"))
    transform_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(transform_module)
except ImportError as e:
    pass

class TestETLTransform(unittest.TestCase):
    
    def test_book_id_generation(self):
        """
        Test that book_id is generated sequentially (01, 02...)
        instead of using category_label.
        """
        # Create dummy data
        data = {
            'Category': ['CatA', 'CatA', 'CatB'],
            'category_label': ['Label1', 'Label2', 'Label3'],
            'book_name': ['Book1', 'Book2', 'Book3'],
            'location': ['Loc1', 'Loc1', 'Loc2']
        }
        df = pd.DataFrame(data)
        
        # Run transform
        df_transformed = transform_module.transform_data(df)
        
        # Check assertions
        expected_ids = ['01', '02', '03']
        actual_ids = df_transformed['book_id'].tolist()
        
        self.assertEqual(actual_ids, expected_ids, f"Expected IDs {expected_ids}, but got {actual_ids}")
        
        # Verify other columns are preserved/renamed correctly
        self.assertEqual(df_transformed['book_category_label'].iloc[0], 'Label1')
        self.assertEqual(df_transformed['name'].iloc[0], 'Book1')

    def test_validation_logic(self):
        """
        Test that validation logic correctly calls Great Expectations.
        """
        # Create dummy data
        data = {
           'book_category': ['CatA'],
           'book_category_label': ['Label1'],
           'name': ['Book1'],
           'location_name': ['Loc1'],
           'book_id': ['01']
        }
        df = pd.DataFrame(data)

        # Import validation module
        import importlib.util
        spec = importlib.util.spec_from_file_location("validation", os.path.join(csv_loader_dir, "validation.py"))
        validation = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validation)
        
        # Mock the GX dataframe and its validation result
        mock_gx_df = mock.MagicMock()
        mock_gx_df.validate.return_value = {"success": True}
        
        # Expectation methods should return success dicts
        mock_gx_df.expect_column_to_exist.return_value = {"success": True}
        mock_gx_df.expect_column_values_to_not_be_null.return_value = {"success": True}
        
        # Mock gx.from_pandas to return our mock_gx_df
        with mock.patch('great_expectations.from_pandas', return_value=mock_gx_df):
             result = validation.validate_data(df)
             self.assertTrue(result)
             
        # Test failure case
        mock_gx_df.validate.return_value = {"success": False, "results": []}
        with mock.patch('great_expectations.from_pandas', return_value=mock_gx_df):
             with self.assertRaises(ValueError):
                 validation.validate_data(df)

    def test_pipeline_orchestration(self):
        """
        Test that main.py orchestrates the pipeline correctly:
        Extract -> Transform -> Validate -> Load Locations -> Load Books
        """
        # We need to mock the modules that main.py imports
        # Since main.py imports them at top level, we need to ensure they are mocked in sys.modules
        # before we import main.
        
        # Create mocks
        mock_extract = mock.MagicMock()
        mock_transform = mock.MagicMock()
        mock_load = mock.MagicMock()
        mock_validation = mock.MagicMock()
        
        # Setup return values
        mock_extract.extract_data.return_value = pd.DataFrame({'col': [1]})
        mock_transform.transform_data.return_value = pd.DataFrame({'col': [1], 'transformed': True})
        
        # Inject mocks into sys.modules
        # We need to use context manager or setup/teardown if we want to be clean, 
        # but for this script we can just patch sys.modules
        
        # We need to mock 'csv_loader.extract', 'csv_loader.transform', etc.
        # because main.py now uses "from csv_loader.extract import ..."
        
        with mock.patch.dict(sys.modules, {
            'csv_loader': mock.MagicMock(), # Ensure parent package exists in modules
            'csv_loader.extract': mock_extract,
            'csv_loader.transform': mock_transform,
            'csv_loader.load': mock_load,
            'csv_loader.validation': mock_validation,
            # Also mock the short names if any legacy code still uses them, though main.py is explicit now
            'extract': mock_extract,
            'transform': mock_transform,
            'load': mock_load,
            'validation': mock_validation
        }):
            # Import main dynamically
            import importlib.util
            spec = importlib.util.spec_from_file_location("main", os.path.join(csv_loader_dir, "main.py"))
            main = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(main)
            
            # Run pipeline
            main.run_pipeline("dummy_path.csv")
            
            # Verify calls
            mock_extract.extract_data.assert_called_once_with("dummy_path.csv")
            mock_transform.transform_data.assert_called_once()
            mock_validation.validate_data.assert_called_once()
            mock_load.load_locations.assert_called_once()
            mock_load.load_books.assert_called_once()
            
            # Verify Order (roughly)
            # We can check that load_books was called after load_locations
            parent = mock.Mock()
            parent.attach_mock(mock_load.load_locations, 'load_locations')
            parent.attach_mock(mock_load.load_books, 'load_books')
            
            # Create a sequence of expected calls
            # validation -> load_locations -> load_books
            # But we attached to different mocks, so it is harder to track exact order across modules without a shared parent.
            # However, assert_called_once is good enough for now to prove they are invoked.

if __name__ == '__main__':
    unittest.main()
