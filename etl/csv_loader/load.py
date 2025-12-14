
import pandas as pd
import sqlalchemy
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert
import logging
from typing import Dict, List, Optional
import sys
import os

# Add parent directory to path to import database module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from database import get_db_connection

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_locations(df: pd.DataFrame):
    """
    Ensure locations from the DataFrame exist in the database.
    This function is idempotent; it only inserts new locations.
    """
    logger.info("Loading locations...")
    
    if 'location_name' not in df.columns:
        logger.warning("No 'location_name' column found. Skipping location loading.")
        return

    # Extract unique locations
    unique_locations = df['location_name'].unique().tolist()
    # Clean out any potential NaNs
    unique_locations = [x for x in unique_locations if pd.notna(x) and x != '']
    
    if not unique_locations:
        logger.info("No locations found to load.")
        return

    engine = get_db_connection()
    with engine.begin() as conn:
        # 1. Get existing locations to minimize inserts
        try:
            existing = pd.read_sql("SELECT location_name FROM locations", conn)
            existing_set = set(existing['location_name'])
        except Exception as e:
            logger.warning(f"Could not read existing locations, assuming empty: {e}")
            existing_set = set()

        # 2. Identify new locations
        new_locations = set(unique_locations) - existing_set
        
        if new_locations:
            logger.info(f"Inserting {len(new_locations)} new locations")
            for loc in new_locations:
                conn.execute(text("INSERT INTO locations (location_name) VALUES (:loc)"), {"loc": loc})
        else:
            logger.info("No new locations to insert.")

def load_books(df: pd.DataFrame):
    """
    Load books into database.
    Maps location names to IDs and performs upsert on books.
    """
    logger.info("Loading books...")
    
    engine = get_db_connection()
    
    with engine.begin() as conn:
        # 1. Map Locations (if applicable)
        if 'location_name' in df.columns:
            logger.info("Mapping locations to IDs...")
            try:
                existing = pd.read_sql("SELECT location_id, location_name FROM locations", conn)
                location_map = dict(zip(existing['location_name'], existing['location_id']))
                
                # Map location names to IDs
                df['storage_location_id'] = df['location_name'].map(location_map)
            except Exception as e:
                logger.error(f"Failed to fetch locations for mapping: {e}")
                # We can't safely proceed if we can't map locations that are expected
                raise
        else:
             logger.warning("No 'location_name' column, skipping location linking.")
             df['storage_location_id'] = None
        
        # 2. Insert Books
        # Prepare records
        cols_to_insert = ['book_id', 'name', 'book_category', 'book_category_label', 'storage_location_id', 'status']
        valid_cols = [c for c in cols_to_insert if c in df.columns]
        
        books_to_insert = df[valid_cols].to_dict(orient='records')
        
        if not books_to_insert:
            logger.warning("No books to insert.")
            return

        # Reflect table to use SQLAlchemy Core properly
        meta = sqlalchemy.MetaData()
        try:
            books_table = sqlalchemy.Table('books', meta, autoload_with=conn)
        except sqlalchemy.exc.NoSuchTableError:
             logger.error("Table 'books' does not exist in the database.")
             raise

        stmt = insert(books_table).values(books_to_insert)
        
        # Upsert Logic:
        # On conflict (book_id), update everything
        do_update_stmt = stmt.on_conflict_do_update(
            index_elements=['book_id'],
            set_={
                'name': stmt.excluded.name,
                'book_category': stmt.excluded.book_category,
                'book_category_label': stmt.excluded.book_category_label,
                'storage_location_id': stmt.excluded.storage_location_id,
                'status': stmt.excluded.status,
                'updated_at': text("CURRENT_TIMESTAMP")
            }
        )
        
        result = conn.execute(do_update_stmt)
        logger.info(f"Loaded {result.rowcount} books (inserted/updated).")
