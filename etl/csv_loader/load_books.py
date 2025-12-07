import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text
import os
import sys
from validate import validate_book_data

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_HOST = os.getenv("POSTGRES_HOST")
    DB_PORT = os.getenv("POSTGRES_PORT")
    DB_NAME = os.getenv("POSTGRES_DB")
    
    if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
        print("Error: Database credentials not fully specified in environment variables.")
        sys.exit(1)

    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def get_db_connection():
    return create_engine(DATABASE_URL)

def generate_book_id(category_label, index):
    """
    Generate a book ID based on category and a running index.
    In a real scenario, we might want to read the existing max ID or use the CSV provided ID.
    For this loader, let's assume we generate IDs like 'A-001', 'A-002' if not provided,
    OR we assume the CSV *should* have an ID?
    
    The plan says: "Generate book IDs if not present".
    Let's assume we auto-increment based on existing count in DB for that category?
    That's risky for concurrency. 
    
    Simpler approach for this phase:
    Assume CSV *might* have 'book_id'. If not, we generate one.
    Let's try to generate purely based on sequential import for now.
    """
    return f"{category_label}-{str(index).zfill(3)}"

def load_data(file_path):
    print(f"Loading data from {file_path}...")
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
        
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        sys.exit(1)
        
    # Validate data
    if not validate_book_data(df):
        print("Skipping load due to validation errors.")
        sys.exit(1)
        
    engine = get_db_connection()
    
    with engine.connect() as conn:
        print("Connected to database.")
        
        for _, row in df.iterrows():
            try:
                # 1. Upsert Category
                # We assume category_label is unique
                cat_query = text("""
                    INSERT INTO categories (category_name, category_label)
                    VALUES (:name, :label)
                    ON CONFLICT (category_label) DO UPDATE 
                    SET category_name = EXCLUDED.category_name
                    RETURNING category_id;
                """)
                result = conn.execute(cat_query, {"name": row['category_name'], "label": row['category_label']})
                category_id = result.fetchone()[0]
                
                # 2. Upsert Location
                # We link location to category_label as per schema
                loc_query = text("""
                    INSERT INTO locations (location_name, category_label)
                    VALUES (:name, :label)
                    RETURNING location_id;
                """)
                # Check if location exists first to avoid duplicates if we don't have unique constraint on name+label
                # Schema: location_id PK. No unique constraint on (location_name, category_label) shown in plan, but good practice.
                # Let's just find or create.
                find_loc = text("SELECT location_id FROM locations WHERE location_name = :name AND category_label = :label")
                loc_res = conn.execute(find_loc, {"name": row['location'], "label": row['category_label']}).fetchone()
                
                if loc_res:
                    location_id = loc_res[0]
                else:
                    loc_res = conn.execute(loc_query, {"name": row['location'], "label": row['category_label']})
                    location_id = loc_res.fetchone()[0]
                
                # 3. Insert Book
                # Generate ID if we don't have one. 
                # Strategy: Find max ID for this category in DB to continue sequence?
                # Or just use a UUID? The requirement was "A-018".
                # Let's try to find the next available number for this category.
                # This is slow for bulk, but safe.
                
                # For this MVP, let's assume we just want to load them.
                # We'll generate a random-ish or sequential ID if we can't find one.
                # BETTER: Let's assume the CSV *provides* the number or we just use a simple counter for this batch.
                # Let's count existing books in this category.
                count_query = text("SELECT COUNT(*) FROM books WHERE category_id = :cat_id")
                count = conn.execute(count_query, {"cat_id": category_id}).fetchone()[0]
                
                # This is a naive ID generation, but works for initial load
                book_num = count + 1
                book_id = f"{row['category_label']}-{str(book_num).zfill(3)}"
                
                # Check if ID exists (collision check)
                while True:
                    check_id = conn.execute(text("SELECT 1 FROM books WHERE book_id = :id"), {"id": book_id}).fetchone()
                    if not check_id:
                        break
                    book_num += 1
                    book_id = f"{row['category_label']}-{str(book_num).zfill(3)}"
                
                insert_book = text("""
                    INSERT INTO books (book_id, name, category_id, storage_location_id, status)
                    VALUES (:id, :name, :cat_id, :loc_id, 'Available')
                    ON CONFLICT (book_id) DO NOTHING;
                """)
                conn.execute(insert_book, {
                    "id": book_id,
                    "name": row['book_name'],
                    "cat_id": category_id,
                    "loc_id": location_id
                })
                
            except Exception as e:
                print(f"Error processing row {row}: {e}")
                continue
                
        conn.commit()
        print("Data load complete.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python load_books.py <path_to_csv>")
        sys.exit(1)
    
    load_data(sys.argv[1])
