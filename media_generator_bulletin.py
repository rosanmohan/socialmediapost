"""
Media generator for 20-second YouTube Shorts bulletin videos
Creates videos with top 5 news items displayed as a bulletin with trending audio
"""
import os
import random
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger
import config
from moviepy.editor import (
    VideoFileClip, ImageClip, CompositeVideoClip,
    AudioFileClip, concatenate_videoclips, ColorClip
)
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import tempfile
import requests
from io import BytesIO

class BulletinMediaGenerator:
    """Generate 20-second bulletin videos for YouTube Shorts"""
    
    def __init__(self):
        self.width = config.VIDEO_WIDTH
        self.height = config.VIDEO_HEIGHT
        self.fps = config.VIDEO_FPS
        self.target_duration = 20.0  # 20 seconds for Shorts
        
        # Ensure output directory exists
        config.MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    
    def generate_bulletin_video(self, news_items: List[Dict], audio_path: str) -> Optional[str]:
        """Generate 20-second bulletin video with top 5 news items and background music"""
        logger.info(f"Generating 20-second bulletin video with {len(news_items)} news items...")
        
        if not audio_path or not os.path.exists(audio_path):
            logger.error("Audio path is required and must exist - cannot create video without audio")
            return None
        
        try:
            # Step 1: Load audio (MUST have audio - no silent fallback)
            logger.info(f"Loading background music: {audio_path}")
            audio_clip = AudioFileClip(audio_path)
            
            # Trim or loop to exactly 20 seconds
            if audio_clip.duration < self.target_duration:
                # Loop audio if shorter
                loops_needed = int(self.target_duration / audio_clip.duration) + 1
                audio_clips = [audio_clip] * loops_needed
                audio_clip = concatenate_videoclips(audio_clips).subclip(0, self.target_duration)
                logger.info(f"Looped audio to match {self.target_duration}s duration")
            else:
                audio_clip = audio_clip.subclip(0, self.target_duration)
                logger.info(f"Trimmed audio to {self.target_duration}s")
            
            # Step 2: Create background (20 seconds)
            background = self._create_background(self.target_duration)
            
            # Step 3: Add news bulletin text overlays
            video_with_text = self._add_bulletin_text(background, news_items, self.target_duration)
            
            # Step 4: Add audio (MUST have audio)
            final_video = video_with_text.set_audio(audio_clip)
            
            # Step 5: Export video
            import time
            output_path = config.MEDIA_DIR / f"bulletin_video_{int(time.time())}.mp4"
            final_video.write_videofile(
                str(output_path),
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                preset='medium',
                bitrate='5000k'
            )
            
            # Cleanup
            audio_clip.close()
            final_video.close()
            background.close()
            
            logger.info(f"Bulletin video generated successfully: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating bulletin video: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _create_background(self, duration: float) -> VideoFileClip:
        """Create or get random background video"""
        bg_videos = list(config.BACKGROUNDS_DIR.glob("*.mp4"))
        
        if bg_videos:
            # Use random background video
            bg_path = random.choice(bg_videos)
            logger.info(f"Using random background video: {bg_path.name}")
            bg_clip = VideoFileClip(str(bg_path))
            
            # Resize to 9:16
            bg_clip = bg_clip.resize((self.width, self.height))
            
            # Adjust duration to exactly 20 seconds
            if bg_clip.duration < duration:
                # Slow down or loop
                speed_factor = bg_clip.duration / duration
                if speed_factor < 0.5:  # Very short video, use looping
                    loops_needed = int(duration / bg_clip.duration) + 1
                    try:
                        from moviepy.video.fx.all import speedx
                        slowed_clip = bg_clip.fx(speedx, 0.7)  # Slight slowdown
                        looped_clips = [slowed_clip] * loops_needed
                        bg_clip = concatenate_videoclips(looped_clips)
                    except:
                        looped_clips = [bg_clip] * loops_needed
                        bg_clip = concatenate_videoclips(looped_clips)
                else:
                    # Slow down smoothly
                    try:
                        from moviepy.video.fx.all import speedx
                        bg_clip = bg_clip.fx(speedx, speed_factor)
                    except:
                        # Fallback: loop
                        loops_needed = int(duration / bg_clip.duration) + 1
                        looped_clips = [bg_clip] * loops_needed
                        bg_clip = concatenate_videoclips(looped_clips)
            
            # Trim to exact duration
            bg_clip = bg_clip.subclip(0, duration)
            return bg_clip
        else:
            # Create gradient background
            logger.info("No background videos found, creating gradient background")
            return self._create_gradient_background(duration)
    
    def _create_gradient_background(self, duration: float) -> VideoFileClip:
        """Create animated gradient background with random colors"""
        try:
            # Generate random pleasant colors
            def random_color():
                return (random.randint(20, 100), random.randint(20, 100), random.randint(50, 150))
            
            c1 = random_color()
            c2 = random_color()
            c3 = random_color()

            # Create base image
            img = Image.new('RGB', (self.width, self.height), c1)
            draw = ImageDraw.Draw(img)
            
            logger.info(f"Creating gradient background with colors: {c1}, {c2}, {c3}")
            
            # Create complex gradient
            for y in range(self.height):
                p = y / self.height
                if p < 0.5:
                    # Blend c1 -> c2
                    ratio = p * 2
                    r = int(c1[0] * (1-ratio) + c2[0] * ratio)
                    g = int(c1[1] * (1-ratio) + c2[1] * ratio)
                    b = int(c1[2] * (1-ratio) + c2[2] * ratio)
                else:
                    # Blend c2 -> c3
                    ratio = (p - 0.5) * 2
                    r = int(c2[0] * (1-ratio) + c3[0] * ratio)
                    g = int(c2[1] * (1-ratio) + c3[1] * ratio)
                    b = int(c2[2] * (1-ratio) + c3[2] * ratio)
                
                draw.line([(0, y), (self.width, y)], fill=(r, g, b))
                
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            img.save(temp_file.name)
            temp_file.close()
            
            clip = ImageClip(temp_file.name, duration=duration)
            
            # Add slow movement/zoom
            # Randomly choose between zoom in, zoom out, or pan
            move_type = random.choice(['zoom_in', 'zoom_out', 'pan'])
            
            if move_type == 'zoom_in':
                clip = clip.resize(lambda t: 1 + 0.1 * t / duration)
            elif move_type == 'zoom_out':
                clip = clip.resize(lambda t: 1.1 - 0.1 * t / duration)
            else: # Pan (resize slightly larger then scroll)
                clip = clip.resize(1.1)
                clip = clip.set_position(lambda t: ('center', -10 * t))
            
            return clip
            
        except Exception as e:
            logger.warning(f"Error creating gradient: {e}, using simple background")
            # Fallback random dark color
            bg_color = (random.randint(10, 50), random.randint(10, 50), random.randint(30, 80))
            return ColorClip(size=(self.width, self.height), color=bg_color, duration=duration)
    
    def _add_bulletin_text(self, background: VideoFileClip, news_items: List[Dict], duration: float) -> CompositeVideoClip:
        """Add news bulletin text overlays - ALL items shown simultaneously for full duration"""
        clips = [background]
        
        # Limit to top 5 news items
        news_items = news_items[:5]
        
        # ALL items shown for the ENTIRE duration (20 seconds)
        # No sequential timing - all at once
        
        # Load font
        font_path = self._get_font_path()
        
        # Create a single image with all 5 news items
        all_items_clip = self._create_all_bulletin_items(
            news_items,
            duration,
            font_path
        )
        
        if all_items_clip:
            clips.append(all_items_clip)
        
        # Composite all clips
        final = CompositeVideoClip(clips, size=(self.width, self.height))
        return final
    
    def _create_all_bulletin_items(self, news_items: List[Dict], duration: float, font_path: Optional[str]) -> Optional[ImageClip]:
        """Create a single image with all 5 news items displayed simultaneously"""
        try:
            # Create image with all text
            img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Load fonts - smaller size to fit all 5 items
            try:
                if font_path and os.path.exists(font_path):
                    font_title = ImageFont.truetype(font_path, 50)  # Smaller for fitting
                    font_number = ImageFont.truetype(font_path, 40)
                else:
                    # Try system fonts
                    try:
                        font_title = ImageFont.truetype("arial.ttf", 50)
                        font_number = ImageFont.truetype("arial.ttf", 40)
                    except:
                        font_title = ImageFont.load_default()
                        font_number = ImageFont.load_default()
            except:
                font_title = ImageFont.load_default()
                font_number = ImageFont.load_default()
            
            # Calculate positions for all 5 items
            # Distribute evenly across the height (9:16 = 1080x1920)
            # Leave margins: top 100px, bottom 100px, so 1720px available
            # 5 items with spacing: each item gets ~344px height
            
            start_y = 150  # Top margin
            item_height = (self.height - 300) // 5  # Available height / 5 items
            spacing = 20  # Space between items
            
            for idx, news in enumerate(news_items):
                news_number = idx + 1
                title = news.get("title", "Breaking News")
                
                # NO TRUNCATION - show full meaningful headline
                # But wrap it to fit in the available space
                
                # Calculate position for this item
                y_start = start_y + idx * (item_height + spacing)
                y_center = y_start + item_height // 2
                
                # Draw news number badge (left side)
                number_text = f"{news_number}"
                bbox = draw.textbbox((0, 0), number_text, font=font_number)
                number_width = bbox[2] - bbox[0]
                number_height = bbox[3] - bbox[1]
                
                # Smaller circle for compact layout
                circle_size = 50
                circle_x = 60
                circle_y = y_center
                
                # Draw circle
                draw.ellipse(
                    [circle_x - circle_size // 2, circle_y - circle_size // 2,
                     circle_x + circle_size // 2, circle_y + circle_size // 2],
                    fill=(255, 0, 0, 240)  # Red circle
                )
                
                # Draw number
                number_x = circle_x - number_width // 2
                number_y = circle_y - number_height // 2
                draw.text((number_x, number_y), number_text, fill=(255, 255, 255, 255), font=font_number)
                
                # Draw news title (right side of number)
                text_x = 130  # Start after number circle
                text_y = y_start + 10  # Top of text area
                max_text_width = self.width - text_x - 40  # Leave right margin
                max_text_height = item_height - 20
                
                # Word wrap the FULL title to fit in available space
                words = title.split()
                lines = []
                current_line = []
                current_width = 0
                
                for word in words:
                    bbox = draw.textbbox((0, 0), word + " ", font=font_title)
                    word_width = bbox[2] - bbox[0]
                    
                    if current_width + word_width > max_text_width and current_line:
                        lines.append(" ".join(current_line))
                        current_line = [word]
                        current_width = word_width
                    else:
                        current_line.append(word)
                        current_width += word_width
                
                if current_line:
                    lines.append(" ".join(current_line))
                
                # Limit lines to fit in available height
                line_height = 55  # Adjusted for smaller font
                max_lines = min(len(lines), max_text_height // line_height)
                lines = lines[:max_lines]
                
                # Draw all lines
                for i, line in enumerate(lines):
                    if i * line_height < max_text_height:
                        draw.text(
                            (text_x, text_y + i * line_height),
                            line,
                            fill=(255, 255, 255, 255),
                            font=font_title,
                            stroke_width=2,
                            stroke_fill=(0, 0, 0, 220)
                        )
            
            # Convert to numpy array
            img_array = np.array(img)
            
            # Create clip for entire duration (all items shown for full 20 seconds)
            clip = ImageClip(img_array).set_duration(duration).set_position(('center', 'center'))
            
            # Add subtle fade in at start
            clip = clip.fadein(0.5)
            
            return clip
            
        except Exception as e:
            logger.error(f"Error creating all bulletin items: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _get_font_path(self) -> Optional[str]:
        """Get font path, prioritizing custom fonts"""
        # Check custom fonts first
        custom_fonts = list(config.FONTS_DIR.glob("*.ttf")) + list(config.FONTS_DIR.glob("*.otf"))
        if custom_fonts:
            return str(random.choice(custom_fonts))
        
        # Try system fonts
        system_fonts = [
            "arial.ttf",
            "calibri.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf"
        ]
        
        for font in system_fonts:
            if os.path.exists(font):
                return font
        
        return None

