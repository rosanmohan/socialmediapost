"""
Unified Scheduler for Viral Content Pipeline
Schedules posts for General, India, Cricket, and Movie news.
"""
import schedule
import time
import subprocess
import sys
import argparse
import config
from loguru import logger
from datetime import datetime
import pytz

# --- EXPLICIT SCHEDULE CONFIGURATION (IST) ---
# Format: "HH:MM" (24-hour format)
# The pipeline will run if the current IST time matches the hour (and minute tolerance)
SCHEDULE_CONFIG = {
    # Bollywood/Movies (Early morning, Mid-day, Evening)
    "movies": ["08:00", "13:00", "19:00"],
    
    # General News (Breakfast, Post-Lunch, Prime Time)
    "general": ["09:00", "14:00", "20:00"],
    
    # India National News (Late Morning, Evening, Late Night)
    "india": ["10:00", "15:00", "21:00"],
    
    # Cricket (Pre-match/Mid-day, Evening, Post-Match)
    "cricket": ["11:00", "16:00", "22:00"]
}

TIMEZONE = "Asia/Kolkata"

def run_viral_job(category: str):
    """Execute pipeline_viral.py with category argument"""
    job_time = datetime.now(pytz.timezone(TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"🚀 Starting Viral {category.upper()} Pipeline at {job_time}")
    
    try:
        # Run pipeline_viral.py with --category flag
        cmd = [sys.executable, "pipeline_viral.py", "--category", category]
        
        # Stream output in real-time
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1) as proc:
            for line in proc.stdout:
                print(line, end='') # Print directly to console for GitHub Actions logs
        
        if proc.returncode == 0:
            logger.info(f"✅ {category.upper()} pipeline completed successfully")
        else:
            logger.error(f"❌ {category.upper()} pipeline failed (Code {proc.returncode})")

    except Exception as e:
        logger.error(f"Critical failure in {category} job execution: {e}")

def run_cron_check():
    """
    Check current time against the explicit schedule and run job if valid.
    Designed for GitHub Actions to run every hour.
    """
    # 1. Get current time in correct timezone
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    current_hour = now.hour
    
    logger.info(f"⏰ Cron Check initiated. Current Time (IST): {now.strftime('%H:%M')}")
    
    active_job_found = False
    
    # 2. Check all schedules
    for category, times in SCHEDULE_CONFIG.items():
        for time_str in times:
            # Parse scheduled hour
            scheduled_h = int(time_str.split(":")[0])
            
            # Check if we are in the matching hour
            # (Strict logic: exact hour match. Since cron runs at start of hour, this works)
            if current_hour == scheduled_h:
                logger.info(f"🎯 Time verified! Matched schedule for [{category.upper()}] at {time_str}")
                run_viral_job(category)
                active_job_found = True
                
    if not active_job_found:
        logger.info("💤 No jobs scheduled for this hour.")

def start_loop_scheduler():
    """Start the persistent scheduler loop (Local Machine Mode)"""
    logger.add(
        "logs/scheduler_viral_{time}.log",
        rotation="1 day",
        retention="30 days",
        level="INFO"
    )
    
    logger.info("🎬 Starting Persistent Viral Content Scheduler (Loop Mode)...")
    
    # Setup schedules using 'schedule' library
    for category, times in SCHEDULE_CONFIG.items():
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
    parser = argparse.ArgumentParser(description="Viral Content Scheduler")
    parser.add_argument("--cron", action="store_true", help="Run in one-off CRON check mode (for GitHub Actions)")
    args = parser.parse_args()
    
    if args.cron:
        run_cron_check()
    else:
        start_loop_scheduler()
