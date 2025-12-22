"""
Main entry point for Bulletin YouTube Shorts
Creates 20-second videos with top 5 news items and trending audio
"""
import sys
from loguru import logger
import config
from pipeline_viral import ViralPipeline
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
    
    # Run viral pipeline
    logger.info("Starting Viral Single-Story Pipeline (APPROVED STYLE)...")
    pipeline = ViralPipeline()
    result = pipeline.run()
    
    if result:  # ViralPipeline returns a dict of results
        logger.info("Viral pipeline completed.")
        
        # Check for any failures in enabled platforms
        failures = []
        status_lines = ["# 📊 Pipeline Execution Status\n"]
        has_critical_failure = False

        for platform, res in result.items():
            status = res.get("status", "unknown")
            error = res.get("error", "")
            icon = "✅" if status == "success" else "❌" if status == "failed" else "⏭️"
            status_lines.append(f"- {icon} **{platform.capitalize()}**: {status.upper()}")
            if error:
                status_lines.append(f"  - Error: `{error}`")
            
            if status == "failed":
                failures.append(platform)
                has_critical_failure = True

        # Write status to file for GitHub Actions to read
        with open("PIPELINE_STATUS.md", "w", encoding="utf-8") as f:
            f.write("\n".join(status_lines))

        if has_critical_failure:
            logger.error(f"❌ Pipeline finished with failures in: {', '.join(failures)}")
            sys.exit(1) # Exit with error so GitHub Actions can trigger alert
        else:
            logger.info("🎉 All platforms processed successfully!")
    else:
        logger.error("❌ Viral pipeline failed fundamentally (no result returned)")
        with open("PIPELINE_STATUS.md", "w") as f:
            f.write("# ❌ Pipeline Fatal Error\nThe pipeline crashed before completing publishing.")
        sys.exit(1)

if __name__ == "__main__":
    main()


