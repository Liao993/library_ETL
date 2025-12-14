# validation.py

import pandas as pd
from great_expectations.dataset import PandasDataset
from great_expectations.core.batch import Batch

def run_validation(df: pd.DataFrame) -> None:
    """
    Validates the raw DataFrame using Great Expectations against schema rules.
    Raises an error if validation fails.
    """
    print("Starting data validation...")
    
    # 1. Create a Great Expectations Dataset object
    # We use a simple PandasDataset here for easy integration
    ge_df = PandasDataset(df)

    # 2. Define Expectations
    # --- Checks based on the database schema constraints ---

    # Core columns should exist
    ge_df.expect_column_to_exist(column="category")
    ge_df.expect_column_to_exist(column="category_label")
    ge_df.expect_column_to_exist(column="book_name")
    ge_df.expect_column_to_exist(column="location")

    # Key columns for books/locations should not be null/empty
    ge_df.expect_column_values_to_not_be_null(column="book_name")
    ge_df.expect_column_values_to_not_be_null(column="location")
    ge_df.expect_column_values_to_not_be_null(column="category")

   
    
    # Text columns should not be excessively long (e.g., prevent overflow in VARCHAR fields)
    ge_df.expect_column_value_lengths_to_be_between(column="category", max_value=50)
    ge_df.expect_column_value_lengths_to_be_between(column="category_label", max_value=50)
    ge_df.expect_column_value_lengths_to_be_between(column="book_name", max_value=255)
    ge_df.expect_column_value_lengths_to_be_between(column="location", max_value=100)

    # 3. Run Validation and Check Results
    validation_result = ge_df.validate()

    if not validation_result["success"]:
        print("--- ❌ Data Validation Failed! ---")
        # Print a summary or detailed results
        for result in validation_result["results"]:
            if not result["success"]:
                print(f"Failed Expectation: {result['expectation_config'].get('expectation_type', 'Unknown')}")
                # Optional: print specific details of the failure
        raise ValueError("Data quality check failed. Please review the raw data.")
    
    print("--- ✅ Data Validation Succeeded! ---")