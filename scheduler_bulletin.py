"""
Scheduler for running the Bulletin Pipeline (main.py) which creates Top 5 News videos.
Schedule: 08:00 AM, 01:00 PM (13:00), 06:00 PM (18:00).
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
SCHEDULE_CONFIG = {
    "bulletin": ["08:00", "13:00", "18:00"]
}

TIMEZONE = "Asia/Kolkata"

def setup_logging():
    """Configure file logging"""
    os.makedirs("logs", exist_ok=True)
    logger.add(
        "logs/scheduler_bulletin_{time}.log",
        rotation="1 day",
        retention="30 days",
        level="INFO"
    )

def write_status_file(status_lines):
    """Write the status file for GitHub Actions"""
    with open("PIPELINE_STATUS.md", "a", encoding="utf-8") as f:
        # Append to existing file (since viral scheduler might have run first)
        f.write("\n\n" + "\n".join(status_lines))

def run_bulletin_job():
    """Execute main.py"""
    job_time = datetime.now(pytz.timezone(TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"🚀 Starting Bulletin Pipeline (main.py) at {job_time}")
    
    status_lines = [f"# 📊 Bulletin Pipeline Execution", f"**Time:** {job_time}\n"]
    
    try:
        # Run main.py
        cmd = [sys.executable, "main.py"]
        
        # Stream output in real-time
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1) as proc:
            for line in proc.stdout:
                print(line, end='') # Print directly to console
            proc.wait() 
        
        if proc.returncode == 0:
            logger.info(f"✅ Bulletin pipeline completed successfully")
            status_lines.append(f"- ✅ **Status**: SUCCESS")
        else:
            logger.error(f"❌ Bulletin pipeline failed (Code {proc.returncode})")
            status_lines.append(f"- ❌ **Status**: FAILED (Exit Code {proc.returncode})")

    except Exception as e:
        logger.error(f"Critical failure in Bulletin job execution: {e}")
        status_lines.append(f"- ❌ **Critical Error**: {str(e)}")
    
    write_status_file(status_lines)

def run_cron_check():
    """
    Check current time against the explicit schedule and run job if valid.
    """
    setup_logging()
    
    # 1. Get current time in correct timezone
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    current_hour = now.hour
    
    logger.info(f"⏰ Bulletin Cron Check initiated. Current Time (IST): {now.strftime('%H:%M')}")
    
    active_job_found = False
    
    # 2. Check schedule
    for time_str in SCHEDULE_CONFIG["bulletin"]:
        scheduled_h = int(time_str.split(":")[0])
        
        if current_hour == scheduled_h:
            logger.info(f"🎯 Time verified! Matched BULLETIN schedule at {time_str}")
            run_bulletin_job()
            active_job_found = True
                
    if not active_job_found:
        logger.info("💤 No Bulletin jobs scheduled for this hour.")

def start_loop_scheduler():
    """Start the persistent scheduler loop (Local Machine Mode)"""
    setup_logging()
    
    logger.info("🎬 Starting Persistent Bulletin Scheduler (Loop Mode)...")
    
    # Setup schedules
    for time_str in SCHEDULE_CONFIG["bulletin"]:
        schedule.every().day.at(time_str).do(run_bulletin_job)
        logger.info(f"📅 Scheduled Bulletin post for {time_str}")

    logger.info("Waiting for next scheduled post...")
    
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
    parser = argparse.ArgumentParser(description="Bulletin Video Scheduler")
    parser.add_argument("--cron", action="store_true", help="Run in one-off CRON check mode (for GitHub Actions)")
    args = parser.parse_args()
    
    if args.cron:
        run_cron_check()
    else:
        start_loop_scheduler()
