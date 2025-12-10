"""
Quick start script to test individual components
Useful for debugging and setup verification
"""
import sys
from loguru import logger
import config
from database import init_db
from news_service import NewsService
from content_generator import ContentGenerator
from media_generator import MediaGenerator

def test_news_service():
    """Test news fetching"""
    logger.info("Testing News Service...")
    service = NewsService()
    news = service.get_top_news()
    if news:
        logger.info(f"✓ News service working. Found {len(news)} articles")
        logger.info(f"  Top article: {news[0].get('title', 'N/A')[:50]}...")
        return True
    else:
        logger.error("✗ News service failed - no articles found")
        return False

def test_content_generator():
    """Test content generation"""
    logger.info("Testing Content Generator...")
    generator = ContentGenerator()
    test_title = "Breaking: AI achieves new milestone in technology"
    test_desc = "Scientists have made a breakthrough in artificial intelligence research."
    
    content = generator.generate_content(test_title, test_desc, "https://example.com")
    if content and content.get("script"):
        logger.info("✓ Content generator working")
        logger.info(f"  Generated script length: {len(content.get('script', ''))} chars")
        return True
    else:
        logger.error("✗ Content generator failed")
        return False

def test_media_generator():
    """Test media generation (without full video)"""
    logger.info("Testing Media Generator...")
    try:
        generator = MediaGenerator()
        logger.info("✓ Media generator initialized")
        
        # Test TTS
        test_text = "This is a test of the text to speech system."
        audio_path = generator._generate_tts(test_text, "test")
        if audio_path:
            logger.info(f"✓ TTS working. Audio saved to: {audio_path}")
            return True
        else:
            logger.error("✗ TTS failed")
            return False
    except Exception as e:
        logger.error(f"✗ Media generator error: {e}")
        return False

def test_database():
    """Test database"""
    logger.info("Testing Database...")
    try:
        init_db()
        logger.info("✓ Database initialized")
        return True
    except Exception as e:
        logger.error(f"✗ Database error: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("=" * 50)
    logger.info("Social Media Agent - Quick Start Test")
    logger.info("=" * 50)
    
    results = {}
    
    # Test database
    results["database"] = test_database()
    print()
    
    # Test news service
    results["news"] = test_news_service()
    print()
    
    # Test content generator
    results["content"] = test_content_generator()
    print()
    
    # Test media generator
    results["media"] = test_media_generator()
    print()
    
    # Summary
    logger.info("=" * 50)
    logger.info("Test Summary:")
    logger.info("=" * 50)
    for component, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{component.upper():15} {status}")
    
    all_passed = all(results.values())
    if all_passed:
        logger.info("\n✓ All components working! You can start the agent.")
        return 0
    else:
        logger.error("\n✗ Some components failed. Please check configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())



