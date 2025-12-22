"""
Media generator for Viral Single-Story videos.
Creates high-impact sequential videos with voiceover and progressive captions.
"""
import os
import random
import numpy as np
import tempfile
from typing import Dict, List, Optional
from loguru import logger
from moviepy import (
    VideoFileClip, ImageClip, CompositeVideoClip,
    AudioFileClip, concatenate_videoclips, ColorClip, concatenate_audioclips
)
from moviepy.video.fx import Resize, FadeIn
from PIL import Image, ImageDraw, ImageFont
import config

class ViralMediaGenerator:
    def __init__(self):
        self.width = config.VIDEO_WIDTH
        self.height = config.VIDEO_HEIGHT
        self.fps = config.VIDEO_FPS
        self.output_dir = os.path.join(config.DATA_DIR, "generated_media")
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_viral_video(self, 
                             story_parts: List[str], 
                             voiceover_paths: List[str], 
                             bg_music_path: Optional[str] = None,
                             accent_color: str = "#FFD700") -> Optional[str]:
        """
        Generates a viral video from story parts and their voiceovers.
        Syncs durations to audio and adds progressive captions.
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

            # Step 2: Get a long enough background
            # Get background and ensure it's longer than our total video
            bg_clip = self._get_random_background(duration=total_video_duration + 2.0)
            
            # Step 3: Create clips for each part
            part_clips = []
            current_time = 0
            
            for i, (text, audio, duration) in enumerate(zip(story_parts, voice_audios, part_durations)):
                # Get the segment of background for this part
                bg_segment = bg_clip.subclipped(current_time, current_time + duration)
                
                # Apply "Pattern Break" zoom to background
                if i % 2 == 0:
                    bg_segment = bg_segment.with_effects([Resize(1.1)])
                else:
                    bg_segment = bg_segment.with_effects([Resize(1.0)])

                # Create text overlay
                text_clip = self._create_text_clip(text, duration, accent_color)
                
                # Combine bg and text
                part_video = CompositeVideoClip([bg_segment, text_clip], size=(self.width, self.height))
                part_video = part_video.with_audio(audio)
                
                part_clips.append(part_video)
                current_time += duration

            # Step 4: Concatenate parts
            final_video = concatenate_videoclips(part_clips)
            
            # Step 3: Add background music (at low volume)
            if bg_music_path and os.path.exists(bg_music_path):
                bg_music = AudioFileClip(bg_music_path).with_volume_scaled(0.1)
                # Loop or trim music to match final_video duration
                if bg_music.duration < final_video.duration:
                    loops = int(final_video.duration / bg_music.duration) + 1
                    bg_music = concatenate_audioclips([bg_music] * loops).subclipped(0, final_video.duration)
                else:
                    bg_music = bg_music.subclipped(0, final_video.duration)
                
                # Overlay background music on top of voiceovers
                from moviepy import CompositeAudioClip
                new_audio = CompositeAudioClip([final_video.audio, bg_music])
                final_video = final_video.with_audio(new_audio)

            # Step 4: Export
            import time
            output_path = os.path.join(self.output_dir, f"viral_video_{int(time.time())}.mp4")
            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile="temp-audio.m4a",
                remove_temp=True
            )
            
            return output_path

        except Exception as e:
            logger.error(f"Error generating viral video: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def _get_random_background(self, duration: float) -> VideoFileClip:
        """Helper to get a random background video clip (Drive first, then local)"""
        bg_path = None
        
        # 1. Try Google Drive first
        if config.DRIVE_BACKGROUNDS_FOLDER_ID:
            try:
                from google_drive_assets import GoogleDriveAssets
                drive = GoogleDriveAssets()
                bg_path = drive.download_random_file(
                    config.DRIVE_BACKGROUNDS_FOLDER_ID,
                    str(config.BACKGROUNDS_DIR),
                    ['.mp4', '.mov']
                )
            except Exception as e:
                logger.warning(f"Failed to get background from Drive: {e}")

        # 2. Fallback to local files if Drive fails or is disabled
        if not bg_path:
            bg_videos = list(config.BACKGROUNDS_DIR.glob("*.mp4"))
            if bg_videos:
                bg_path = str(random.choice(bg_videos))
        
        if bg_path and os.path.exists(bg_path):
            bg_clip = VideoFileClip(bg_path)
        else:
            # Final fallback: dark color
            logger.warning("No background videos found, using color fallback")
            bg_clip = ColorClip(size=(self.width, self.height), color=(20, 20, 20), duration=duration)
            
        # Resize to fit portrait
        bg_clip = bg_clip.with_effects([Resize(new_size=(self.width, self.height))])
        
        if bg_clip.duration < duration:
            loops = int(duration / bg_clip.duration) + 1
            bg_clip = concatenate_videoclips([bg_clip] * loops)
            
        return bg_clip.subclipped(0, duration)

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
        return ImageClip(img_array).with_duration(duration).with_position(('center', 'center'))

    def _get_font_path(self) -> Optional[str]:
        """Get font path, prioritizing custom fonts"""
        custom_fonts = list(config.FONTS_DIR.glob("*.ttf")) + list(config.FONTS_DIR.glob("*.otf"))
        if custom_fonts:
            return str(random.choice(custom_fonts))
        return None
