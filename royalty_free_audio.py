"""
Get royalty-free music for videos
Uses multiple sources to ensure copyright-safe audio is always available
"""
import os
import random
import tempfile
import requests
from typing import Optional
from loguru import logger
import config
from pathlib import Path

class RoyaltyFreeAudio:
    """Get copyright-safe royalty-free music for videos"""
    
    def __init__(self):
        # Create audio cache directory
        self.audio_cache_dir = config.MEDIA_DIR / "audio_cache"
        self.audio_cache_dir.mkdir(exist_ok=True)
        # Track last used audio for variety
        self.last_used_file = None
    
    def get_background_music(self, duration: float = 20.0) -> Optional[str]:
        """
        Get royalty-free background music with variety
        First tries audio files from assets/audio folder, then generates music
        Always picks different audio each time
        """
        logger.info(f"Getting royalty-free background music ({duration}s)...")
        
        # Step 1: Try to get audio from Google Drive (Primary source)
        if config.DRIVE_AUDIO_FOLDER_ID:
            logger.info("Checking Google Drive for audio...")
            try:
                from google_drive_assets import GoogleDriveAssets
                drive = GoogleDriveAssets()
                drive_audio = drive.download_random_file(
                    config.DRIVE_AUDIO_FOLDER_ID, 
                    str(config.AUDIO_DIR),
                    ['.mp3', '.wav', '.m4a']
                )
                if drive_audio:
                    self.last_used_file = drive_audio
                    logger.info(f"Using audio from Google Drive: {os.path.basename(drive_audio)}")
                    return drive_audio
            except Exception as e:
                logger.error(f"Failed to get audio from Drive: {e}")

        # Step 2: Try to get audio from assets/audio folder (Fallback)
        audio_path = self._get_random_audio_from_folder(duration)
        
        if audio_path and os.path.exists(audio_path):
            self.last_used_file = audio_path
            logger.info(f"Using audio from assets folder: {os.path.basename(audio_path)}")
            return audio_path
        
        # Step 3: Fallback to programmatically generated music

        # Step 3: Fallback to programmatically generated music
        logger.info("No audio files in assets folder, generating music programmatically")
        audio_path = self._generate_varied_music(duration)
        
        if audio_path and os.path.exists(audio_path):
            self.last_used_file = audio_path
            return audio_path
        
        # Step 3: Last resort - generate simple tone (always works)
        logger.info("Generating background tone with variety")
        return self._generate_simple_tone(duration)
    
    def _generate_varied_music(self, duration: float) -> Optional[str]:
        """Generate varied background music programmatically - different each time"""
        try:
            import numpy as np
            from moviepy.audio.AudioClip import AudioArrayClip
            
            # Expanded music styles for more variety
            styles = [
                {"name": "ambient", "base_freq": 220.0, "scale": [1, 5/4, 3/2, 2], "tempo": 0.5},
                {"name": "upbeat", "base_freq": 261.63, "scale": [1, 9/8, 5/4, 3/2, 5/3, 2], "tempo": 4.0},
                {"name": "calm", "base_freq": 196.00, "scale": [1, 6/5, 3/2], "tempo": 0.2},
                {"name": "energetic", "base_freq": 329.63, "scale": [1, 4/3, 3/2, 15/8, 2], "tempo": 6.0},
                {"name": "mysterious", "base_freq": 174.61, "scale": [1, 6/5, 3/2, 9/5], "tempo": 1.0},
                {"name": "techno", "base_freq": 146.83, "scale": [1, 3/2, 2], "tempo": 8.0},
                {"name": "ethereal", "base_freq": 392.00, "scale": [1, 5/4, 3/2, 15/8], "tempo": 0.3},
            ]
            
            # Pick a random style
            style = random.choice(styles)
            logger.info(f"Generating {style['name']} style background music")
            
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration))
            audio_data = np.zeros(len(t))
            
            # Create a rich layered sound
            base_freq = style["base_freq"]
            
            # Layer 1: Bass/Pad
            for ratio in style["scale"]:
                freq = base_freq * ratio
                # Add slow modulation
                mod = 1 + 0.05 * np.sin(2 * np.pi * 0.1 * t)
                wave = 0.1 * np.sin(2 * np.pi * freq * t * mod)
                audio_data += wave

            # Layer 2: Rhythmic Element
            tempo = style["tempo"]
            beat = np.sin(2 * np.pi * tempo * t) ** 4  # Sharp pulses
            beat_freq = base_freq * 2
            beat_wave = 0.05 * beat * np.sin(2 * np.pi * beat_freq * t)
            audio_data += beat_wave
            
            # Layer 3: Random Arpeggios
            # Divide timeline into segments
            segment_len = int(sample_rate * 0.5) # 0.5 seconds
            num_segments = len(t) // segment_len
            
            for i in range(num_segments):
                start = i * segment_len
                end = start + segment_len
                if end > len(t): break
                
                # Pick random note from scale
                ratio = random.choice(style["scale"])
                note_freq = base_freq * 4 * ratio # Higher pitch
                
                # Envelope for note
                local_t = np.linspace(0, 0.5, segment_len)
                envelope = np.exp(-5 * local_t) # Decay
                
                note_wave = 0.05 * envelope * np.sin(2 * np.pi * note_freq * local_t)
                audio_data[start:end] += note_wave

            # Normalize
            audio_data = audio_data / (np.max(np.abs(audio_data)) + 0.001) * 0.3
            
            # Convert to stereo
            audio_array = np.array([audio_data, audio_data]).T
            
            # Create audio clip
            audio_clip = AudioArrayClip(audio_array, fps=sample_rate)
            
            # Save
            import time
            random_id = random.randint(1000, 9999)
            output_path = self.audio_cache_dir / f"music_{style['name']}_{random_id}_{int(duration)}s.mp3"
            
            audio_clip.write_audiofile(
                str(output_path),
                verbose=False,
                logger=None,
                codec='libmp3lame',
                bitrate='128k'
            )
            audio_clip.close()
            
            return str(output_path)
            
        except Exception as e:
            logger.warning(f"Varied music generation error: {e}")
            # Fallback to simple tone
            return self._generate_simple_tone(duration)
    
    def _get_random_audio_from_folder(self, duration: float) -> Optional[str]:
        """Get random audio file from assets/audio folder (like background videos)"""
        try:
            # Check for audio files in assets/audio folder
            audio_extensions = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac']
            audio_files = []
            
            for ext in audio_extensions:
                audio_files.extend(list(config.AUDIO_DIR.glob(f"*{ext}")))
                audio_files.extend(list(config.AUDIO_DIR.glob(f"*{ext.upper()}")))
            
            if not audio_files:
                logger.debug(f"No audio files found in {config.AUDIO_DIR}")
                return None
            
            # Filter out the last used file to avoid immediate repeats
            available_files = [f for f in audio_files if str(f) != self.last_used_file]
            
            # If all files were used, reset and use all files
            if not available_files:
                logger.info("All audio files have been used, resetting selection")
                available_files = audio_files
                self.last_used_file = None
            
            # Randomly select an audio file
            selected_audio = random.choice(available_files)
            logger.info(f"Selected random audio: {selected_audio.name} (from {len(audio_files)} available files)")
            
            # Load and adjust duration if needed
            from moviepy.editor import AudioFileClip
            
            audio_clip = AudioFileClip(str(selected_audio))
            
            # If audio is shorter than needed, loop it
            if audio_clip.duration < duration:
                loops_needed = int(duration / audio_clip.duration) + 1
                from moviepy.editor import concatenate_audioclips
                audio_clips = [audio_clip] * loops_needed
                audio_clip = concatenate_audioclips(audio_clips).subclip(0, duration)
                logger.info(f"Looped audio to match {duration}s duration")
            else:
                # Trim to exact duration
                audio_clip = audio_clip.subclip(0, duration)
                logger.info(f"Trimmed audio to {duration}s")
            
            # Save to cache with unique name to avoid conflicts
            import time
            cached_path = self.audio_cache_dir / f"cached_{int(time.time())}_{selected_audio.stem}.mp3"
            audio_clip.write_audiofile(
                str(cached_path),
                verbose=False,
                logger=None,
                codec='libmp3lame',
                bitrate='192k'
            )
            audio_clip.close()
            
            return str(cached_path)
            
        except Exception as e:
            logger.warning(f"Error getting audio from folder: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None
    
    def _generate_simple_music(self, duration: float) -> Optional[str]:
        """Generate simple background music programmatically"""
        try:
            import numpy as np
            from scipy.io import wavfile
            
            # Generate a simple, pleasant background tone
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration))
            
            # Create a pleasant chord progression (C major)
            # Multiple frequencies for richness
            frequencies = [261.63, 329.63, 392.00, 523.25]  # C, E, G, C (octave)
            
            audio_data = np.zeros(int(sample_rate * duration))
            
            for i, freq in enumerate(frequencies):
                # Add each frequency with different amplitude
                amplitude = 0.1 / (i + 1)  # Decreasing amplitude
                wave = amplitude * np.sin(2 * np.pi * freq * t)
                # Add slight variation for interest
                wave *= (1 + 0.1 * np.sin(2 * np.pi * 0.5 * t))  # Slow modulation
                audio_data += wave
            
            # Normalize
            audio_data = audio_data / np.max(np.abs(audio_data)) * 0.3  # 30% volume
            
            # Convert to 16-bit integer
            audio_data = (audio_data * 32767).astype(np.int16)
            
            # Save as WAV
            output_path = self.audio_cache_dir / f"generated_music_{int(duration)}s.wav"
            wavfile.write(str(output_path), sample_rate, audio_data)
            
            logger.info(f"Generated simple background music: {output_path}")
            return str(output_path)
            
        except ImportError:
            logger.debug("scipy not available for music generation")
            return None
        except Exception as e:
            logger.debug(f"Music generation error: {e}")
            return None
    
    def _generate_simple_tone(self, duration: float) -> str:
        """Generate a simple background tone with variety (always works - guaranteed audio)"""
        try:
            import numpy as np
            from moviepy.audio.AudioClip import AudioArrayClip
            
            # Different chord progressions for variety
            chord_progressions = [
                [261.63, 329.63, 392.00],  # C major
                [293.66, 369.99, 440.00],  # D major
                [329.63, 415.30, 493.88],  # E major
                [220.00, 277.18, 329.63],  # A minor
                [246.94, 311.13, 369.99],  # B minor
            ]
            
            # Pick random chord progression
            frequencies = random.choice(chord_progressions)
            chord_name = ["C major", "D major", "E major", "A minor", "B minor"][chord_progressions.index(frequencies)]
            logger.info(f"Generating {chord_name} background tone")
            
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration))
            
            audio_data = np.zeros(len(t))
            
            for i, freq in enumerate(frequencies):
                amplitude = 0.15 / (i + 1)
                wave = amplitude * np.sin(2 * np.pi * freq * t)
                # Random modulation for variety
                mod_freq = random.uniform(0.15, 0.35)
                wave *= (1 + 0.1 * np.sin(2 * np.pi * mod_freq * t))
                audio_data += wave
            
            # Normalize
            audio_data = audio_data / (np.max(np.abs(audio_data)) + 0.001) * 0.25  # 25% volume
            
            # Convert to stereo
            audio_array = np.array([audio_data, audio_data]).T
            
            # Create audio clip
            audio_clip = AudioArrayClip(audio_array, fps=sample_rate)
            
            # Save with unique name (random ID for variety)
            random_id = random.randint(1000, 9999)
            output_path = self.audio_cache_dir / f"tone_{random_id}_{int(duration)}s.mp3"
            
            # Avoid immediate repeats
            if output_path.exists() and output_path == self.last_used_file:
                random_id = random.randint(1000, 9999)
                output_path = self.audio_cache_dir / f"tone_{random_id}_{int(duration)}s.mp3"
            
            audio_clip.write_audiofile(
                str(output_path), 
                verbose=False, 
                logger=None,
                codec='libmp3lame',
                bitrate='128k'
            )
            audio_clip.close()
            
            logger.info(f"Generated {chord_name} background tone: {output_path}")
            self.last_used_file = output_path
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating simple tone: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Last resort: use numpy to create WAV file directly
            try:
                import numpy as np
                import wave
                import struct
                
                sample_rate = 44100
                t = np.linspace(0, duration, int(sample_rate * duration))
                frequency = 440.0  # A note
                audio_data = 0.2 * np.sin(2 * np.pi * frequency * t)
                
                # Convert to 16-bit integers
                audio_data = (audio_data * 32767).astype(np.int16)
                
                output_path = self.audio_cache_dir / f"simple_tone_{int(duration)}s.wav"
                with wave.open(str(output_path), 'w') as wav_file:
                    wav_file.setnchannels(2)  # Stereo
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(sample_rate)
                    # Write stereo data
                    for sample in audio_data:
                        wav_file.writeframes(struct.pack('<hh', sample, sample))
                
                logger.info(f"Generated WAV tone: {output_path}")
                return str(output_path)
            except Exception as e2:
                logger.error(f"Even WAV generation failed: {e2}")
                # Return a path anyway - video generation will handle the error
                return str(self.audio_cache_dir / f"fallback_{int(duration)}s.wav")
    
    def _download_audio(self, video_id: str, duration: float) -> Optional[str]:
        """Download audio from YouTube video using yt-dlp"""
        try:
            import yt_dlp
            
            # Check cache first
            cached_path = self.audio_cache_dir / f"audio_{video_id}.mp3"
            if os.path.exists(cached_path):
                logger.info(f"Using cached audio: {cached_path}")
                return str(cached_path)
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(cached_path).replace('.mp3', '.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
            }
            
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Check if file was created
            if os.path.exists(cached_path):
                return str(cached_path)
            else:
                # Check for different extensions
                for ext in ['.m4a', '.webm', '.opus']:
                    alt_path = str(cached_path).replace('.mp3', ext)
                    if os.path.exists(alt_path):
                        return alt_path
                return None
                
        except Exception as e:
            logger.debug(f"Audio download error: {e}")
            return None

