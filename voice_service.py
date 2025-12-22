"""
Voice Service
Handles AI voiceover generation using edge-tts.
"""
import asyncio
import edge_tts
import os
from loguru import logger
import config

class VoiceService:
    def __init__(self, voice="en-US-ChristopherNeural"):
        self.voice = voice
        self.output_dir = os.path.join(config.DATA_DIR, "generated_media", "audio_cache")
        os.makedirs(self.output_dir, exist_ok=True)

    async def generate_voiceover(self, text: str, filename: str) -> str:
        """Generates an mp3 file from text using edge-tts with gTTS fallback"""
        output_path = os.path.join(self.output_dir, filename)
        
        # Try Edge-TTS first (Premium quality)
        try:
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(output_path)
            logger.info(f"✅ Edge-TTS: Voiceover generated: {output_path}")
            return output_path
        except Exception as e:
            logger.warning(f"⚠️ Edge-TTS failed (403 or Service Error): {e}")
            logger.info("💡 Falling back to gTTS (Standard quality)...")
            
            # Fallback to gTTS (Highly reliable in cloud environments)
            try:
                from gtts import gTTS
                tts = gTTS(text=text, lang='en', tld='com')
                tts.save(output_path)
                logger.info(f"✅ gTTS: Voiceover generated as fallback: {output_path}")
                return output_path
            except Exception as ge:
                logger.error(f"❌ Both Edge-TTS and gTTS failed: {ge}")
                return None

    def generate_voiceover_sync(self, text: str, filename: str) -> str:
        """Synchronous wrapper for generate_voiceover"""
        return asyncio.run(self.generate_voiceover(text, filename))

if __name__ == "__main__":
    # Test
    service = VoiceService()
    path = service.generate_voiceover_sync("This is a test of the viral voiceover system.", "test_voice.mp3")
    print(f"Generated at: {path}")
