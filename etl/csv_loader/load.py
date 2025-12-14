
import pandas as pd
import psycopg2
from psycopg2 import sql
from typing import Dict
from database import get_db_connection

def load_locations(conn, locations_df: pd.DataFrame) -> Dict[str, int]:
    """
    Loads unique locations into the locations table and returns a mapping
    of location_name -> location_id.
    """
    print("Loading unique locations...")
    cursor = conn.cursor()
    location_map = {}

    for index, row in locations_df.iterrows():
        location_name = row['location_name']
        
        # SQL to insert location and return the generated location_id
        insert_query = sql.SQL("""
            INSERT INTO locations (location_name)
            VALUES (%s)
            ON CONFLICT (location_name) DO NOTHING  -- Assuming you might add a UNIQUE constraint later
            RETURNING location_id;
        """)
        
        # We need a SELECT if the insert was ignored by ON CONFLICT
        select_query = sql.SQL("""
            SELECT location_id FROM locations WHERE location_name = %s;
        """)

        try:
            cursor.execute(insert_query, (location_name,))
            # Fetch the new ID if the insert was successful
            if cursor.rowcount > 0:
                location_id = cursor.fetchone()[0]
            else:
                # If ON CONFLICT was hit (location already exists), select the existing ID
                cursor.execute(select_query, (location_name,))
                location_id = cursor.fetchone()[0]

            location_map[location_name] = location_id
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Error loading location '{location_name}': {e}")
            raise

    conn.commit()
    print(f"Loaded {len(location_map)} unique locations.")
    return location_map

def load_books(conn, books_df: pd.DataFrame, location_map: Dict[str, int]) -> None:
    """
    Loads books into the books table using the location_name to storage_location_id map.
    """
    print("Loading books...")
    cursor = conn.cursor()
    
    # 1. Map the 'location' name in books_df to the actual 'storage_location_id'
    books_df['storage_location_id'] = books_df['location'].map(location_map)
    
    # Drop the temporary 'location' column
    books_df.drop(columns=['location'], inplace=True)
    
    # 2. Prepare for bulk insertion
    # Column names in the books table
    columns = ['book_id', 'name', 'book_category', 'book_category_label', 'storage_location_id', 'status']
    
    # Values to be inserted
    records = books_df[columns].values.tolist()
    
    # Prepare the INSERT statement
    insert_query = sql.SQL("""
        INSERT INTO books ({}) VALUES ({});
    """).format(
        sql.SQL(', ').join(map(sql.Identifier, columns)),
        sql.SQL(', ').join([sql.Placeholder() for _ in columns])
    )

    try:
        # Execute batch insertion (best practice for performance)
        cursor.executemany(insert_query, records)
        conn.commit()
        print(f"Loaded {len(records)} books.")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error loading books: {e}")
        raise

    finally:
        cursor.close()

def run_load_pipeline(books_df: pd.DataFrame, locations_df: pd.DataFrame) -> None:
    """Main function to orchestrate the database loading."""
    conn = None
    try:
        conn = get_db_connection()
        
        # STEP 1: Load Locations and get the mapping
        location_map = load_locations(conn, locations_df)
        
        # STEP 2: Load Books using the mapping
        load_books(conn, books_df, location_map)
        
        print("\n--- ✅ Database Load Successful! ---")
        
    except Exception as e:
        print(f"Pipeline failed: {e}")
        if conn:
            conn.rollback() # Ensure transaction is rolled back on error
            
    finally:
        if conn:
            conn.close()