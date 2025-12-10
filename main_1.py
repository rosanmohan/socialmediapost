"""
Main entry point for Bulletin YouTube Shorts
Creates 20-second videos with top 5 news items and trending audio
"""
import sys
from loguru import logger
import config
from pipeline_bulletin import BulletinPipeline
from database import init_db

def setup_logging():
    """Configure logging"""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    logger.add(
        config.LOGS_DIR / "bulletin_{time}.log",
        rotation="1 day",
        retention="30 days",
        level="DEBUG"
    )

def main():
    """Main entry point for bulletin videos"""
    # Setup logging
    setup_logging()
    
    # Initialize database
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized")
    
    # Run bulletin pipeline
    logger.info("Starting bulletin pipeline for 20-second YouTube Shorts...")
    pipeline = BulletinPipeline()
    result = pipeline.run()
    
    if result["status"] == "success":
        logger.info("Bulletin pipeline completed successfully")
        logger.info(f"Post ID: {result.get('post_id')}")
        logger.info(f"Publish results: {result.get('publish_results', {})}")
        if result.get("warnings"):
            logger.warning(f"Warnings: {result.get('warnings', [])}")
    else:
        logger.error("Bulletin pipeline failed")
        logger.error(f"Errors: {result.get('errors', [])}")
        if result.get("warnings"):
            logger.warning(f"Warnings: {result.get('warnings', [])}")
        sys.exit(1)

if __name__ == "__main__":
    main()


