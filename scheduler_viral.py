"""
Unified Scheduler for Viral Content Pipeline
Schedules posts for General, India, Cricket, and Movie news.
Total 12 posts per day (4 categories * 3 times each).
"""
import schedule
import time
import subprocess
import sys
import config
from loguru import logger
from datetime import datetime

def run_viral_job(category: str):
    """Execute pipeline_viral.py with category argument"""
    job_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"🚀 Starting scheduled Viral {category.upper()} job at {job_time}")
    
    try:
        # Run pipeline_viral.py with --category flag
        cmd = [sys.executable, "pipeline_viral.py", "--category", category]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            logger.info(f"[{category}] Output:\n{result.stdout[-1000:]}") # Last 1000 chars
            
        if result.returncode == 0:
            logger.info(f"✅ {category.upper()} job completed successfully")
        else:
            logger.error(f"❌ {category.upper()} job failed (Code {result.returncode})")
            if result.stderr:
                logger.error(f"Error Output:\n{result.stderr}")
                
    except Exception as e:
        logger.error(f"Critical failure in {category} job execution: {e}")

def start_scheduler():
    """Start the main scheduler loop"""
    logger.add(
        "logs/scheduler_viral_{time}.log",
        rotation="1 day",
        retention="30 days",
        level="INFO"
    )
    
    logger.info("🎬 Starting Unified Viral Content Scheduler...")
    
    # Define category to schedule mapping
    schedule_map = {
        "general": config.POST_TIMES,
        "india": config.INDIA_POST_TIMES,
        "cricket": config.CRICKET_POST_TIMES,
        "movies": config.MOVIES_POST_TIMES
    }
    
    # Setup schedules
    for category, times in schedule_map.items():
        for time_str in times:
            schedule.every().day.at(time_str).do(run_viral_job, category=category)
            logger.info(f"📅 Scheduled {category.upper()} post for {time_str}")

    logger.info("Waiting for next scheduled post...")
    
    # Run loop
    while True:
        try:
            schedule.run_pending()
            time.sleep(30)
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"Scheduler loop error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    start_scheduler()
