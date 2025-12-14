
import pandas as pd
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_data(file_path: str) -> pd.DataFrame:
    """
    Extract data from CSV file.
    """
    logger.info(f"Extracting data from {file_path}")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found")
        
    data = pd.read_csv(file_path)
    print(data.head())
    return data

if __name__ == "__main__":
    # logical path to the data file assuming standard project structure
    # script is in etl/csv_loader/extract.py -> data is in data/book.csv
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(base_dir, 'data', 'book.csv')
    
    if os.path.exists(file_path):
        extract_data(file_path)
    else:
        print(f"File not found at {file_path}. Please check the path.")
