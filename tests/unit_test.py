# tests/unit_test.py

import unittest
import pandas as pd
from unittest.mock import patch, MagicMock, mock_open
import sys
import os

# Adjusting path to import modules from the 'etl' directory
# Assuming 'etl' is sibling to 'tests' in the root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../etl/csv_loader')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../etl')))

# Import the functions we want to test
import transform
import validation
import load

class TestETLPipeline(unittest.TestCase):
    
    def setUp(self):
        """Setup a consistent, raw input DataFrame for all tests."""
        self.raw_data = {
            'category': ['Fiction', 'Non-Fiction', 'Fiction', 'Biography'],
            'category_label': ['Novel', 'Science', 'Mystery', 'History'],
            'book_name': ['The Great Book', 'A History of Time', 'The Coded Key', 'Famous Person'],
            'location': ['Shelf A', 'Shelf B', 'Shelf A', 'Shelf C']
        }
        self.raw_df = pd.DataFrame(self.raw_data)
        
    # --- 1. Test Validation Logic ---
    
    def test_validation_success(self):
        """Tests that a clean DataFrame passes validation."""
        try:
            validation.run_validation(self.raw_df)
            # If no exception is raised, the test passes
            self.assertTrue(True) 
        except ValueError:
            self.fail("Validation failed unexpectedly on clean data.")

    def test_validation_failure_null_book_name(self):
        """Tests that validation fails when a required column (book_name) is null."""
        bad_data = self.raw_data.copy()
        bad_data['book_name'] = ['Book1', None, 'Book3', 'Book4']
        bad_df = pd.DataFrame(bad_data)
        
        # We expect a ValueError to be raised by run_validation
        with self.assertRaises(ValueError) as context:
            validation.run_validation(bad_df)
        
        self.assertIn("Data quality check failed", str(context.exception))
        
    # --- 2. Test Transformation Logic ---
    
    def test_transform_output_structure(self):
        """Tests that transform_data returns two DataFrames with correct columns."""
        books_df, locations_df = transform.transform_data(self.raw_df)
        
        # Check locations_df structure
        self.assertEqual(len(locations_df), 3) # Shelf A, Shelf B, Shelf C
        self.assertListEqual(locations_df.columns.tolist(), ['location_name'])
        
        # Check books_df structure
        expected_cols = {'book_id', 'name', 'book_category', 'book_category_label', 'location', 'status'}
        self.assertEqual(len(books_df), 4)
        self.assertSetEqual(set(books_df.columns.tolist()), expected_cols)
        
    def test_transform_book_id_uniqueness(self):
        """Tests that unique book_ids are generated."""
        books_df, _ = transform.transform_data(self.raw_df)
        # All generated book_ids must be unique
        self.assertEqual(books_df['book_id'].nunique(), len(books_df))
        
    def test_transform_default_status(self):
        """Tests that the default status is correctly applied."""
        books_df, _ = transform.transform_data(self.raw_df)
        self.assertTrue((books_df['status'] == 'Available').all())

    # --- 3. Test Loading Logic (Requires Mocking the Database) ---

    @patch('load.psycopg2.connect')
    def test_load_locations_successful(self, mock_connect):
        """Tests that location loading attempts correct database calls and returns map."""
        
        # Setup mock connection and cursor
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        
        # Simulate the database returning location_ids (1, 2, 3) for 3 unique locations
        # fetchone needs to return one result per location insert/select call
        mock_cursor.fetchone.side_effect = [(1,), (2,), (3,)] 
        mock_cursor.rowcount = 1 # Simulate that INSERT was successful
        
        _, locations_df = transform.transform_data(self.raw_df)
        
        location_map = load.load_locations(mock_conn, locations_df)
        
        # Assertions on the mock calls
        self.assertEqual(mock_cursor.execute.call_count, len(locations_df) * 1) # 3 INSERT calls
        mock_conn.commit.assert_called_once()
        
        # Assertions on the returned map
        expected_map_keys = set(locations_df['location_name'].tolist())
        self.assertSetEqual(set(location_map.keys()), expected_map_keys)
        self.assertEqual(len(location_map), 3)

    @patch('load.psycopg2.connect')
    def test_load_books_successful(self, mock_connect):
        """Tests that book loading attempts correct database calls."""
        
        # Setup mock connection and cursor
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        
        # Mock the location map that would come from a successful load_locations
        location_map = {
            'Shelf A': 1,
            'Shelf B': 2,
            'Shelf C': 3
        }
        
        books_df, _ = transform.transform_data(self.raw_df)
        
        load.load_books(mock_conn, books_df, location_map)
        
        # Assertions on the mock calls
        
        # 1. Check if the final DataFrame has the correct storage_location_id
        # Shelf A (id 1) appears twice, Shelf B (id 2) once, Shelf C (id 3) once
        expected_ids = [1, 2, 1, 3]
        actual_ids = books_df['storage_location_id'].tolist()
        self.assertListEqual(actual_ids, expected_ids)
        
        # 2. Check if executemany was called once with all 4 records
        # executemany is the high-performance way to insert multiple rows
        mock_cursor.executemany.assert_called_once()
        self.assertEqual(len(mock_cursor.executemany.call_args[0][1]), 4)
        
        # 3. Check for commit
        mock_conn.commit.assert_called_once()
        
# To run the tests, you can use: python -m unittest tests.unit_test
if __name__ == '__main__':
    unittest.main()