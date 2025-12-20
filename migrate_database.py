"""
Database migration script to fix caption field size
Run this once to update the existing database schema
"""
from sqlalchemy import create_engine, text
import config
from loguru import logger

def migrate_caption_field():
    """Increase caption field size from 500 to 2000 characters"""
    engine = create_engine(config.DATABASE_URL, echo=True)
    
    try:
        with engine.connect() as conn:
            # Alter the caption column to support longer text
            logger.info("Migrating caption field from VARCHAR(500) to VARCHAR(2000)...")
            conn.execute(text("ALTER TABLE posts ALTER COLUMN caption TYPE VARCHAR(2000);"))
            conn.commit()
            logger.info("✅ Migration completed successfully!")
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        logger.info("If the error says 'column does not exist', the table might not be created yet.")
        logger.info("In that case, just run the main application and it will create tables with the correct schema.")
        raise

if __name__ == "__main__":
    migrate_caption_field()
