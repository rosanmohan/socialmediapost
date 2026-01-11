"""
Debug script to check configuration values
Run this in GitHub Actions to see what values are being loaded
"""
import os
import config
from loguru import logger

logger.info("=" * 60)
logger.info("CONFIGURATION DEBUG REPORT")
logger.info("=" * 60)

# Check environment variables directly
logger.info("\n📋 ENVIRONMENT VARIABLES (Raw):")
logger.info(f"  ENABLE_PUBLISH_YOUTUBE (env): {os.getenv('ENABLE_PUBLISH_YOUTUBE', 'NOT SET')}")
logger.info(f"  ENABLE_PUBLISH_INSTAGRAM (env): {os.getenv('ENABLE_PUBLISH_INSTAGRAM', 'NOT SET')}")
logger.info(f"  ENABLE_PUBLISH_FACEBOOK (env): {os.getenv('ENABLE_PUBLISH_FACEBOOK', 'NOT SET')}")

# Check config values
logger.info("\n⚙️ CONFIG VALUES (Parsed):")
logger.info(f"  ENABLE_PUBLISH_YOUTUBE: {config.ENABLE_PUBLISH_YOUTUBE}")
logger.info(f"  ENABLE_PUBLISH_INSTAGRAM: {config.ENABLE_PUBLISH_INSTAGRAM}")
logger.info(f"  ENABLE_PUBLISH_FACEBOOK: {config.ENABLE_PUBLISH_FACEBOOK}")

# Check credentials
logger.info("\n🔑 CREDENTIALS CHECK:")
logger.info(f"  YOUTUBE_CLIENT_ID: {'✅ SET' if config.YOUTUBE_CLIENT_ID else '❌ NOT SET'}")
logger.info(f"  YOUTUBE_CLIENT_SECRET: {'✅ SET' if config.YOUTUBE_CLIENT_SECRET else '❌ NOT SET'}")
logger.info(f"  YOUTUBE_REFRESH_TOKEN: {'✅ SET' if config.YOUTUBE_REFRESH_TOKEN else '❌ NOT SET'}")
logger.info(f"  FACEBOOK_ACCESS_TOKEN: {'✅ SET' if config.FACEBOOK_ACCESS_TOKEN else '❌ NOT SET'}")
logger.info(f"  FACEBOOK_PAGE_ID: {'✅ SET' if config.FACEBOOK_PAGE_ID else '❌ NOT SET'}")
logger.info(f"  INSTAGRAM_BUSINESS_ACCOUNT_ID: {'✅ SET' if config.INSTAGRAM_BUSINESS_ACCOUNT_ID else '❌ NOT SET'}")

# Check database
logger.info("\n💾 DATABASE:")
logger.info(f"  DATABASE_URL: {config.DATABASE_URL[:50]}..." if len(config.DATABASE_URL) > 50 else config.DATABASE_URL)

# Check LLM
logger.info("\n🤖 LLM CONFIGURATION:")
logger.info(f"  LLM_PROVIDER: {config.LLM_PROVIDER}")
logger.info(f"  LLM_MODEL: {config.LLM_MODEL}")
logger.info(f"  OPENAI_API_KEY: {'✅ SET' if config.OPENAI_API_KEY else '❌ NOT SET'}")
logger.info(f"  GROQ_API_KEY: {'✅ SET' if config.GROQ_API_KEY else '❌ NOT SET'}")

# Check news APIs
logger.info("\n📰 NEWS APIs:")
logger.info(f"  NEWS_API_KEY: {'✅ SET' if config.NEWS_API_KEY else '❌ NOT SET'}")
logger.info(f"  GNEWS_API_KEY: {'✅ SET' if config.GNEWS_API_KEY else '❌ NOT SET'}")

logger.info("\n" + "=" * 60)
logger.info("END OF DEBUG REPORT")
logger.info("=" * 60)
