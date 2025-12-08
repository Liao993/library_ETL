import os
from sqlalchemy import create_engine
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_connection():
    """Create a database connection using environment variables."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Fallback to constructing from individual vars if DATABASE_URL not set
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "postgres")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5433")
        db = os.getenv("POSTGRES_DB", "library_system")
        db_url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    
    try:
        engine = create_engine(db_url)
        # Test connection
        with engine.connect() as conn:
            pass
        return engine
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise
