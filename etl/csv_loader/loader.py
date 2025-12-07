import os
import sys
import pandas as pd
import uuid
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.sql import func

# Setup Database Connection
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable is not set.")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Model Definitions (Replicated from backend to keep ETL independent) ---

class Category(Base):
    __tablename__ = "categories"
    
    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(100), nullable=False)
    category_label = Column(String(50), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Location(Base):
    __tablename__ = "locations"
    
    location_id = Column(Integer, primary_key=True, index=True)
    category_label = Column(String(50), ForeignKey("categories.category_label", ondelete="SET NULL"))
    location_name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Book(Base):
    __tablename__ = "books"
    
    book_id = Column(String(50), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.category_id", ondelete="SET NULL"))
    storage_location_id = Column(Integer, ForeignKey("locations.location_id", ondelete="SET NULL"))
    status = Column(String(20), default="Available", nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# --- Loader Logic ---

def load_data():
    csv_path = '/data/book.csv' # Path inside the container (mounted to /data)
    
    print(f"Reading data from {csv_path}...")
    
    if not os.path.exists(csv_path):
        print(f"Error: File not found at {csv_path}")
        return

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    db = SessionLocal()
    
    try:
        print("Starting ingestion...")
        
        # Cache for performance
        category_cache = {} # label -> id
        location_cache = {} # name -> id
        
        # Pre-fill cache from DB to avoid duplicates if re-running
        existing_cats = db.query(Category).all()
        for c in existing_cats:
            category_cache[c.category_label] = c.category_id
            
        existing_locs = db.query(Location).all()
        for l in existing_locs:
            location_cache[l.location_name] = l.location_id
        
        books_to_add = []
        
        for index, row in df.iterrows():
            # 1. Handle Category
            cat_name = row.get('Category')
            cat_label = row.get('category_label')
            
            # Skip if essential data is missing
            if pd.isna(cat_name) or pd.isna(cat_label):
                print(f"Skipping row {index}: Missing Category or category_label")
                continue
                
            cat_name = str(cat_name).strip()
            cat_label = str(cat_label).strip()
            
            if cat_label not in category_cache:
                # Check DB again (just in case)
                category = db.query(Category).filter(Category.category_label == cat_label).first()
                if not category:
                    category = Category(
                        category_name=cat_name,
                        category_label=cat_label
                    )
                    db.add(category)
                    db.flush() # Get ID
                    print(f"Created Category: {cat_name} ({cat_label})")
                category_cache[cat_label] = category.category_id
            
            cat_id = category_cache[cat_label]
            
            # 2. Handle Location
            loc_name = row.get('Location')
            if pd.isna(loc_name) or str(loc_name).strip() == '':
                loc_name = "未分類"
            else:
                loc_name = str(loc_name).strip()
            
            if loc_name not in location_cache:
                location = db.query(Location).filter(Location.location_name == loc_name).first()
                if not location:
                    location = Location(
                        location_name=loc_name,
                        # Linking to category is ambiguous in CSV, leaving null or could link to current cat_label
                        # For now, following original logic: just create it.
                    )
                    db.add(location)
                    db.flush()
                    print(f"Created Location: {loc_name}")
                location_cache[loc_name] = location.location_id
                
            loc_id = location_cache[loc_name]
            
            # 3. Create Book
            book_name = row.get('book_name')
            if pd.isna(book_name):
                continue
                
            book_name = str(book_name).strip()
            
            # Check if book already exists (simple check by name + category? or just assume new?)
            # Original script generated new UUID every time. 
            # To be safe/idempotent, we might want to check, but for now let's follow original logic 
            # but maybe check if a book with same name exists in that location?
            # For bulk load, let's just insert.
            
            book_id = str(uuid.uuid4())
            
            book = Book(
                book_id=book_id,
                name=book_name,
                category_id=cat_id,
                storage_location_id=loc_id,
                status="Available"
            )
            books_to_add.append(book)
        
        # Bulk save books
        if books_to_add:
            db.bulk_save_objects(books_to_add)
            print(f"Prepared {len(books_to_add)} books for insertion.")
            
        db.commit()
        print("Ingestion completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    load_data()
