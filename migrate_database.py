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
            # 1. Alter the caption column (Postgres specific syntax)
            logger.info("Updating caption field size...")
            if "postgresql" in config.DATABASE_URL:
                conn.execute(text("ALTER TABLE posts ALTER COLUMN caption TYPE VARCHAR(2000);"))
            else:
                logger.info("SQLite/Other DB detected, skipping Postgres-specific Type Alter.")
            
            # 2. Add category column to news_items if missing
            logger.info("Checking for 'category' column in news_items...")
            try:
                # This works for both Postgres and SQLite
                conn.execute(text("ALTER TABLE news_items ADD COLUMN category VARCHAR(50) DEFAULT 'general';"))
                conn.commit()
                logger.info("✅ Added 'category' column.")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    logger.info("ℹ️ 'category' column already exists.")
                else:
                    logger.warning(f"⚠️ Could not add column (it might already exist): {e}")
            
            conn.commit()
            logger.info("✅ Migration completed successfully!")

if __name__ == "__main__":
    migrate_caption_field()
