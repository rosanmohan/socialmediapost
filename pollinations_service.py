"""
Service for generating images using Pollinations.ai (Free, No API Key).
"""
import requests
import urllib.parse
import time
from typing import Dict, Optional
from loguru import logger
from pathlib import Path
import config

class PollinationsService:
    """
    Generates images using the free Pollinations.ai API.
    """
    
    def __init__(self):
        self.base_url = "https://image.pollinations.ai/prompt"
        # Standard vertical video aspect ratio 9:16 (1080x1920) or square (1024x1024)
        self.width = 1080
        self.height = 1920 
        self.model = "flux" # Options: flux, flux-realism, any-dark, turbo

    def generate_image(self, prompt: str, filename: Optional[str] = None) -> Dict:
        """
        Generate an image from a text prompt.
        
        Args:
            prompt (str): Description of the image
            filename (str, optional): Filename to save as. If None, auto-generated.
            
        Returns:
            Dict: status and image_path
        """
        try:
            # 1. Prepare URL
            # Encode prompt to be URL-safe
            encoded_prompt = urllib.parse.quote(prompt)
            
            # Construct URL with parameters
            # Adding seed for randomness if needed, or rely on their backend
            timestamp_seed = int(time.time())
            
            url = f"{self.base_url}/{encoded_prompt}?width={self.width}&height={self.height}&model={self.model}&seed={timestamp_seed}&nologo=true"
            
            logger.info(f"Generating image with Pollinations... Prompt: {prompt[:50]}...")
            
            # Add delay to avoid Rate Limit (Anonymous tier)
            delay = 5 + (timestamp_seed % 5) # Random delay between 5-10s
            logger.info(f"Waiting {delay}s to respect rate limits...")
            time.sleep(delay)

            # 2. Request Image (GET request returns binary)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=120)
            
            if response.status_code == 200:
                # 3. Save Image
                if not filename:
                    clean_prompt = "".join(x for x in prompt[:20] if x.isalnum() or x in " _-")
                    filename = f"pollinations_{clean_prompt}_{timestamp_seed}.jpg"
                
                save_path = config.MEDIA_DIR / filename
                
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                    
                logger.info(f"Image saved successfully: {save_path}")
                return {
                    "status": "success", 
                    "image_path": str(save_path),
                    "url": url # The URL itself is the source
                }
            else:
                logger.error(f"Pollinations Error: {response.status_code} - {response.text[:100]}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return {"status": "failed", "error": str(e)}

if __name__ == "__main__":
    # Test stub
    service = PollinationsService()
    print("Testing Pollinations Generator...")
    
    prompt = "A futuristic city with flying cars and neon lights, cyberpunk style, high quality, 8k"
    result = service.generate_image(prompt)
    
    print(result)
    
    if result.get("status") == "success":
        import os
        path = result.get("image_path")
        print(f"Opening {path}...")
        os.system(f'explorer /select,"{path}"')
