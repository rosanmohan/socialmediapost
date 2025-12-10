"""
Scheduler for running the Bulletin Pipeline (main_1.py) at specified times.
Schedule: 7:00 AM, 11:00 AM, 3:00 PM (15:00), 7:00 PM (19:00), 11:00 PM (23:00).
"""
import schedule
import time
import subprocess
import sys
import config
from loguru import logger
import pytz
from datetime import datetime

# Define the schedule times (24-hour format)
SCHEDULE_TIMES = ["07:00", "11:00", "15:00", "19:00", "23:00"]

def run_job():
    """Execute main_1.py using subprocess to ensure a clean state"""
    job_time = datetime.now().strftime("%H:%M:%S")
    logger.info(f"Starting scheduled job at {job_time}")
    
    try:
        # Run main_1.py as a separate process
        # This prevents any memory leaks or state issues from affecting the scheduler
        result = subprocess.run(
            [sys.executable, "main_1.py"],
            capture_output=True,
            text=True,
            check=False  # We handle return code manually
        )
        
        # Log the output from the subprocess
        if result.stdout:
            logger.info(f"Job Output:\n{result.stdout}")
        
        if result.returncode == 0:
            logger.info("Job completed successfully")
        else:
            logger.error(f"Job failed with return code {result.returncode}")
            if result.stderr:
                logger.error(f"Error Output:\n{result.stderr}")
                
    except Exception as e:
        logger.error(f"Failed to execute job: {e}")

def run_scheduler():
    """Main scheduler loop"""
    logger.add(
        "logs/scheduler_bulletin_{time}.log",
        rotation="1 day",
        retention="30 days",
        level="INFO"
    )
    
    logger.info("Starting Bulletin Scheduler...")
    logger.info(f"Scheduled times: {', '.join(SCHEDULE_TIMES)}")
    logger.info(f"Timezone: {config.TIMEZONE}")

    # Setup schedule
    for time_str in SCHEDULE_TIMES:
        schedule.every().day.at(time_str).do(run_job)
        logger.info(f"Scheduled job for {time_str}")

    # Run loop
    while True:
        try:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"Scheduler loop error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    run_scheduler()
