"""
Scheduler for running the pipeline at specified times
Runs 24/7 and executes pipeline 2-3 times per day
"""
import schedule
import time
from datetime import datetime
from loguru import logger
import pytz
import config
from pipeline import Pipeline
from utils import send_notification

class Scheduler:
    """Scheduler for automated posting"""
    
    def __init__(self):
        self.pipeline = Pipeline()
        self.timezone = pytz.timezone(config.TIMEZONE)
        self.setup_schedule()
    
    def setup_schedule(self):
        """Setup scheduled jobs based on POST_TIMES"""
        logger.info(f"Setting up schedule for times: {config.POST_TIMES}")
        
        for post_time in config.POST_TIMES:
            post_time = post_time.strip()
            if post_time:
                # Schedule job
                schedule.every().day.at(post_time).do(self.run_scheduled_job, slot_name=post_time)
                logger.info(f"Scheduled job for {post_time}")
    
    def run_scheduled_job(self, slot_name: str):
        """Run pipeline for a scheduled slot"""
        logger.info(f"Running scheduled job: {slot_name}")
        send_notification(f"Starting scheduled job: {slot_name}", "info")
        
        try:
            result = self.pipeline.run(slot_name=slot_name)
            
            if result["status"] == "success":
                duration = result.get("duration_seconds", 0)
                logger.info(f"Job {slot_name} completed successfully in {duration:.1f}s")
            else:
                logger.warning(f"Job {slot_name} completed with errors: {result.get('errors', [])}")
                
        except Exception as e:
            logger.error(f"Error in scheduled job {slot_name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            send_notification(f"Error in scheduled job {slot_name}: {str(e)[:200]}", "error")
    
    def run(self):
        """Run scheduler loop (24/7)"""
        logger.info("Starting scheduler (24/7 mode)...")
        logger.info(f"Timezone: {config.TIMEZONE}")
        logger.info(f"Scheduled times: {config.POST_TIMES}")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    # Configure logging
    logger.add(
        config.LOGS_DIR / "scheduler_{time}.log",
        rotation="1 day",
        retention="30 days",
        level="INFO"
    )
    
    scheduler = Scheduler()
    scheduler.run()

