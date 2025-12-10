"""
Content generation service using LLM
Generates scripts, captions, and hashtags for social media posts
"""
from typing import Dict, Optional
from loguru import logger
import config
import json
import re

class ContentGenerator:
    """Generate content using LLM APIs"""
    
    def __init__(self):
        self.provider = config.LLM_PROVIDER
        self.model = config.LLM_MODEL
        self.api_key = getattr(config, f"{self.provider.upper()}_API_KEY", "")
        
        if self.provider == "openai":
            try:
                import openai
                self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
            except ImportError:
                logger.error("OpenAI library not installed")
                self.client = None
        elif self.provider == "anthropic":
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
            except ImportError:
                logger.error("Anthropic library not installed")
                self.client = None
        elif self.provider == "groq":
            # Groq - Free tier, very fast
            self.client = "groq"
        elif self.provider == "huggingface":
            # Hugging Face Inference API - Free tier
            self.client = "huggingface"
        elif self.provider == "together":
            # Together AI - Free tier available
            self.client = "together"
        elif self.provider == "openrouter":
            # OpenRouter - Free models available
            self.client = "openrouter"
        else:
            self.client = None
            logger.warning(f"Unknown LLM provider: {self.provider}")
    
    def generate_content(self, news_title: str, news_description: str, news_url: str) -> Dict:
        """Generate complete content package for a news article"""
        logger.info(f"Generating content for: {news_title[:50]}...")
        
        prompt = self._create_prompt(news_title, news_description, news_url)
        
        try:
            if self.provider == "openai":
                response = self._call_openai(prompt)
            elif self.provider == "anthropic":
                response = self._call_anthropic(prompt)
            elif self.provider == "groq":
                response = self._call_groq(prompt)
            elif self.provider == "huggingface":
                response = self._call_huggingface(prompt)
            elif self.provider == "together":
                response = self._call_together(prompt)
            elif self.provider == "openrouter":
                response = self._call_openrouter(prompt)
            else:
                logger.error("No valid LLM provider configured")
                return self._fallback_content(news_title, news_description)
            
            # Parse response
            content = self._parse_response(response)
            logger.info("Content generated successfully")
            return content
            
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return self._fallback_content(news_title, news_description)
    
    def _create_prompt(self, title: str, description: str, url: str) -> str:
        """Create prompt for LLM"""
        return f"""You are a social media content creator specializing in viral news content for short-form video platforms (Instagram Reels, YouTube Shorts, TikTok).

Given this news article, create engaging content:

Title: {title}
Description: {description}
Source URL: {url}

Please provide a JSON response with the following structure:
{{
    "hook": "A compelling 1-2 line hook that grabs attention immediately (max 100 characters)",
    "script": "A complete 40-45 second script for a vertical video. Break it into natural pauses. Make it engaging, informative, and suitable for text-to-speech. (300-400 words)",
    "on_screen_text": [
        {{"text": "First text overlay", "duration": 2.5, "start_time": 0.0}},
        {{"text": "Second text overlay", "duration": 3.0, "start_time": 2.5}},
        ...
    ],
    "caption": "A platform-agnostic caption (100-150 characters) that summarizes the story",
    "hashtags": ["hashtag1", "hashtag2", "hashtag3", ...],
    "title": "A catchy title for YouTube (max 100 characters, include #Shorts)"
}}

Requirements:
- Hook must be attention-grabbing and make people want to watch (3-4 seconds)
- Script should be conversational, clear, and work well with TTS. Include natural pauses.
- On-screen text should be short (1-2 lines max, max 8-10 words per segment), readable, and PERFECTLY timed to match the spoken words.
- Each text segment should appear exactly when those words are spoken in the script.
- Calculate timing precisely: average speaking rate is 2.5 words per second.
- Example: If script is "Breaking news today. Scientists discovered something amazing."
  - First segment: text="Breaking news today", start_time=0.0, duration=1.2 (3 words / 2.5 = 1.2s)
  - Second segment: text="Scientists discovered", start_time=1.2, duration=0.8 (2 words / 2.5 = 0.8s)
  - Third segment: text="something amazing", start_time=2.0, duration=0.8 (2 words / 2.5 = 0.8s)
- Start times must be sequential and cumulative based on word positions in script.
- Duration = number of words in segment / 2.5
- Caption should be concise and engaging
- Include 10-15 relevant hashtags (mix of trending and niche)
- Make content suitable for a 9:16 vertical video format
- Keep tone professional but engaging
- Avoid controversial or sensitive content that might violate platform policies

CRITICAL: For on_screen_text, calculate start_time and duration based on word position in script:
- If script starts with "Breaking news today", and "Breaking news" appears at word 0-2, start_time should be 0
- If "today" appears at word 2-3, start_time should be 0.8 (2 words / 2.5 words per second)
- Duration should match the number of words: word_count / 2.5

Return ONLY valid JSON, no additional text."""

    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        if not self.client:
            raise Exception("OpenAI client not initialized")
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert social media content creator. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API"""
        if not self.client:
            raise Exception("Anthropic client not initialized")
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=0.7,
            system="You are an expert social media content creator. Always respond with valid JSON only.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text
    
    def _call_groq(self, prompt: str) -> str:
        """Call Groq API (Free tier, very fast)"""
        try:
            import requests
            
            api_key = config.GROQ_API_KEY
            if not api_key:
                raise Exception("GROQ_API_KEY not configured")
            
            # Try different model names (Groq model names may vary)
            # Updated Nov 2025: Best models for content generation
            models_to_try = [
                self.model or "llama-3.1-8b-instant",  # Fast, good quality (default)
                "llama-3.3-70b-versatile",  # Latest 70B model (best quality if available)
                "llama-3.1-70b-versatile",  # Previous 70B model (fallback)
                "llama-3-70b-8192",  # Stable 70B model
                "mixtral-8x7b-32768",  # Mixtral model (alternative)
                "gemma2-9b-it"  # Google Gemma 2 (if available)
            ]
            
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            last_error = None
            for model in models_to_try:
                try:
                    data = {
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "You are an expert social media content creator. Always respond with valid JSON only."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 2000
                    }
                    
                    response = requests.post(url, json=data, headers=headers, timeout=60)
                    
                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"Groq API success with model: {model}")
                        return result["choices"][0]["message"]["content"]
                    else:
                        error_text = response.text[:200]
                        logger.warning(f"Groq API error with model {model}: {response.status_code} - {error_text}")
                        last_error = f"{response.status_code}: {error_text}"
                        # Try next model
                        continue
                        
                except requests.exceptions.RequestException as e:
                    last_error = str(e)
                    logger.warning(f"Groq API request error with model {model}: {e}")
                    continue
            
            # If all models failed, raise the last error
            raise Exception(f"Groq API failed with all models. Last error: {last_error}")
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            # Log more details for debugging
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response text: {e.response.text[:500]}")
            raise
    
    def _call_huggingface(self, prompt: str) -> str:
        """Call Hugging Face Inference API (Free tier)"""
        try:
            import requests
            
            api_key = getattr(config, "HUGGINGFACE_API_KEY", "")
            model = self.model or "mistralai/Mistral-7B-Instruct-v0.2"
            
            url = f"https://api-inference.huggingface.co/models/{model}"
            headers = {
                "Authorization": f"Bearer {api_key}" if api_key else None
            }
            
            # Format prompt for Hugging Face
            formatted_prompt = f"You are an expert social media content creator. Always respond with valid JSON only.\n\n{prompt}"
            
            data = {
                "inputs": formatted_prompt,
                "parameters": {
                    "max_new_tokens": 2000,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=120)
            response.raise_for_status()
            result = response.json()
            
            # Handle different response formats
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "")
            elif isinstance(result, dict):
                return result.get("generated_text", "")
            return str(result)
            
        except Exception as e:
            logger.error(f"Hugging Face API error: {e}")
            raise
    
    def _call_together(self, prompt: str) -> str:
        """Call Together AI API (Free tier available)"""
        try:
            import requests
            
            api_key = getattr(config, "TOGETHER_API_KEY", "")
            if not api_key:
                raise Exception("TOGETHER_API_KEY not configured")
            
            url = "https://api.together.xyz/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.model or "mistralai/Mixtral-8x7B-Instruct-v0.1",
                "messages": [
                    {"role": "system", "content": "You are an expert social media content creator. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=60)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"Together AI API error: {e}")
            raise
    
    def _call_openrouter(self, prompt: str) -> str:
        """Call OpenRouter API (Free models available)"""
        try:
            import requests
            
            api_key = getattr(config, "OPENROUTER_API_KEY", "")
            if not api_key:
                raise Exception("OPENROUTER_API_KEY not configured")
            
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/your-repo",  # Optional
                "X-Title": "Social Media Agent"  # Optional
            }
            data = {
                "model": self.model or "google/gemini-flash-1.5",  # Free model
                "messages": [
                    {"role": "system", "content": "You are an expert social media content creator. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=60)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            raise
    
    def _parse_response(self, response_text: str) -> Dict:
        """Parse LLM response into structured content"""
        # Try to extract JSON from response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            json_str = response_text
        
        # Clean JSON string more aggressively
        # Remove control characters that break JSON parsing
        json_str = json_str.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        # Remove any other control characters except spaces
        json_str = ''.join(char for char in json_str if ord(char) >= 32 or char == ' ')
        
        # Fix common JSON issues:
        # 1. Remove trailing commas before } or ]
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # 2. Try to fix unescaped quotes in string values
        # This is tricky - we'll use a simpler approach: try to parse, and if it fails, try to fix common issues
        # First, try to find and fix unescaped newlines in strings
        json_str = re.sub(r':\s*"([^"]*)"', lambda m: f': "{m.group(1).replace(chr(10), " ").replace(chr(13), " ")}"', json_str)
        
        try:
            content = json.loads(json_str)
            
            # Validate and clean
            if "on_screen_text" not in content:
                content["on_screen_text"] = []
            
            if not isinstance(content["on_screen_text"], list):
                content["on_screen_text"] = []
            
            # Ensure all required fields
            required_fields = ["hook", "script", "caption", "hashtags", "title"]
            for field in required_fields:
                if field not in content:
                    content[field] = ""
            
            return content
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response text: {response_text[:500]}")
            raise
    
    def _fallback_content(self, title: str, description: str) -> Dict:
        """Generate fallback content if LLM fails"""
        logger.warning("Using fallback content generation")
        
        # Simple fallback
        hook = f"Breaking: {title[:80]}"
        script = f"Here's what you need to know. {description[:200]}. Stay informed. Follow for more updates."
        caption = title[:100] if len(title) <= 100 else title[:97] + "..."
        hashtags = ["news", "breaking", "trending", "viral", "update"]
        
        return {
            "hook": hook,
            "script": script,
            "on_screen_text": [
                {"text": hook, "duration": 3, "start_time": 0},
                {"text": description[:50], "duration": 5, "start_time": 3}
            ],
            "caption": caption,
            "hashtags": hashtags,
            "title": f"{title[:90]} #Shorts"
        }
    
    def split_script_into_segments(self, script: str, target_duration: int = 45) -> list:
        """Split script into timed segments for on-screen text"""
        sentences = re.split(r'[.!?]+', script)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        segments = []
        current_time = 0
        words_per_second = 2.5  # Average speaking rate
        
        for sentence in sentences:
            word_count = len(sentence.split())
            duration = max(2, min(5, int(word_count / words_per_second)))
            
            segments.append({
                "text": sentence[:100],  # Limit text length
                "duration": duration,
                "start_time": current_time
            })
            
            current_time += duration
            
            if current_time >= target_duration:
                break
        
        return segments

