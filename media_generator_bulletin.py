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
        """Create or get random background video (Drive > Local > Gradient)"""
        
        # Step 1: Try Google Drive (Primary)
        if config.DRIVE_BACKGROUNDS_FOLDER_ID:
            try:
                # Check if we already have files downloaded recently to avoid spamming API? 
                # For now, let's try to get a new one to ensure variety
                logger.info("Checking Google Drive for background video...")
                from google_drive_assets import GoogleDriveAssets
                drive = GoogleDriveAssets()
                drive_bg = drive.download_random_file(
                    config.DRIVE_BACKGROUNDS_FOLDER_ID,
                    str(config.BACKGROUNDS_DIR),
                    ['.mp4', '.mov']
                )
                
                if drive_bg:
                    logger.info(f"Using background from Google Drive: {os.path.basename(drive_bg)}")
                    bg_clip = VideoFileClip(drive_bg)
                    return self._process_background_clip(bg_clip, duration)
            except Exception as e:
                logger.error(f"Failed to get background from Drive: {e}")

        # Step 2: Local Backgrounds
        bg_videos = list(config.BACKGROUNDS_DIR.glob("*.mp4"))
        
        if bg_videos:
            # Use random background video
            bg_path = random.choice(bg_videos)
            logger.info(f"Using random background video: {bg_path.name}")
            bg_clip = VideoFileClip(str(bg_path))
            return self._process_background_clip(bg_clip, duration)
            
        # Step 3: Gradient Fallback
        logger.info("No background videos found, creating gradient background")
        return self._create_gradient_background(duration)

    def _process_background_clip(self, bg_clip: VideoFileClip, duration: float) -> VideoFileClip:
        """Process a raw video clip to fit the target dimensions and duration"""
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
                    font_title = ImageFont.truetype(font_path, 60)  # Larger font (was 50)
                    font_number = ImageFont.truetype(font_path, 50)
                    font_header = ImageFont.truetype(font_path, 80)
                else:
                    # Try system fonts
                    try:
                        font_title = ImageFont.truetype("arial.ttf", 60)
                        font_number = ImageFont.truetype("arial.ttf", 50)
                        font_header = ImageFont.truetype("arial.ttf", 80)
                    except:
                        font_title = ImageFont.load_default()
                        font_number = ImageFont.load_default()
                        font_header = ImageFont.load_default()
            except:
                font_title = ImageFont.load_default()
                font_number = ImageFont.load_default()
                font_header = ImageFont.load_default()
            
            # --- Draw Header ---
            header_text = "TOP 5 BREAKING NEWS"
            bbox = draw.textbbox((0, 0), header_text, font=font_header)
            header_w = bbox[2] - bbox[0]
            
            # Draw header background
            draw.rectangle([0, 0, self.width, 140], fill=(200, 0, 0, 255)) # Red banner
            draw.text(((self.width - header_w)/2, 30), header_text, fill="white", font=font_header, stroke_width=3, stroke_fill="black")

            # --- Calculate Layout ---
            start_y = 180  # Top margin (below header)
            item_height = (self.height - 300) // 5  # Available height / 5 items
            
            # Distribute evenly across the height (9:16 = 1080x1920)
            # Leave margins: top 100px, bottom 100px, so 1720px available
            # 5 items with spacing: each item gets ~344px height
            
                # Draw glassmorphism card background for readability
                card_height = item_height - 25
                card_margin = 40
                card_y = y_center - card_height // 2
                
                # Semi-transparent dark background for text readability
                draw.rectangle(
                    [card_margin, card_y, self.width - card_margin, card_y + card_height],
                    fill=(0, 0, 0, 160),
                    outline=(255, 255, 255, 30),
                    width=2
                )
                
                # Draw Colorful Number Badge (Left)
                badge_size = 80
                badge_x = card_margin + 50
                badge_y = y_center
                
                # Vibrant colors for numbers for eye-catching look
                badge_colors = [(255, 59, 48), (255, 149, 0), (255, 204, 0), (52, 199, 89), (0, 122, 255)]
                badge_color = badge_colors[idx % len(badge_colors)]
                
                draw.ellipse(
                    [badge_x - badge_size//2, badge_y - badge_size//2, 
                     badge_x + badge_size//2, badge_y + badge_size//2],
                    fill=badge_color
                )
                
                # Draw number centered in badge
                # Use thicker stroke for bold look
                number_text = str(news_number)
                bbox = draw.textbbox((0, 0), number_text, font=font_number)
                num_w, num_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
                draw.text(
                    (badge_x - num_w/2, badge_y - num_h/2 - 5), 
                    number_text, 
                    fill="white", 
                    font=font_number,
                    stroke_width=2,
                    stroke_fill="black"
                )
                
                # Draw Title (Right)
                text_x = badge_x + 70
                max_text_width = self.width - text_x - card_margin - 30
                
                # Word wrap logic
                words = title.split()
                lines = []
                current_line = []
                current_w = 0
                
                for word in words:
                    bbox = draw.textbbox((0, 0), word + " ", font=font_title)
                    w = bbox[2] - bbox[0]
                    if current_w + w > max_text_width:
                        lines.append(" ".join(current_line))
                        current_line = [word]
                        current_w = w
                    else:
                        current_line.append(word)
                        current_w += w
                if current_line: lines.append(" ".join(current_line))
                
                # Center vertically based on number of lines
                total_text_height = len(lines) * 60
                text_start_y = y_center - total_text_height // 2
                
                for i, line in enumerate(lines):
                    draw.text(
                        (text_x, text_start_y + i * 60),
                        line,
                        fill="white",
                        font=font_title,
                        stroke_width=2,
                        stroke_fill="black"
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

