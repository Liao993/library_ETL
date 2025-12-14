import sys
import os
import logging
# Add parent directory (etl) to sys.path so we can import 'csv_loader' as a package
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from csv_loader.extract import extract_data
from csv_loader.transform import transform_data
from csv_loader.load import load_locations, load_books
from csv_loader.validation import validate_data

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
    
    # 2. Transform
    df_transformed = transform_data(df)
    logger.info("Transformation complete.")
    
    # 3. Validate
    validate_data(df_transformed)
    
    # 4. Load Locations (Dimension)
    load_locations(df_transformed)
    
    # 5. Load Books (Fact)
    load_books(df_transformed)
    
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

