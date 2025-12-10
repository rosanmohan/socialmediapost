"""
Main entry point for the Social Media Agent
Can run as scheduler (24/7) or one-time execution
"""
import sys
import argparse
from loguru import logger
import config
from pipeline import Pipeline
from scheduler import Scheduler
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
        config.LOGS_DIR / "agent_{time}.log",
        rotation="1 day",
        retention="30 days",
        level="DEBUG"
    )

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Social Media Posting Agent")
    parser.add_argument(
        "--mode",
        choices=["run", "schedule"],
        default="schedule",
        help="Run mode: 'run' for one-time execution, 'schedule' for 24/7 scheduler"
    )
    parser.add_argument(
        "--slot",
        type=str,
        default="manual",
        help="Slot name for one-time run (used in run mode)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    
    # Initialize database
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized")
    
    if args.mode == "run":
        # One-time execution
        logger.info(f"Running one-time pipeline execution (slot: {args.slot})")
        pipeline = Pipeline()
        result = pipeline.run(slot_name=args.slot)
        
        if result["status"] == "success":
            logger.info("Pipeline execution completed successfully")
            logger.info(f"Post ID: {result.get('post_id')}")
            logger.info(f"Publish results: {result.get('publish_results', {})}")
            if result.get("warnings"):
                logger.warning(f"Warnings: {result.get('warnings', [])}")
        else:
            logger.error("Pipeline execution failed")
            logger.error(f"Errors: {result.get('errors', [])}")
            sys.exit(1)
    
    elif args.mode == "schedule":
        # 24/7 scheduler mode
        logger.info("Starting 24/7 scheduler mode...")
        scheduler = Scheduler()
        scheduler.run()

if __name__ == "__main__":
    main()


