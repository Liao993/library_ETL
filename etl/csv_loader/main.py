

import os
import sys
import logging
from csv_loader.extract import extract_data
from csv_loader.transform import transform_data
from csv_loader.load import run_load_pipeline
from csv_loader.validation import run_validation

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Get the directory where this script is located
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up two levels to get to the project root
project_root = os.path.dirname(os.path.dirname(current_dir))
default_path = os.path.join(project_root, "data", "book.csv")

def run_pipeline(file_path: str):
    logger.info(f"Starting ETL pipeline for {file_path}")
    
    # 1. Extract
    df = extract_data(file_path)
    logger.info(f"Extracted {len(df)} rows.")
    
    
    # 2. Validate
    run_validation(df)
    
    # 3. Transform
    books_df, locations_df = transform_data(df)
    
    # 4. Load Locations (Dimension)
    run_load_pipeline(books_df, locations_df)
    
    logger.info("Pipeline finished successfully.")

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else default_path
    print(f"DEBUG: Calculated project_root: {project_root}")
    print(f"DEBUG: Target file_path: {file_path}")
    if os.path.exists(file_path):
        print("DEBUG: File exists.")
    else:
        print("DEBUG: File DOES NOT exist.")
    
    try:
        run_pipeline(file_path)
    except Exception as e:
        logger.error(f"ETL Pipeline Failed: {e}")
        sys.exit(1)

