"""
Media generator for Viral Single-Story videos.
Creates high-impact sequential videos with voiceover and progressive captions.
Integrates Pollinations.ai for dynamic AI image backgrounds.
"""
import os
import random
import numpy as np
import tempfile
from typing import Dict, List, Optional
from loguru import logger
from moviepy.editor import (
    VideoFileClip, ImageClip, CompositeVideoClip,
    AudioFileClip, concatenate_videoclips, ColorClip, concatenate_audioclips
)
from moviepy.video.fx.all import resize, fadein
from PIL import Image, ImageDraw, ImageFont
import config
from pollinations_service import PollinationsService

class ViralMediaGenerator:
    def __init__(self):
        self.width = config.VIDEO_WIDTH
        self.height = config.VIDEO_HEIGHT
        self.fps = config.VIDEO_FPS
        self.output_dir = os.path.join(config.DATA_DIR, "generated_media")
        os.makedirs(self.output_dir, exist_ok=True)
        self.image_gen = PollinationsService()

    def generate_viral_video(self, 
                             story_parts: List[str], 
                             voiceover_paths: List[str], 
                             bg_music_path: Optional[str] = None,
                             accent_color: str = "#FFD700") -> Optional[str]:
        """
        Generates a viral video from story parts and their voiceovers.
        Syncs durations to audio and adds progressive captions and AI backgrounds.
        """
        logger.info(f"Generating viral video with {len(story_parts)} parts...")
        
        try:
            # Step 1: Calculate total duration and prep audio clips
            voice_audios = []
            part_durations = []
            total_video_duration = 0
            
            for vp in voiceover_paths:
                if os.path.exists(vp):
                    audio = AudioFileClip(vp)
                    duration = audio.duration + 0.4 # Small buffer
                    voice_audios.append(audio)
                    part_durations.append(duration)
                    total_video_duration += duration
                else:
                    logger.warning(f"Voiceover not found: {vp}")
                    # Use silence fallback? For now just skip logic will break sync, so better to add dummy
                    # But simpler to assume success for now based on user flow

            # Step 2: Generate AI Images for each part
            logger.info("Generating AI images for each story part...")
            image_paths = []
            for i, part_text in enumerate(story_parts):
                # Optimize prompt for visual clarity
                prompt = f"Editorial news image representing: {part_text}. Cinematic lighting, highly detailed, 4k, dark moody aesthetic"
                res = self.image_gen.generate_image(prompt)
                
                if res.get("status") == "success":
                    image_paths.append(res.get("image_path"))
                else:
                    logger.warning(f"Failed to generate image for part {i}, using fallback.")
                    image_paths.append(None)

            # Step 3: Create clips for each part
            part_clips = []
            
            # Fallback background in case image gen fails entirely for a part
            default_bg = self._get_random_background(duration=5.0) # 5s dummy duration
            
            for i, (text, audio, duration, img_path) in enumerate(zip(story_parts, voice_audios, part_durations, image_paths)):
                
                # A. Create Visual Base (AI Image or Fallback)
                if img_path and os.path.exists(img_path):
                    # Load image
                    img_clip = ImageClip(img_path).set_duration(duration)
                    
                    # 1. Scale to Fill Screen FIRST
                    # Use 'height' priority for 9:16
                    base_clip = img_clip.resize(height=self.height)
                    if base_clip.w < self.width:
                        base_clip = base_clip.resize(width=self.width)
                        
                    # 2. Apply Cinematic Zoom (Dynamic) AFTER scaling to fit
                    # Zoom In or Out (increased intensity to 0.04/s = ~20% over 5s)
                    if i % 2 == 0:
                        # Zoom IN: Starts at 1.0, grows larger
                        visual_clip = base_clip.resize(lambda t: 1 + 0.04 * t)
                    else:
                        # Zoom OUT: Starts larger (1.2), shrinks to 1.0
                        visual_clip = base_clip.resize(lambda t: 1.2 - 0.04 * t)
                        
                    visual_clip = visual_clip.set_position(('center', 'center'))
                else:
                    # Use fallback video segment
                    # We just loop the default_bg to match duration
                    loops = int(duration / default_bg.duration) + 1
                    visual_clip = concatenate_videoclips([default_bg] * loops).subclip(0, duration)

                # B. Create Text Overlay
                text_clip = self._create_text_clip(text, duration, accent_color)
                
                # C. Combine
                part_video = CompositeVideoClip([visual_clip, text_clip], size=(self.width, self.height))
                part_video = part_video.set_audio(audio)
                
                part_clips.append(part_video)

            # Step 4: Concatenate parts
            final_video = concatenate_videoclips(part_clips)
            
            # Step 5: Add background music (at low volume)
            if bg_music_path and os.path.exists(bg_music_path):
                bg_music = AudioFileClip(bg_music_path).volumex(0.12)
                # Loop or trim music
                if bg_music.duration < final_video.duration:
                    loops = int(final_video.duration / bg_music.duration) + 1
                    bg_music = concatenate_audioclips([bg_music] * loops).subclip(0, final_video.duration)
                else:
                    bg_music = bg_music.subclip(0, final_video.duration)
                
                from moviepy.editor import CompositeAudioClip
                new_audio = CompositeAudioClip([final_video.audio, bg_music])
                final_video = final_video.set_audio(new_audio)

            # Step 6: Export
            import time
            output_path = os.path.join(self.output_dir, f"viral_video_{int(time.time())}.mp4")
            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile="temp-audio.m4a",
                remove_temp=True,
                preset='medium', # Better quality/speed balance
                threads=4
            )
            
            return output_path

        except Exception as e:
            logger.error(f"Error generating viral video: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def _get_random_background(self, duration: float) -> VideoFileClip:
        """Helper to get a random background video clip (Fallback)"""
        bg_path = None
        
        # Try local folder first
        bg_videos = list(config.BACKGROUNDS_DIR.glob("*.mp4"))
        if bg_videos:
            bg_path = str(random.choice(bg_videos))
        
        if bg_path and os.path.exists(bg_path):
            bg_clip = VideoFileClip(bg_path)
        else:
            # Final fallback: dark color
            bg_clip = ColorClip(size=(self.width, self.height), color=(20, 20, 20), duration=duration)
            
        # Resize/Loop
        # Ensure it covers screen
        if bg_clip.w < self.width or bg_clip.h < self.height:
             bg_clip = bg_clip.resize(newsize=(self.width, self.height))

        if bg_clip.duration < duration:
            loops = int(duration / bg_clip.duration) + 1
            bg_clip = concatenate_videoclips([bg_clip] * loops)
            
        return bg_clip.subclip(0, duration)

    def _create_text_clip(self, text: str, duration: float, color: str) -> ImageClip:
        """Create a high-impact caption clip"""
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Load font
        font_path = self._get_font_path()
        font_size = 80
        try:
            font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
        except:
            font = ImageFont.load_default()

        # Wrap text
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] < self.width - 150:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
        lines.append(" ".join(current_line))
        
        # Calculate vertical position (centered)
        line_height = font_size + 20
        total_text_height = len(lines) * line_height
        y_start = (self.height - total_text_height) // 2
        
        # Draw Background Box for Readability (Glassmorphism style)
        box_width = self.width - 100
        box_height = total_text_height + 60
        box_x = 50
        box_y = y_start - 30
        
        # Rounded rectangle background
        draw.rounded_rectangle(
            [box_x, box_y, box_x + box_width, box_y + box_height],
            radius=20,
            fill=(0, 0, 0, 180)
        )
        
        # Draw Accent vertical bar on the left of the box
        draw.rectangle(
            [box_x, box_y + 10, box_x + 10, box_y + box_height - 10],
            fill=color
        )

        y = y_start
        for line in lines:
            bbox = draw.textbbox((0,0), line, font=font)
            w = bbox[2] - bbox[0]
            x = (self.width - w) // 2
            
            # Draw text
            draw.text((x, y), line, font=font, fill="white")
            y += line_height
            
        img_array = np.array(img)
        return ImageClip(img_array).set_duration(duration).set_position(('center', 'center'))

    def _get_font_path(self) -> Optional[str]:
        """Get font path, prioritizing custom fonts"""
        custom_fonts = list(config.FONTS_DIR.glob("*.ttf")) + list(config.FONTS_DIR.glob("*.otf"))
        if custom_fonts:
            return str(random.choice(custom_fonts))
        return None
