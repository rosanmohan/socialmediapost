"""
Media generation service
Creates 9:16 vertical videos with text overlays, background, and TTS audio
"""
import os
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
from gtts import gTTS
import io
import tempfile

class MediaGenerator:
    """Generate 9:16 vertical videos for social media"""
    
    def __init__(self):
        self.width = config.VIDEO_WIDTH
        self.height = config.VIDEO_HEIGHT
        self.fps = config.VIDEO_FPS
        
        # Ensure output directory exists
        config.MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    
    def generate_video(self, content: Dict, news_title: str) -> Optional[str]:
        """Generate complete video from content"""
        logger.info("Starting video generation...")
        
        try:
            # Step 1: Generate TTS audio
            audio_path = self._generate_tts(content["script"], news_title)
            if not audio_path:
                logger.error("Failed to generate TTS audio")
                return None
            
            # Step 2: Get audio duration
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            
            # Step 3: Create background
            background = self._create_background(duration)
            
            # Step 4: Add text overlays
            video_with_text = self._add_text_overlays(background, content, duration)
            
            # Step 5: Add audio
            final_video = video_with_text.set_audio(audio_clip)
            
            # Step 6: Export video
            output_path = config.MEDIA_DIR / f"video_{int(os.path.getmtime(audio_path))}.mp4"
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
            
            logger.info(f"Video generated successfully: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _generate_tts(self, script: str, identifier: str) -> Optional[str]:
        """Generate text-to-speech audio"""
        logger.info("Generating TTS audio...")
        
        try:
            if config.TTS_PROVIDER == "gtts":
                tts = gTTS(text=script, lang='en', slow=False)
                audio_path = config.MEDIA_DIR / f"audio_{identifier.replace(' ', '_')[:50]}.mp3"
                tts.save(str(audio_path))
                logger.info(f"TTS audio saved: {audio_path}")
                return str(audio_path)
            else:
                # Fallback to pyttsx3
                import pyttsx3
                engine = pyttsx3.init()
                audio_path = config.MEDIA_DIR / f"audio_{identifier.replace(' ', '_')[:50]}.wav"
                engine.save_to_file(script, str(audio_path))
                engine.runAndWait()
                return str(audio_path)
                
        except Exception as e:
            logger.error(f"Error generating TTS: {e}")
            return None
    
    def _create_background(self, duration: float) -> VideoFileClip:
        """Create or get background video/image"""
        # Check for background videos
        bg_videos = list(config.BACKGROUNDS_DIR.glob("*.mp4"))
        bg_images = list(config.BACKGROUNDS_DIR.glob("*.jpg")) + list(config.BACKGROUNDS_DIR.glob("*.png"))
        
        if bg_videos:
            # Use random background video for variety
            import random
            bg_path = random.choice(bg_videos)
            logger.info(f"Using random background video: {bg_path.name} (selected from {len(bg_videos)} options)")
            bg_clip = VideoFileClip(str(bg_path))
            original_duration = bg_clip.duration
            logger.info(f"Background video duration: {original_duration:.2f}s, needed: {duration:.2f}s")
            
            # Resize first
            bg_clip = bg_clip.resize((self.width, self.height))
            
            if bg_clip.duration < duration:
                # Calculate how much we need to slow it down
                speed_factor = bg_clip.duration / duration
                logger.info(f"Background video is {bg_clip.duration:.2f}s, need {duration:.2f}s. Speed factor: {speed_factor:.3f}")
                
                # If video is very short (< 3s) and needs extreme slowdown (> 10x), use looping instead
                # Otherwise, slow it down smoothly
                if bg_clip.duration < 3.0 and speed_factor < 0.1:
                    # Video is very short, use looping with slight slowdown for better quality
                    logger.info("Video is very short, using looping with slight slowdown")
                    loops_needed = max(1, int(duration / bg_clip.duration) + 1)
                    # Slow down each loop slightly (2x slower) for smoother appearance
                    try:
                        from moviepy.video.fx.all import speedx
                        slowed_clip = bg_clip.fx(speedx, 0.5)  # 2x slower
                        looped_clips = [slowed_clip] * loops_needed
                        bg_clip = concatenate_videoclips(looped_clips)
                        logger.info(f"Created {loops_needed} loops with 2x slowdown")
                    except:
                        # Fallback: just loop normally
                        looped_clips = [bg_clip] * loops_needed
                        bg_clip = concatenate_videoclips(looped_clips)
                        logger.info(f"Created {loops_needed} loops")
                else:
                    # Normal slowdown - use speedx for smooth result
                    try:
                        from moviepy.video.fx.all import speedx
                        # speed_factor: 0.25 means 4x slower (if video is 10s, becomes 40s)
                        bg_clip = bg_clip.fx(speedx, speed_factor)
                        logger.info(f"Video slowed down using speedx: {speed_factor:.3f}x")
                    except (ImportError, AttributeError, TypeError) as e:
                        logger.warning(f"speedx import/usage failed: {e}, trying alternative method")
                        # Method 2: Use set_fps (works but less smooth)
                        try:
                            original_fps = bg_clip.fps or 30
                            new_fps = max(1, int(original_fps * speed_factor))  # Ensure fps >= 1
                            bg_clip = bg_clip.set_fps(new_fps)
                            logger.info(f"Using fps method: {original_fps} -> {new_fps} fps")
                        except Exception as e2:
                            # Method 3: Loop as last resort
                            logger.warning(f"Using loop fallback: {e2}")
                            loops_needed = max(1, int(duration / bg_clip.duration) + 1)
                            looped_clips = [bg_clip] * loops_needed
                            bg_clip = concatenate_videoclips(looped_clips)
            
            # Ensure exact duration match
            bg_clip = bg_clip.subclip(0, min(bg_clip.duration, duration))
            if bg_clip.duration < duration:
                # If still shorter, extend last frame
                bg_clip = bg_clip.fx(lambda clip: clip.set_duration(duration))
            
            logger.info(f"Final background duration: {bg_clip.duration:.2f}s")
            return bg_clip
        elif bg_images:
            # Use image background with zoom and pan effect
            bg_path = bg_images[0]
            img_clip = ImageClip(str(bg_path), duration=duration)
            img_clip = img_clip.resize((self.width, self.height))
            
            # Add dynamic zoom and pan effect
            def zoom_pan(t):
                zoom_factor = 1 + 0.2 * t / duration  # Zoom from 1.0 to 1.2
                return zoom_factor
            
            img_clip = img_clip.resize(zoom_pan)
            # Add slight opacity variation for depth
            img_clip = img_clip.fx(lambda clip: clip.set_opacity(0.9))
            return img_clip
        else:
            # Create gradient background
            logger.info("Creating gradient background")
            return self._create_gradient_background(duration)
    
    def _create_gradient_background(self, duration: float) -> VideoFileClip:
        """Create an animated gradient background"""
        try:
            # Create a more interesting gradient background
            # Use a modern color scheme
            colors = [
                (25, 25, 112),    # Midnight blue
                (72, 61, 139),    # Dark slate blue  
                (123, 104, 238),  # Medium slate blue
            ]
            
            # Create gradient image
            img = Image.new('RGB', (self.width, self.height), colors[0])
            draw = ImageDraw.Draw(img)
            
            # Create vertical gradient
            for y in range(self.height):
                progress = y / self.height
                color_idx = int(progress * (len(colors) - 1))
                next_idx = min(color_idx + 1, len(colors) - 1)
                blend = (progress * (len(colors) - 1)) - color_idx
                
                color1 = colors[color_idx]
                color2 = colors[next_idx]
                
                r = int(color1[0] * (1 - blend) + color2[0] * blend)
                g = int(color1[1] * (1 - blend) + color2[1] * blend)
                b = int(color1[2] * (1 - blend) + color2[2] * blend)
                
                draw.rectangle([(0, y), (self.width, y+1)], fill=(r, g, b))
            
            # Save and create clip
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            img.save(temp_file.name)
            temp_file.close()
            
            clip = ImageClip(temp_file.name, duration=duration)
            
            # Add subtle zoom effect for motion
            def zoom(t):
                return 1 + 0.15 * t / duration
            
            clip = clip.resize(zoom)
            
            return clip
            
        except Exception as e:
            logger.warning(f"Error creating gradient: {e}, using simple background")
            bg_color = (30, 30, 50)
            return ColorClip(size=(self.width, self.height), color=bg_color, duration=duration)
    
    def _add_text_overlays(self, background: VideoFileClip, content: Dict, duration: float) -> CompositeVideoClip:
        """Add text overlays with perfect audio sync and animations"""
        clips = [background]
        
        logger.info(f"Adding text overlays. Duration: {duration:.2f}s")
        
        # Load better fonts (try bold first, then custom fonts)
        font_hook = None
        font_main = None
        font_hook_size = 150  # Track font sizes explicitly
        font_main_size = 110
        
        try:
            # Try custom fonts from assets/fonts first
            custom_fonts = list(config.FONTS_DIR.glob("*.ttf"))
            if custom_fonts:
                try:
                    font_path = str(custom_fonts[0])
                    logger.info(f"Using custom font: {font_path}")
                    # Much larger fonts for better readability on mobile screens (9:16 vertical format)
                    font_hook = ImageFont.truetype(font_path, font_hook_size)  # 150px for hook
                    font_main = ImageFont.truetype(font_path, font_main_size)  # 110px for main text
                    logger.info(f"Font sizes: hook={font_hook_size}px, main={font_main_size}px")
                except Exception as e:
                    logger.warning(f"Failed to load custom font: {e}")
            
            # Fallback to system fonts
            if not font_hook:
                font_paths = [
                    "C:/Windows/Fonts/arialbd.ttf",  # Arial Bold
                    "C:/Windows/Fonts/calibrib.ttf",  # Calibri Bold
                    "C:/Windows/Fonts/arial.ttf",     # Arial Regular
                ]
                
                for path in font_paths:
                    if os.path.exists(path):
                        try:
                            # Much larger fonts for better readability on mobile screens
                            font_hook = ImageFont.truetype(path, font_hook_size)  # 150px for hook
                            font_main = ImageFont.truetype(path, font_main_size)   # 110px for main text
                            logger.info(f"Using system font: {path} (size: hook={font_hook_size}px, main={font_main_size}px)")
                            break
                        except Exception as e:
                            logger.warning(f"Failed to load {path}: {e}")
                            continue
            
            if not font_hook:
                # Default font is very small, try to scale it up
                try:
                    # Try to get a larger default font
                    default_font = ImageFont.load_default()
                    # For default font, we'll need to use a workaround since it doesn't support size
                    font_hook = default_font
                    font_main = default_font
                    font_hook_size = 20  # Default font is very small
                    font_main_size = 16
                    logger.warning("Using default font (very small - consider adding custom fonts)")
                except:
                    font_hook = ImageFont.load_default()
                    font_main = ImageFont.load_default()
                    font_hook_size = 20
                    font_main_size = 16
                    logger.warning("Using default font (very small - consider adding custom fonts)")
        except Exception as e:
            logger.error(f"Error loading fonts: {e}")
            font_hook = ImageFont.load_default()
            font_main = ImageFont.load_default()
            font_hook_size = 20
            font_main_size = 16
        
        # Add hook text with animation (first 3-4 seconds)
        hook = content.get("hook", "")
        if hook:
            logger.info(f"Creating hook text: {hook[:50]}...")
            hook_clip = self._create_animated_text_clip(
                hook, font_hook, min(3.5, duration), 
                self.width, self.height, 
                animation_type='fade_scale',
                is_hook=True,
# font_size removed - using is_hook flag instead
            )
            if hook_clip:
                clips.append(hook_clip.set_start(0))
                logger.info(f"Hook text clip created: duration={hook_clip.duration:.2f}s")
            else:
                logger.error("Failed to create hook text clip")
        
        # Get script for better synchronization
        script = content.get("script", "")
        words_per_second = 2.5  # Average speaking rate
        
        # Add on-screen text segments with perfect sync
        on_screen_texts = content.get("on_screen_text", [])
        if not on_screen_texts:
            logger.info("No on_screen_text provided, auto-generating from script")
            # Auto-generate with better timing
            on_screen_texts = self._auto_generate_text_segments(script, duration)
        
        logger.info(f"Processing {len(on_screen_texts)} text segments")
        
        # Improve timing based on actual script words
        script_words = script.split()
        current_word_index = 0
        text_clips_created = 0
        
        for idx, text_seg in enumerate(on_screen_texts):
            text = text_seg.get("text", "").strip()
            start_time = text_seg.get("start_time", 0)
            seg_duration = text_seg.get("duration", 3)
            
            if not text:
                logger.warning(f"Empty text in segment {idx}")
                continue
            
            # Recalculate timing based on actual word positions in script
            if script and text:
                # Find text in script
                text_words = text.split()
                if len(text_words) > 0:
                    # Try to find where this text appears in script
                    for i in range(current_word_index, len(script_words) - len(text_words) + 1):
                        if script_words[i:i+len(text_words)] == text_words:
                            # Found it! Calculate exact timing
                            start_time = i / words_per_second
                            seg_duration = len(text_words) / words_per_second
                            current_word_index = i + len(text_words)
                            break
            
            if text and start_time < duration:
                logger.info(f"Creating text clip {idx+1}: '{text[:30]}...' at {start_time:.2f}s for {seg_duration:.2f}s")
                text_clip = self._create_animated_text_clip(
                    text, font_main, 
                    min(seg_duration, duration - start_time), 
                    self.width, self.height,
                    animation_type='slide_fade',
                    is_hook=False  # is_hook=False will use 110px automatically
                )
                if text_clip:
                    clips.append(text_clip.set_start(start_time))
                    text_clips_created += 1
                    logger.info(f"Text clip {idx+1} created successfully")
                else:
                    logger.error(f"Failed to create text clip {idx+1} for: {text[:30]}")
        
        logger.info(f"Created {text_clips_created} text clips out of {len(on_screen_texts)} segments")
        logger.info(f"Total clips to composite: {len(clips)}")
        
        # Composite all clips
        try:
            final = CompositeVideoClip(clips, size=(self.width, self.height))
            logger.info("Text overlays composited successfully")
            return final
        except Exception as e:
            logger.error(f"Error compositing clips: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Return background only if composition fails
            return background
    
    def _create_animated_text_clip(self, text: str, font: ImageFont.FreeTypeFont, duration: float, 
                                   width: int, height: int, animation_type: str = 'fade',
                                   is_hook: bool = False) -> Optional[ImageClip]:
        """Create animated text clip with professional effects - COMPLETELY REWRITTEN TO AVOID ERRORS"""
        try:
            # STEP 1: Validate and convert duration to float - NO EXCEPTIONS
            duration_val = 3.0  # Default
            try:
                if isinstance(duration, (int, float)):
                    duration_val = float(duration)
                elif not callable(duration):
                    duration_val = float(str(duration))
            except:
                duration_val = 3.0
            duration_val = max(0.1, duration_val)
            
            logger.info(f"Creating text clip: is_hook={is_hook}, duration={duration_val:.2f}s")
            
            # STEP 2: Create image with text
            img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # STEP 3: Word wrap text
            words = text.split()
            lines = []
            current_line = []
            max_width = width - 200
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=font)
                text_width = bbox[2] - bbox[0]
                
                if text_width <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # STEP 4: Set colors
            if is_hook:
                text_color = (255, 255, 0, 255)
                outline_color = (0, 0, 0, 255)
                outline_width = 4
            else:
                text_color = (255, 255, 255, 255)
                outline_color = (0, 0, 0, 255)
                outline_width = 3
            
            # STEP 5: Calculate positions - ALL HARDCODED, NO MULTIPLICATION
            if is_hook:
                line_height_num = 225  # Hardcoded
            else:
                line_height_num = 165  # Hardcoded
            
            num_lines = len(lines)
            total_height_num = num_lines * line_height_num  # Both are integers
            start_y_num = (height - total_height_num) // 2 - 100
            
            # STEP 6: Draw text
            for line_idx in range(num_lines):
                line = lines[line_idx]
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                y = start_y_num + (line_idx * line_height_num)  # All integers
                
                # Draw outline
                for adj in range(-outline_width, outline_width + 1):
                    for adj2 in range(-outline_width, outline_width + 1):
                        if adj != 0 or adj2 != 0:
                            draw.text((x + adj, y + adj2), line, font=font, fill=outline_color)
                
                # Draw main text
                draw.text((x, y), line, font=font, fill=text_color)
            
            # STEP 7: Save image
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            img.save(temp_file.name, 'PNG')
            temp_file.close()
            
            # STEP 8: Create clip - NO FADE, SIMPLE APPROACH
            clip = ImageClip(temp_file.name, duration=duration_val)
            
            # STEP 9: Clean up
            import atexit
            atexit.register(lambda: os.unlink(temp_file.name) if os.path.exists(temp_file.name) else None)
            
            logger.info(f"Text clip created successfully: '{text[:30]}...'")
            return clip
            
        except Exception as e:
            logger.error(f"Error creating animated text clip: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _create_text_clip(self, text: str, font: ImageFont.FreeTypeFont, duration: float, width: int, height: int) -> Optional[ImageClip]:
        """Legacy method - redirects to animated version"""
        return self._create_animated_text_clip(text, font, duration, width, height, animation_type='fade', is_hook=False)
    
    def _auto_generate_text_segments(self, script: str, duration: float) -> List[Dict]:
        """Auto-generate text segments with perfect timing based on word positions"""
        import re
        
        # Split into sentences, but keep track of word positions
        sentences = re.split(r'([.!?]+)', script)
        # Reconstruct sentences with punctuation
        clean_sentences = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                clean_sentences.append((sentences[i] + sentences[i+1]).strip())
            else:
                clean_sentences.append(sentences[i].strip())
        
        clean_sentences = [s for s in clean_sentences if s]
        
        segments = []
        current_time = 3.5  # Start after hook (3.5 seconds)
        words_per_second = 2.5
        
        # Track word position in full script
        script_words = script.split()
        current_word_index = 0
        
        for sentence in clean_sentences:
            if current_time >= duration:
                break
            
            sentence_words = sentence.split()
            word_count = len(sentence_words)
            
            if word_count == 0:
                continue
            
            # Calculate exact duration based on word count
            seg_duration = word_count / words_per_second
            seg_duration = max(2.0, min(6.0, seg_duration))  # Min 2s, max 6s
            
            # Find sentence in script to get exact word position
            if current_word_index < len(script_words):
                # Calculate start time based on word position
                start_time = current_word_index / words_per_second
                # Ensure it's after hook
                if start_time < 3.5:
                    start_time = current_time
                else:
                    current_time = start_time
                
                segments.append({
                    "text": sentence[:100],  # Allow longer text
                    "duration": seg_duration,
                    "start_time": start_time
                })
                
                current_word_index += word_count
                current_time = start_time + seg_duration
            else:
                # Fallback if we can't find position
                segments.append({
                    "text": sentence[:100],
                    "duration": seg_duration,
                    "start_time": current_time
                })
                current_time += seg_duration
        
        return segments
    
    def generate_thumbnail(self, title: str, output_path: Optional[str] = None) -> str:
        """Generate thumbnail image"""
        if not output_path:
            output_path = config.MEDIA_DIR / f"thumbnail_{title[:30].replace(' ', '_')}.jpg"
        
        # Create thumbnail image
        img = Image.new('RGB', (self.width, self.height), color=(30, 30, 50))
        draw = ImageDraw.Draw(img)
        
        # Try to load font
        try:
            if config.FONT_PATH.exists():
                font_large = ImageFont.truetype(str(config.FONT_PATH), 100)  # Increased from 80 to 100
                font_small = ImageFont.truetype(str(config.FONT_PATH), 70)  # Increased from 50 to 70
            else:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Draw title (wrapped)
        words = title.split()
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font_large)
            if bbox[2] - bbox[0] < self.width - 100:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw lines
        y = (self.height - len(lines) * 100) // 2
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font_large)
            x = (self.width - (bbox[2] - bbox[0])) // 2
            draw.text((x, y), line, fill='white', font=font_large)
            y += 100
        
        img.save(str(output_path))
        logger.info(f"Thumbnail generated: {output_path}")
        return str(output_path)

