
import pandas as pd
import logging
import great_expectations as gx

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_data(df: pd.DataFrame) -> bool:
    """
    Validate dataframe using Great Expectations.
    Returns True if valid, raises Exception if invalid.
    """
    logger.info("Validating data with Great Expectations...")
    
    # Convert pandas DF to GE DF
    # We can use an ephemeral context or just wrap the dataframe
    ge_df = gx.from_pandas(df)
    
    # Define expectations
    
    # 1. Critical columns must exist and not be null
    critical_cols = ['book_category', 'book_category_label', 'name', 'location_name']
    for col in critical_cols:
        # Expect column to exist
        res = ge_df.expect_column_to_exist(col)
        if not res["success"]:
            raise ValueError(f"Column {col} missing: {res}")
            
        # Expect values to not be null
        res = ge_df.expect_column_values_to_not_be_null(col)
        if not res["success"]:
             # If strict, raise error.
             logger.warning(f"Column {col} contains null values. This might cause DB errors.")
             # For this strict requirement, let's fail
             raise ValueError(f"Column {col} has null values: {res['result']}")

    # 2. Data Types
    # Expect book_category to be string
    ge_df.expect_column_values_to_be_of_type("book_category", "object")
    ge_df.expect_column_values_to_be_of_type("name", "object")
    
    # 3. Custom: book_id should be unique in this batch (it is generated mechanically, so it should be, but good to check)
    ge_df.expect_column_values_to_be_unique("book_id")
    
    # Validate
    validation_result = ge_df.validate()
    
    if not validation_result["success"]:
        logger.error("Great Expectations Validation Failed!")
        # Log failure details
        for res in validation_result["results"]:
            if not res["success"]:
                logger.error(f"Failed expectation: {res['expectation_config']['expectation_type']} on {res['expectation_config']['kwargs']}")
        raise ValueError("Data Validation Failed via Great Expectations")
        
    logger.info("Data Validation Passed.")
    return True
