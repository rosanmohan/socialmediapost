"""
Unified Scheduler for Viral Content Pipeline
Schedules posts for General, India, Cricket, and Movie news.
"""
import schedule
import time
import os
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
    "movies": [],
    
    # General News (Breakfast, Post-Lunch, Prime Time)
    "general": [],
    
    # India National News (Late Morning, Evening, Late Night)
    "india": [],
    
    # Cricket (Pre-match/Mid-day, Evening, Post-Match)
    "cricket": []
}

TIMEZONE = "Asia/Kolkata"

def setup_logging():
    """Configure file logging"""
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    logger.add(
        "logs/scheduler_viral_{time}.log",
        rotation="1 day",
        retention="30 days",
        level="INFO"
    )

def write_status_file(status_lines):
    """Write the status file for GitHub Actions"""
    with open("PIPELINE_STATUS.md", "w", encoding="utf-8") as f:
        f.write("\n".join(status_lines))

def run_viral_job(category: str):
    """Execute pipeline_viral.py with category argument"""
    job_time = datetime.now(pytz.timezone(TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"🚀 Starting Viral {category.upper()} Pipeline at {job_time}")
    
    status_lines = [f"# 📊 Pipeline Execution Status: {category.upper()}", f"**Time:** {job_time}\n"]
    
    try:
        # Run pipeline_viral.py with --category flag
        cmd = [sys.executable, "pipeline_viral.py", "--category", category]
        
        # Stream output in real-time
        # Stream output in real-time
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1) as proc:
            for line in proc.stdout:
                print(line, end='') # Print directly to console for GitHub Actions logs
            proc.wait() # Ensure process finishes
        
        if proc.returncode == 0:
            logger.info(f"✅ {category.upper()} pipeline completed successfully")
            status_lines.append(f"- ✅ **Status**: SUCCESS")
            status_lines.append(f"- 📂 **Category**: {category}")
        else:
            logger.error(f"❌ {category.upper()} pipeline failed (Code {proc.returncode})")
            status_lines.append(f"- ❌ **Status**: FAILED (Exit Code {proc.returncode})")
            status_lines.append(f"- 📂 **Category**: {category}")

    except Exception as e:
        logger.error(f"Critical failure in {category} job execution: {e}")
        status_lines.append(f"- ❌ **Critical Error**: {str(e)}")
    
    write_status_file(status_lines)

def run_cron_check():
    """
    Check current time against the explicit schedule and run job if valid.
    Designed for GitHub Actions to run every hour.
    """
    setup_logging()
    
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
            if current_hour == scheduled_h:
                logger.info(f"🎯 Time verified! Matched schedule for [{category.upper()}] at {time_str}")
                run_viral_job(category)
                active_job_found = True
                
    if not active_job_found:
        logger.info("💤 No jobs scheduled for this hour.")
        write_status_file([
            "# 💤 Pipeline Skipped",
            f"**Time:** {now.strftime('%Y-%m-%d %H:%M:%S')} IST",
            f"No jobs scheduled for hour: {current_hour}:00"
        ])

def start_loop_scheduler():
    """Start the persistent scheduler loop (Local Machine Mode)"""
    setup_logging()
    
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
