"""
Main pipeline orchestrator
Coordinates all components to create and publish content
"""
from loguru import logger
from datetime import datetime
from typing import Optional, Dict
import config
from database import SessionLocal, NewsItem, Post, PublishLog, SystemLog
from news_service import NewsService
from content_generator import ContentGenerator
from media_generator import MediaGenerator
from publishers import PublisherManager
from utils import send_notification, format_duration
import time

class Pipeline:
    """Main pipeline for automated content creation and publishing"""
    
    def __init__(self):
        self.news_service = NewsService()
        self.content_generator = ContentGenerator()
        self.media_generator = MediaGenerator()
        self.publisher_manager = PublisherManager()
    
    def run(self, slot_name: str = "default") -> Dict:
        """Run the complete pipeline"""
        logger.info(f"Starting pipeline run: {slot_name}")
        start_time = datetime.utcnow()
        
        result = {
            "slot": slot_name,
            "start_time": start_time,
            "status": "failed",
            "post_id": None,
            "errors": []
        }
        
        db = SessionLocal()
        
        try:
            # Step 1: Fetch and select news
            logger.info("Step 1: Fetching news...")
            news_items = self.news_service.get_top_news()
            
            if not news_items:
                logger.warning("No news items found")
                result["errors"].append("No news items found")
                return result
            
            # Save news to database
            saved_items_info = self.news_service.save_to_database(news_items)
            
            # Get news item from database (ensures it's bound to current session)
            # IMPORTANT: Always select UNUSED news to avoid duplicates
            selected_news = None
            
            # First, try to find unused news from the newly saved items
            if saved_items_info:
                for item_info in saved_items_info:
                    news_item = db.query(NewsItem).filter_by(id=item_info["id"]).first()
                    if news_item and not news_item.used_in_post:
                        selected_news = news_item
                        logger.info(f"Selected unused news from new items: {news_item.title[:50]}...")
                        break
            
            # If no unused news in new items, get any unused news from database
            if not selected_news:
                selected_news = db.query(NewsItem).filter_by(used_in_post=False).order_by(NewsItem.score.desc()).first()
                if selected_news:
                    logger.info(f"Selected unused news from database: {selected_news.title[:50]}...")
            
            # If still no unused news, check if we can reuse old news (older than 7 days)
            if not selected_news:
                from datetime import timedelta
                cutoff_date = datetime.utcnow() - timedelta(days=7)
                selected_news = db.query(NewsItem).filter(
                    NewsItem.used_at < cutoff_date
                ).order_by(NewsItem.score.desc()).first()
                if selected_news:
                    logger.info(f"Reusing old news (older than 7 days): {selected_news.title[:50]}...")
                    # Reset the used flag
                    selected_news.used_in_post = False
                    selected_news.used_at = None
                    db.commit()
            
            # Last resort: use any news item (even if used recently) - prefer newly saved items
            if not selected_news:
                # First try newly saved items
                if saved_items_info:
                    for item_info in saved_items_info:
                        news_item = db.query(NewsItem).filter_by(id=item_info["id"]).first()
                        if news_item:
                            selected_news = news_item
                            logger.warning(f"Reusing newly saved news (no unused news available): {news_item.title[:50]}...")
                            # Reset the used flag
                            selected_news.used_in_post = False
                            selected_news.used_at = None
                            db.commit()
                            break
                
                # If still nothing, use any news item from database
                if not selected_news:
                    selected_news = db.query(NewsItem).order_by(NewsItem.score.desc()).first()
                    if selected_news:
                        logger.warning(f"Using any available news (no unused news available): {selected_news.title[:50]}...")
                        # Reset the used flag
                        selected_news.used_in_post = False
                        selected_news.used_at = None
                        db.commit()
            
            if not selected_news:
                logger.error("No news items available in database")
                result["errors"].append("No news items available in database")
                return result
            
            logger.info(f"Selected news: {selected_news.title[:50]}...")
            
            # Step 2: Generate content
            logger.info("Step 2: Generating content...")
            content = self.content_generator.generate_content(
                selected_news.title,
                selected_news.description or "",
                selected_news.url
            )
            
            if not content:
                logger.error("Content generation failed")
                result["errors"].append("Content generation failed")
                return result
            
            # Step 3: Generate video
            logger.info("Step 3: Generating video...")
            video_path = self.media_generator.generate_video(content, selected_news.title)
            
            if not video_path:
                logger.error("Video generation failed")
                result["errors"].append("Video generation failed")
                return result
            
            # Step 4: Generate thumbnail
            logger.info("Step 4: Generating thumbnail...")
            thumbnail_path = self.media_generator.generate_thumbnail(selected_news.title)
            
            # Step 5: Save post to database
            logger.info("Step 5: Saving post to database...")
            post = Post(
                news_id=selected_news.id,
                script=content.get("script", ""),
                caption=content.get("caption", ""),
                hashtags=",".join(content.get("hashtags", [])),
                video_path=video_path,
                thumbnail_path=thumbnail_path
            )
            db.add(post)
            db.commit()
            db.refresh(post)
            
            # Mark news as used
            selected_news.used_in_post = True
            selected_news.used_at = datetime.utcnow()
            db.commit()
            
            # Step 6: Publish to all platforms
            logger.info("Step 6: Publishing to platforms...")
            publish_results = self.publisher_manager.publish_all(video_path, content)
            
            # Step 7: Log publishing results
            logger.info("Step 7: Logging publish results...")
            for platform, publish_result in publish_results.items():
                publish_log = PublishLog(
                    post_id=post.id,
                    platform=platform,
                    status=publish_result.get("status", "failed"),
                    response=str(publish_result),
                    posted_at=datetime.utcnow() if publish_result.get("status") == "success" else None,
                    error_message=publish_result.get("error", "")
                )
                db.add(publish_log)
            
            db.commit()
            
            # Check if at least one platform succeeded
            success_count = sum(1 for r in publish_results.values() if r.get("status") == "success")
            
            # Video generation succeeded, so pipeline is successful
            # Publishing failures are logged but don't fail the pipeline
            result["status"] = "success"
            result["post_id"] = post.id
            result["publish_results"] = publish_results
            
            if success_count > 0:
                logger.info(f"Pipeline completed successfully. Published to {success_count} platform(s)")
                send_notification(
                    f"Post published successfully to {success_count} platform(s). Post ID: {post.id}",
                    "success"
                )
            else:
                # All platforms failed, but video was generated successfully
                logger.warning("Pipeline completed: Video generated successfully, but all platforms failed to publish")
                logger.info("This is normal if API keys are not configured. Video is saved and can be published manually or retried later.")
                result["warnings"] = result.get("warnings", [])
                result["warnings"].append("All platforms failed to publish - check API keys/credentials")
                
                # Only send notification if configured
                if config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID:
                    send_notification(
                        f"Video generated successfully (Post ID: {post.id}), but publishing failed. Check API credentials.",
                        "warning"
                    )
            
            result["end_time"] = datetime.utcnow()
            result["duration_seconds"] = (result["end_time"] - start_time).total_seconds()
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            import traceback
            error_trace = traceback.format_exc()
            logger.error(error_trace)
            result["errors"].append(str(e))
            
            # Log to database
            try:
                system_log = SystemLog(
                    level="error",
                    message=str(e),
                    component="pipeline",
                    log_metadata=error_trace[:5000]  # Limit metadata size
                )
                db.add(system_log)
                db.commit()
            except:
                pass  # Don't fail if DB logging fails
            
            # Send notification
            send_notification(
                f"Pipeline error in slot {slot_name}: {str(e)[:200]}",
                "error"
            )
            
            return result
            
        finally:
            db.close()

