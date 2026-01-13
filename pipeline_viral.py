"""
Viral Single-Story Pipeline
Creates a single, high-impact reel for one story instead of a list.
"""
import os
import time
import random
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from loguru import logger
from database import SessionLocal, NewsItem, Post, init_db
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

    def run(self, category_filter: Optional[str] = None):
        print(f"🎬 Starting Viral Single-Story Pipeline {'for ' + category_filter if category_filter else ''}...")
        logger.info(f"🎬 Starting Viral Single-Story Pipeline {'for ' + category_filter if category_filter else ''}...")
        
        # Ensure database tables exist (Critical for fresh CI/CD runs)
        init_db()

        db = SessionLocal()
        try:
            # 1. Refresh news for the specific category we need (Efficiency fix)
            print(f"📡 Fetching news for {category_filter or 'any'}...")
            self.news_service.fetch_all_news(category_filter=category_filter)
            
            # 2. Rank and Save to DB (Ensure session is passed to keep objects 'attached')
            top_articles = self.news_service.get_top_news(category_filter=category_filter)
            if not top_articles:
                print("⚠️ No top articles found after filtering.")
            self.news_service.save_to_database(top_articles, db=db)
            
            # 3. Validate Connections
            self.publisher.validate_all()
            
            # 4. Get the #1 unused story (Filtered by category, using shared session)
            story_list = self.news_service.get_unused_news(limit=1, category=category_filter, db=db)
            
            # FALLBACK: If no news for specific category, try GENERAL category
            if not story_list and category_filter:
                print(f"⚠️ No unused news found for {category_filter}. Trying 'general' fallback...")
                logger.warning(f"No unused news stories found for {category_filter}! Trying fallback to 'general'...")
                story_list = self.news_service.get_unused_news(limit=1, category="general", db=db)
                if not story_list:
                     # Ultra fallback: fetch general news NOW
                     self.news_service.fetch_all_news(category_filter="general")
                     top_articles = self.news_service.get_top_news(category_filter="general")
                     self.news_service.save_to_database(top_articles, db=db)
                     story_list = self.news_service.get_unused_news(limit=1, category="general", db=db)

            if not story_list:
                msg = f"❌ FATAL: No unused news stories found even after fallback!"
                print(msg)
                logger.error(msg)
                # EXIT WITH ERROR CODE to fail the pipeline explicitly
                sys.exit(1)
            
            story = story_list[0] 
            print(f"✨ Selected Viral Story: {story.title} (Category: {story.category})")
            logger.info(f"✨ Selected Viral Story: {story.title} (Category: {story.category})")
            
            # Use story's actual category if no filter was provided
            active_category = category_filter if category_filter else story.category
            
            # 1. Generate Viral Hook & Progressive Story
            print("🧠 Generating viral script with LLM...")
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
            print("🎙️ Generating voiceovers...")
            voiceover_paths = []
            for i, part in enumerate(all_parts):
                filename = f"part_{i}_{int(time.time())}.mp3"
                path = self.voice_service.generate_voiceover_sync(part, filename)
                if path:
                    voiceover_paths.append(path)
            
            if len(voiceover_paths) < len(all_parts):
                logger.error("Failed to generate all voiceovers!")
                print("❌ Failed to generate all voiceovers!")
                sys.exit(1)

            # 3. Get Color Code based on active category
            accent_color = self.viral_service.get_color_code(active_category)

            # 4. Generate Video
            print("🎥 Rendering video (this takes time)...")
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
                print("❌ Video generation failed!")
                sys.exit(1)

            # 5. Publish with platform-specific captions
            success_any = False
            results = {}
            
            platforms = ["youtube", "instagram", "facebook"]
            for platform in platforms:
                platform_data = self.platform_caption_mapper(platform, hook, story.description, active_category)
                
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
            print("✅ Viral Pipeline results saved to database.")
            
            print("✅ Viral Pipeline completed successfully!")
            return results

        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            db.rollback()
        finally:
            db.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run the Viral Social Media Pipeline")
    parser.add_argument("--category", type=str, help="Filter by news category (e.g. india, cricket, movies)")
    args = parser.parse_args()
    
    pipeline = ViralPipeline()
    pipeline.run(category_filter=args.category)
