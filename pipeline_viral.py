"""
Viral Single-Story Pipeline
Creates a single, high-impact reel for one story instead of a list.
"""
import os
import time
import random
from datetime import datetime
from typing import Dict, List
from pathlib import Path
from loguru import logger
from database import SessionLocal, NewsItem, Post
from news_service import NewsService
from viral_content_service import ViralContentService
from media_generator_viral import ViralMediaGenerator
from voice_service import VoiceService
from royalty_free_audio import RoyaltyFreeAudio
from publishers import PublisherManager
import config

class ViralPipeline:
    def __init__(self):
        self.news_service = NewsService()
        self.viral_service = ViralContentService()
        self.voice_service = VoiceService()
        self.publisher = PublisherManager()
        self.media_gen = ViralMediaGenerator() 
        self.audio_service = RoyaltyFreeAudio()

    def platform_caption_mapper(self, platform: str, hook: str, description: str, category: str) -> Dict:
        """Customizes caption and metadata for each platform"""
        category_tag = category.lower().replace(" ", "")
        
        if platform == "youtube":
            return {
                "title": f"{hook} ⚠️ #shorts #news", # YouTube uses titles
                "caption": f"{hook}\n\n{description[:100]}...\n\n#news #{category_tag} #shorts",
                "hashtags": ["news", category_tag, "shorts"]
            }
        elif platform == "instagram":
            return {
                "caption": f"{hook} ⚠️\n\n{description[:150]}...\n\n.\n.\n#news #{category_tag} #reels #trending",
                "hashtags": ["news", category_tag, "reels", "trending"]
            }
        else: # facebook
            return {
                "caption": f"BIG UPDATE: {hook}\n\n{description[:200]}...\n\nCheck back for more updates. #news #{category_tag}",
                "hashtags": ["news", category_tag]
            }

    def run(self):
        logger.info("🎬 Starting Viral Single-Story Pipeline...")
        
        db = SessionLocal()
        try:
            # Refresh news first
            self.news_service.fetch_all_news()
            # We also need to get the ranked items and save them to the DB so we have a score to sort by
            top_articles = self.news_service.get_top_news()
            self.news_service.save_to_database(top_articles)
            
            # --- NEW: VALIDATE CONNECTIONS FIRST ---
            # This prevents wasting 4 minutes generating a video if publishing will fail
            self.publisher.validate_all()
            
            # Get the #1 unused story (Using actual column names: used_in_post and score)
            story = db.query(NewsItem).filter(NewsItem.used_in_post == False).order_by(NewsItem.score.desc()).first()
            
            if not story:
                logger.error("No unused news stories found!")
                return
            
            logger.info(f"✨ Selected Viral Story: {story.title}")
            
            # 1. Generate Viral Hook & Progressive Story
            hook = self.viral_service.generate_viral_hook(story.title)
            story_parts = self.viral_service.summarize_to_story(story.title, story.description)
            
            # Combine all parts for video generation: Hook + 6 story parts
            all_parts = [hook] + story_parts
            
            # --- CLEAR SCRIPT LOGGING FOR USER ANALYSIS ---
            logger.info("="*50)
            logger.info("🎬 FULL VIDEO SCRIPT / CAPTION PREVIEW")
            logger.info(f"🪝 HOOK: {hook}")
            for i, part in enumerate(story_parts):
                logger.info(f"📝 Part {i+1}: {part}")
            logger.info("="*50)

            # 2. Generate Voiceovers for each part
            voiceover_paths = []
            for i, part in enumerate(all_parts):
                filename = f"part_{i}_{int(time.time())}.mp3"
                path = self.voice_service.generate_voiceover_sync(part, filename)
                if path:
                    voiceover_paths.append(path)
            
            if len(voiceover_paths) < len(all_parts):
                logger.error("Failed to generate all voiceovers!")
                return

            # 3. Get Color Code based on category (Fallback to Politics if not present)
            category = "News" # Default since NewsItem doesn't have category field
            accent_color = self.viral_service.get_color_code(category)

            # 4. Generate Video
            # Try to get background music (Drive first, then local)
            bg_music_path = self.audio_service.get_background_music(duration=20.0) # Will be trimmed/looped later anyway
            
            video_path = self.media_gen.generate_viral_video(
                all_parts, 
                voiceover_paths, 
                bg_music_path=bg_music_path,
                accent_color=accent_color
            )
            
            if not video_path:
                logger.error("Video generation failed!")
                return

            # 5. Publish with platform-specific captions
            success_any = False
            results = {}
            
            platforms = ["youtube", "instagram", "facebook"]
            for platform in platforms:
                platform_data = self.platform_caption_mapper(platform, hook, story.description, category)
                
                if platform == "youtube" and config.ENABLE_PUBLISH_YOUTUBE:
                    logger.info("Publishing to YouTube...")
                    res = self.publisher.youtube.publish(video_path, platform_data["title"], platform_data["caption"], platform_data["hashtags"])
                elif platform == "instagram" and config.ENABLE_PUBLISH_INSTAGRAM:
                    logger.info("Publishing to Instagram...")
                    res = self.publisher.instagram.publish(video_path, platform_data["caption"], platform_data["hashtags"])
                elif platform == "facebook" and config.ENABLE_PUBLISH_FACEBOOK:
                    logger.info("Publishing to Facebook...")
                    res = self.publisher.facebook.publish(video_path, platform_data["caption"], platform_data["hashtags"])
                else:
                    logger.info(f"Skipping {platform} publishing (disabled in config)")
                    res = {"status": "skipped", "error": "Disabled in config"}
                
                results[platform] = res
                if res.get("status") == "success":
                    success_any = True

            # 6. Save Post & Link to NewsItem
            try:
                # Refresh session if it stale after long video generation
                db.add(story)
                story.used_in_post = True
                story.used_at = datetime.utcnow()
                
                new_post = Post(
                    news_id=story.id,
                    script=" | ".join(all_parts),
                    video_path=video_path,
                    caption=f"{hook}\n\n{story.description[:200]}",
                    hashtags="", 
                    created_at=datetime.utcnow()
                )
                db.add(new_post)
                db.commit()
                logger.info("✅ Viral Pipeline results saved to database.")
            except Exception as dbe:
                logger.warning(f"⚠️ Initial commit failed, retrying with new session: {dbe}")
                db.rollback()
                # Final attempt with fresh session
                fresh_db = SessionLocal()
                try:
                    story_id = story.id
                    fresh_story = fresh_db.query(NewsItem).get(story_id)
                    fresh_story.used_in_post = True
                    fresh_story.used_at = datetime.utcnow()
                    
                    fresh_post = Post(
                        news_id=story_id,
                        script=" | ".join(all_parts),
                        video_path=video_path,
                        caption=f"{hook}\n\n{story.description[:200]}",
                        hashtags="", 
                        created_at=datetime.utcnow()
                    )
                    fresh_db.add(fresh_post)
                    fresh_db.commit()
                    logger.info("✅ Results saved on retry session.")
                finally:
                    fresh_db.close()
            
            logger.info("✅ Viral Pipeline completed!")
            return results

        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            db.rollback()
        finally:
            db.close()

if __name__ == "__main__":
    pipeline = ViralPipeline()
    pipeline.run()
