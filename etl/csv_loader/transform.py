# transform.py

import pandas as pd
import uuid

def generate_book_id():
    """Generates a unique, short, and URL-safe ID."""
    # Using a truncated UUID for a unique VARCHAR(50) ID
    return str(uuid.uuid4()).replace('-', '')[:32]

def transform_data(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Performs normalization and transformation steps on the raw DataFrame.

    Returns:
        A tuple: (books_df, locations_df)
    """
    print("Starting data transformation...")
    
    # 1. Create the Locations DataFrame (Normalization Step 1)
    # Extract unique locations and assign a temporary ID for mapping.
    # We will let the database assign the final location_id (SERIAL PRIMARY KEY).
    # This DF is ready for insertion into the 'locations' table.
    locations_df = raw_df[['location']].drop_duplicates().reset_index(drop=True)
    locations_df.rename(columns={'location': 'location_name'}, inplace=True)
    # The 'location_name' is used as the lookup key during the load process.
    
    # 2. Prepare the Books DataFrame (Normalization Step 2)
    books_df = raw_df[['category', 'category_label', 'book_name', 'location']].copy()
    
    # Add a unique book_id
    books_df['book_id'] = [generate_book_id() for _ in range(len(books_df))]
    
    # Add default status column
    # The database has a default, but it's often cleaner to explicitly set it here
    # to maintain consistency if the database schema ever changes.
    books_df['status'] = 'Available'
    
    # IMPORTANT: The 'storage_location_id' column in books_df needs the
    # actual location_id *after* the locations have been loaded into the DB.
    # For now, we keep the original 'location' name to be used as a foreign key
    # lookup during the loading phase. We will drop this column and replace it
    # with 'storage_location_id' in load.py.
    
    # Final Columns for Books table: book_id, name, book_category, book_category_label,
    # storage_location_id (will be added later), status
    books_df.rename(columns={'book_name': 'name', 
                             'category': 'book_category', 
                             'category_label': 'book_category_label'}, 
                    inplace=True)
    
    print("Transformation complete.")
    return books_df, locations_df

