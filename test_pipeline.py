#!/usr/bin/env python
"""Quick pipeline test script"""
import sys
from loguru import logger
from database import init_db, SessionLocal, NewsItem
from news_service import NewsService
from pipeline_viral import ViralPipeline
import config

logger.info("=" * 60)
logger.info("=== PIPELINE LOCAL TEST ===")
logger.info("=" * 60)

# 1. Check configuration
logger.info("\n📋 Configuration Check:")
logger.info(f"  Publishing - YouTube: {config.ENABLE_PUBLISH_YOUTUBE}")
logger.info(f"  Publishing - Instagram: {config.ENABLE_PUBLISH_INSTAGRAM}")
logger.info(f"  Publishing - Facebook: {config.ENABLE_PUBLISH_FACEBOOK}")
logger.info(f"  LLM Provider: {config.LLM_PROVIDER}")
logger.info(f"  LLM Model: {config.LLM_MODEL}")
logger.info(f"  Database: {config.DATABASE_URL[:50]}...")

# 2. Initialize database
logger.info("\n💾 Initializing database...")
init_db()
logger.success("Database initialized")

# 3. Fetch news
logger.info("\n📰 Fetching news for 'general' category...")
ns = NewsService()
db = SessionLocal()

try:
    articles = ns.fetch_all_news(category_filter='general')
    logger.info(f"✅ Fetched {len(articles)} articles")
    
    if not articles:
        logger.error("❌ No articles fetched! Check your API keys in .env file")
        logger.info("Required keys: NEWS_API_KEY, GNEWS_API_KEY")
        sys.exit(1)
    
    # Show first 3 articles
    logger.info("\nTop 3 fetched articles:")
    for i, art in enumerate(articles[:3], 1):
        logger.info(f"  {i}. {art['title'][:70]}...")
    
    # 4. Rank and save to database
    logger.info("\n🏆 Ranking articles...")
    top_articles = ns.rank_and_filter(articles)
    logger.info(f"✅ Top {len(top_articles)} articles after ranking")
    
    logger.info("\n💾 Saving to database...")
    saved = ns.save_to_database(top_articles, db=db)
    logger.info(f"✅ Saved {len(saved)} articles to database")
    
    # 5. Check unused news
    unused_count = db.query(NewsItem).filter_by(used_in_post=False).count()
    total_count = db.query(NewsItem).count()
    logger.info(f"\n📊 Database status:")
    logger.info(f"  Total news items: {total_count}")
    logger.info(f"  Unused items: {unused_count}")
    
    if unused_count == 0:
        logger.error("❌ No unused news items! Cannot generate video.")
        logger.info("💡 Tip: Delete the database file and run again to fetch fresh news")
        sys.exit(1)
    
    # Show the top unused item
    top_unused = db.query(NewsItem).filter_by(used_in_post=False).order_by(NewsItem.score.desc()).first()
    if top_unused:
        logger.info(f"\n🎯 Top unused story:")
        logger.info(f"  Title: {top_unused.title}")
        logger.info(f"  Category: {top_unused.category}")
        logger.info(f"  Score: {top_unused.score:.2f}")
    
finally:
    db.close()

# 6. Run pipeline
logger.info("\n" + "=" * 60)
logger.info("🎬 Starting Viral Pipeline...")
logger.info("=" * 60)

pipeline = ViralPipeline()
result = pipeline.run(category_filter='general')

logger.info("\n" + "=" * 60)
if result:
    logger.success("✅ PIPELINE COMPLETED SUCCESSFULLY!")
    logger.info("\n📊 Results:")
    for platform, res in result.items():
        status = res.get('status', 'unknown')
        icon = "✅" if status == "success" else "⏭️" if status == "skipped" else "❌"
        logger.info(f"  {icon} {platform.capitalize()}: {status.upper()}")
        if res.get('error'):
            logger.info(f"      Error: {res.get('error')}")
    
    logger.info("\n📁 Check output/videos/ folder for generated video")
else:
    logger.error("❌ PIPELINE FAILED OR RETURNED NONE")
    logger.info("Check the logs above for error messages")
    sys.exit(1)

logger.info("=" * 60)
logger.info("=== TEST COMPLETE ===")
logger.info("=" * 60)
