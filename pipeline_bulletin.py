"""
Pipeline for generating 20-second YouTube Shorts bulletin videos
Fetches top 5 news, creates bulletin video with trending audio, and uploads to YouTube
"""
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from loguru import logger
from database import SessionLocal, Post, PublishLog, NewsItem
from fuzzywuzzy import fuzz
from news_service import NewsService
from media_generator_bulletin import BulletinMediaGenerator
from royalty_free_audio import RoyaltyFreeAudio
from publishers import YouTubePublisher
from utils import send_notification
import config

class BulletinPipeline:
    """Pipeline for bulletin-style YouTube Shorts"""
    
    def __init__(self):
        self.news_service = NewsService()
        self.media_generator = BulletinMediaGenerator()
        self.royalty_free_audio = RoyaltyFreeAudio()
        self.youtube_publisher = YouTubePublisher()
    
    def run(self) -> Dict:
        """Run the bulletin pipeline"""
        start_time = datetime.utcnow()
        result = {
            "status": "pending",
            "start_time": start_time,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Step 1: Fetch exactly 5 UNUSED news items (no duplicates)
            logger.info("Step 1: Fetching exactly 5 unused news items...")
            top_5_news = self._get_exactly_5_unused_news()
            
            if len(top_5_news) < 5:
                result["status"] = "failed"
                result["errors"].append(f"Could not find 5 unused news items. Found only {len(top_5_news)}")
                logger.error(f"Could not find 5 unused news items. Found only {len(top_5_news)}")
                return result
            
            logger.info(f"Selected exactly {len(top_5_news)} unused news items for bulletin")

            # Step 1.5: Rewrite headlines for impact (Viral Hooks)
            logger.info("Step 1.5: Rewriting headlines for viral impact...")
            try:
                from llm_provider import get_llm
                llm = get_llm()
                
                # Create a prompt for all 5 items at once to save time/tokens
                headlines = [f"{idx+1}. {item.get('title')}" for idx, item in enumerate(top_5_news)]
                joined_headlines = "\n".join(headlines)
                
                prompt = (
                    f"Rewrite these 5 news headlines into catchy, viral video hooks (MAX 8 words each).\n"
                    f"Make them punchy, dramatic, and clear. No hashtags. No emojis.\n"
                    f"Current headlines:\n{joined_headlines}\n\n"
                    f"Output ONLY the 5 rewritten headlines, numbered 1-5."
                )
                
                response = llm.generate_text(prompt)
                
                # Parse response
                rewritten_lines = [line.strip() for line in response.strip().split('\n') if line.strip() and line[0].isdigit()]
                
                if len(rewritten_lines) == 5:
                    for i in range(5):
                        # Extract text after number (e.g. "1. Headline" -> "Headline")
                        clean_text = rewritten_lines[i].split('.', 1)[-1].strip()
                        # Update the news item dict (keep original title for description)
                        top_5_news[i]['original_title'] = top_5_news[i]['title']
                        top_5_news[i]['title'] = clean_text
                        logger.info(f"Rewrote: {top_5_news[i]['original_title'][:30]}... -> {clean_text}")
                else:
                    logger.warning(f"LLM return format issue. Got {len(rewritten_lines)} lines via LLM. Using originals.")
                    
            except Exception as e:
                logger.error(f"Failed to rewrite headlines: {e}. Using originals.")
            
            # Step 2: Get royalty-free background music (MUST have audio)
            logger.info("Step 2: Getting royalty-free background music...")
            audio_path = self.royalty_free_audio.get_background_music(duration=20.0)
            
            if not audio_path:
                result["status"] = "failed"
                result["errors"].append("Failed to get background music - audio is required")
                logger.error("Could not get background music - audio is required for attractive videos")
                return result
            
            logger.info(f"Got royalty-free background music: {audio_path}")
            
            # Step 3: Generate bulletin video
            logger.info("Step 3: Generating 20-second bulletin video...")
            video_path = self.media_generator.generate_bulletin_video(
                top_5_news,
                audio_path
            )
            
            if not video_path:
                result["status"] = "failed"
                result["errors"].append("Failed to generate video")
                logger.error("Video generation failed")
                return result
            
            # Step 4: Create title and description
            # Ensure we have exactly 5 items
            if len(top_5_news) != 5:
                result["status"] = "failed"
                result["errors"].append(f"Expected 5 news items but got {len(top_5_news)}")
                logger.error(f"Expected 5 news items but got {len(top_5_news)}")
                return result
            
            title = "📰 Top 5 Breaking News #Shorts"
            description = "Top 5 trending news stories you need to know!\n\n"
            for idx, news in enumerate(top_5_news, 1):
                # Use FULL title - no truncation
                full_title = news.get('title', 'News')
                description += f"{idx}. {full_title}\n"
            description += "\n#News #BreakingNews #Shorts #Trending"
            
            hashtags = ["news", "breakingnews", "shorts", "trending", "viral", "top5"]
            
            # Step 5: Upload to YouTube
            logger.info("Step 5: Uploading to YouTube...")
            publish_result = self.youtube_publisher.publish(
                video_path,
                title,
                description,
                hashtags
            )
            
            # Step 6: Save to database
            logger.info("Step 6: Saving to database...")
            db = SessionLocal()
            try:
                # Create post entry
                post = Post(
                    news_id=None,  # Multiple news items, no single news_id
                    script="",  # No script for bulletin
                    caption=description,
                    hashtags=",".join(hashtags),
                    video_path=video_path,
                    thumbnail_path=None
                )
                db.add(post)
                db.commit()
                db.refresh(post)
                
                # Mark news items as used (if they have IDs)
                for news in top_5_news:
                    news_id = news.get("id")
                    if news_id:
                        news_item = db.query(NewsItem).filter_by(id=news_id).first()
                        if news_item:
                            news_item.used_in_post = True
                            news_item.used_at = datetime.utcnow()
                
                # Log publish result
                publish_log = PublishLog(
                    post_id=post.id,
                    platform="youtube",
                    status=publish_result.get("status", "failed"),
                    response=str(publish_result),
                    posted_at=datetime.utcnow() if publish_result.get("status") == "success" else None,
                    error_message=publish_result.get("error", "")
                )
                db.add(publish_log)
                db.commit()
                
                result["post_id"] = post.id
                
            except Exception as e:
                db.rollback()
                logger.error(f"Error saving to database: {e}")
                result["warnings"].append(f"Database save error: {e}")
            finally:
                db.close()
            
            # Step 7: Finalize result
            if publish_result.get("status") == "success":
                result["status"] = "success"
                result["publish_results"] = {"youtube": publish_result}
                logger.info("Bulletin pipeline completed successfully")
                send_notification(
                    f"Bulletin video uploaded to YouTube! Post ID: {result.get('post_id')}",
                    "success"
                )
            else:
                result["status"] = "partial_failure"
                result["errors"].append("YouTube upload failed")
                result["publish_results"] = {"youtube": publish_result}
                logger.warning("Bulletin video generated but YouTube upload failed")
            
            result["end_time"] = datetime.utcnow()
            result["duration_seconds"] = (result["end_time"] - start_time).total_seconds()
            
            return result
            
        except Exception as e:
            result["status"] = "failed"
            result["errors"].append(str(e))
            logger.error(f"Bulletin pipeline error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return result
    
    def _get_exactly_5_unused_news(self) -> List[Dict]:
        """Get exactly 5 unused, unique news items - no duplicates"""
        db = SessionLocal()
        selected_news = []
        
        try:
            # Step 1: Fetch fresh news from APIs (get more than 5 to have options)
            logger.info("Fetching fresh news from all sources...")
            # Temporarily increase the limit for bulletin videos
            original_limit = config.TOP_N_NEWS_TO_CONSIDER
            config.TOP_N_NEWS_TO_CONSIDER = 20  # Get more items to choose from
            fresh_news = self.news_service.get_top_news()
            config.TOP_N_NEWS_TO_CONSIDER = original_limit  # Restore original
            
            # Save fresh news to database
            if fresh_news:
                saved_items_info = self.news_service.save_to_database(fresh_news)
                logger.info(f"Saved {len(saved_items_info)} fresh news items to database")
            
            # Step 2: Get unused news items from database
            # Priority: Newly fetched unused items > Old unused items > Updated versions of used items
            
            # First, try to get unused items from newly fetched news
            if fresh_news:
                for news in fresh_news[:20]:  # Check top 20 fresh items
                    if len(selected_news) >= 5:
                        break
                    
                    # Check if this news is already in database and unused
                    existing = db.query(NewsItem).filter_by(url=news.get("url", "")).first()
                    if existing and not existing.used_in_post:
                        # Convert to dict format
                        selected_news.append({
                            "id": existing.id,
                            "title": existing.title,
                            "description": existing.description or "",
                            "url": existing.url,
                            "source": existing.source or "Unknown"
                        })
                        logger.info(f"Selected unused fresh news: {existing.title[:60]}...")
            
            # Step 3: If we don't have 5 yet, get any unused items from database
            if len(selected_news) < 5:
                unused_items = db.query(NewsItem).filter_by(used_in_post=False).order_by(
                    NewsItem.score.desc(), NewsItem.fetched_at.desc()
                ).limit(10).all()
                
                for item in unused_items:
                    if len(selected_news) >= 5:
                        break
                    
                    # Check if we already have a similar item (avoid duplicates)
                    is_duplicate = False
                    for selected in selected_news:
                        # Check title similarity
                        title_similarity = fuzz.ratio(
                            item.title.lower(), 
                            selected.get("title", "").lower()
                        )
                        if title_similarity > 85:  # Very similar titles
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        selected_news.append({
                            "id": item.id,
                            "title": item.title,
                            "description": item.description or "",
                            "url": item.url,
                            "source": item.source or "Unknown"
                        })
                        logger.info(f"Selected unused news from database: {item.title[:60]}...")
            
            # Step 4: If still don't have 5, check for updated versions of used items
            # (Same story but different/newer article - this is allowed)
            if len(selected_news) < 5:
                # Get recently used items (within last 7 days) to check for updates
                cutoff_date = datetime.utcnow() - timedelta(days=7)
                recent_used = db.query(NewsItem).filter(
                    NewsItem.used_in_post == True,
                    NewsItem.used_at >= cutoff_date
                ).order_by(NewsItem.used_at.desc()).limit(20).all()
                
                # Check if any fresh news is an update to a used story
                for fresh in fresh_news[:20]:
                    if len(selected_news) >= 5:
                        break
                    
                    # Check if this fresh news is similar to a used item (update)
                    for used_item in recent_used:
                        title_similarity = fuzz.ratio(
                            fresh.get("title", "").lower(),
                            used_item.title.lower()
                        )
                        
                        # If similar (80-95% match), it might be an update
                        # But different URL means it's a new article about same story
                        if 80 <= title_similarity < 95 and fresh.get("url") != used_item.url:
                            # This is an update - allow it
                            existing = db.query(NewsItem).filter_by(url=fresh.get("url", "")).first()
                            if existing:
                                # Check if we already have this in selected
                                already_selected = any(s.get("url") == existing.url for s in selected_news)
                                if not already_selected:
                                    selected_news.append({
                                        "id": existing.id,
                                        "title": existing.title,
                                        "description": existing.description or "",
                                        "url": existing.url,
                                        "source": existing.source or "Unknown"
                                    })
                                    logger.info(f"Selected updated news (same story, new article): {existing.title[:60]}...")
                                    break
            
            # Step 5: Last resort - reuse old news (older than 7 days) if we still don't have 5
            if len(selected_news) < 5:
                cutoff_date = datetime.utcnow() - timedelta(days=7)
                old_news = db.query(NewsItem).filter(
                    NewsItem.used_at < cutoff_date
                ).order_by(NewsItem.score.desc()).limit(10).all()
                
                for item in old_news:
                    if len(selected_news) >= 5:
                        break
                    
                    # Check for duplicates
                    is_duplicate = False
                    for selected in selected_news:
                        title_similarity = fuzz.ratio(
                            item.title.lower(),
                            selected.get("title", "").lower()
                        )
                        if title_similarity > 85:
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        selected_news.append({
                            "id": item.id,
                            "title": item.title,
                            "description": item.description or "",
                            "url": item.url,
                            "source": item.source or "Unknown"
                        })
                        logger.info(f"Reusing old news (older than 7 days): {item.title[:60]}...")
            
            # Ensure we have exactly 5 items
            if len(selected_news) > 5:
                selected_news = selected_news[:5]
            
            return selected_news
            
        except Exception as e:
            logger.error(f"Error getting unused news: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return selected_news
        finally:
            db.close()

