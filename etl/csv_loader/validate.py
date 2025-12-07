import pandas as pd
import great_expectations as ge
from great_expectations.core.expectation_configuration import ExpectationConfiguration
import sys
import os

def validate_book_data(df: pd.DataFrame) -> bool:
    """
    Validate the book dataframe using Great Expectations.
    Returns True if valid, False otherwise.
    """
    print("Starting data validation...")
    
    # Convert to GE DataFrame
    ge_df = ge.from_pandas(df)
    
    # Define expectations
    # 1. Required columns exist
    required_columns = ["category_name", "category_label", "book_name", "location"]
    for col in required_columns:
        ge_df.expect_column_to_exist(col)
        ge_df.expect_column_values_to_not_be_null(col)

    # 2. Category label format (e.g., "A", "B", "C") - assuming single letter for now based on plan
    # But user said "Category Dropdown: Fixed list of 3 categories (e.g., A, B, C)"
    # And "Manual Label Input: Teacher types the numeric portion (e.g., '018')"
    # The CSV might contain the full ID or separate parts. 
    # The plan says CSV has: category_name, category_label, book_name, location
    # Let's assume category_label in CSV is the prefix (A, B, C).
    
    # 3. Book name length
    ge_df.expect_column_value_lengths_to_be_between("book_name", min_value=1, max_value=255)
    
    # Run validation
    results = ge_df.validate()
    
    if not results["success"]:
        print("❌ Data Validation Failed!")
        for result in results["results"]:
            if not result["success"]:
                print(f"  - {result['expectation_config']['expectation_type']}: {result.get('result', {}).get('unexpected_percent', 0)}% unexpected")
        return False
    
    print("✅ Data Validation Passed!")
    return True
