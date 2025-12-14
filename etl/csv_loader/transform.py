
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform the dataframe to match database schema.
    """
    logger.info("Transforming data...")
    
    # Rename columns to match our internal logic
    # Category -> book_category
    # category_label -> book_category_label (and book_id)
    # book_name -> name
    # location -> location_name
    
    # Ensure columns exist before renaming to avoid errors
    expected_map = {
        'Category': 'book_category',
        'category_label': 'book_category_label',
        'book_name': 'name',
        'location': 'location_name'
    }
    
    # Filter map to only include keys present in df
    rename_map = {k: v for k, v in expected_map.items() if k in df.columns}
    
    df_transformed = df.rename(columns=rename_map)
    
    # Strip whitespace from all object columns
    for col in df_transformed.columns:
        if df_transformed[col].dtype == 'object':
            df_transformed[col] = df_transformed[col].str.strip()

    # Generate sequential book_id (01, 02...)
    # This assumes the input DF respects the order we want to assign IDs.
    if 'book_id' not in df_transformed.columns:
         df_transformed['book_id'] = (df_transformed.index + 1).astype(str).str.zfill(2)
         
    # Derive 'status' based on location
    # Rule: If location is '活動室', it is 'Available', otherwise it implies it is compiled/borrowed/unavailable
    if 'location_name' in df_transformed.columns:
        df_transformed['status'] = df_transformed['location_name'].apply(
            lambda x: 'Available' if x == '活動室' else 'On Loan'
        )
    else:
        # Default fallback
        df_transformed['status'] = 'Available'
    
    return df_transformed
