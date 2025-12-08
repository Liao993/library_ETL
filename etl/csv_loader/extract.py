
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
    
    return pd.read_csv(file_path)
