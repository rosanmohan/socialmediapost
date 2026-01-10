"""
Viral Content Service
Handles hook generation, story summarization, and viral formatting.
Supports both OpenAI and Groq (via OpenAI-compatible API).
"""
import openai
import os
from loguru import logger
import config

class ViralContentService:
    def __init__(self):
        self.provider = config.LLM_PROVIDER.lower()
        self.model = config.LLM_MODEL
        
        # Determine API Key and Base URL
        if self.provider == "openai":
            self.api_key = config.OPENAI_API_KEY
            self.base_url = None
            if not self.model: self.model = "gpt-4o-mini"
        elif self.provider == "groq":
            self.api_key = config.GROQ_API_KEY
            self.base_url = "https://api.groq.com/openai/v1"
            if not self.model: self.model = "llama-3.1-8b-instant"
        else:
            # Fallback/Other
            self.api_key = config.OPENAI_API_KEY or config.GROQ_API_KEY
            self.base_url = "https://api.groq.com/openai/v1" if config.GROQ_API_KEY else None
            self.model = config.LLM_MODEL or "llama-3.1-8b-instant"

        if self.api_key:
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            logger.info(f"✅ ViralContentService: Initialized with {self.provider} (Model: {self.model})")
        else:
            self.client = None
            logger.warning("⚠️ ViralContentService: No LLM API key found! Using fallbacks.")

    def generate_viral_hook(self, headline: str) -> str:
        """Generates a creative, scroll-stopping viral hook using the LLM"""
        if not self.client:
            return "This just happened..."  # Fallback only if LLM fails
            
        try:
            prompt = f"""
            News Headline: {headline}
            
            Write a 3-6 word "Viral Hook" for this news. 
            The goal is to make a user STOP scrolling on TikTok/Reels immediately.
            
            Rules:
            - MAX 6 words.
            - Must be punchy, urgent, or mysterious.
            - Do NOT clickbait falsely, but be dramatic.
            - First letter MUST be capitalized. No ending punctuation unless it's a question mark.
            
            Examples of good hooks:
            - You won't believe this
            - This changes everything
            - Is this the end?
            - Finally, it happened
            - Avoid this mistake
            
            Return ONLY the hook text.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20,
                temperature=0.8  # Higher temperature for more creativity
            )
            hook = response.choices[0].message.content.strip().replace('"', '').replace('“', '').replace('”', '')
            
            # Basic validation
            if len(hook.split()) > 10:  # If it generated a sentence, truncate it or fallback
                return "Breaking News Update"
            
            return hook
            
        except Exception as e:
            logger.error(f"Error generating creative hook: {e}")
            return "This just happened..."

    def summarize_to_story(self, headline: str, content: str) -> list:
        """Turns a news article into a 5-part concise narrative (~100 words total)"""
        if not self.client:
            return [
                f"Big update today on {headline[:40]}...",
                "Details are emerging about this significant development.",
                "Experts are analyzing the potential long-term impact.",
                "Stakeholders are reacting as the situation continues to unfold.",
                "We will monitor this story and provide updates."
            ]

        try:
            prompt = f"""
            News Item: {headline}
            Details: {content}
            
            Rewrite this into a concise, clear 5-part narrative script for a news reel.
            The TOTAL length of all 5 sentences combined must be around 100 words.
            Each part must be a complete, easy-to-understand sentence.
            
            Logical Flow:
            1. The What: State the news clearly.
            2. The Detail: A key piece of data or info.
            3. The Context: Why it's happening now.
            4. The Reaction/Impact: What people are saying or what is affected.
            5. The Conclusion: Current status or next steps.
            
            Return exactly 5 lines, one short sentence per line. NO labels.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            parts = [p.strip() for p in response.choices[0].message.content.strip().split("\n") if p.strip()]
            
            # Clean up any potential labels (Part 1:, etc.)
            filtered_parts = []
            for p in parts:
                clean_p = p.split(": ", 1)[-1] if (":" in p[:15] and ("Part" in p or "Line" in p or p[0].isdigit())) else p
                filtered_parts.append(clean_p)
            
            return filtered_parts[:5]
        except Exception as e:
            logger.error(f"Error summarizing story: {e}")
            return [f"Breaking news: {headline}", "Developments are occurring rapidly.", "The situation is evolving by the hour.", "Stay tuned for further updates."]

    def rewrite_headlines(self, headlines: list) -> list:
        """Rewrites multiple headlines into viral hooks at once"""
        if not self.client:
            return headlines

        try:
            joined_headlines = "\n".join([f"{i+1}. {h}" for i, h in enumerate(headlines)])
            prompt = (
                f"Rewrite these news headlines into catchy, viral video hooks (MAX 8 words each).\n"
                f"Make them punchy and dramatic. Output ONLY the rewritten headlines, one per line, numbered.\n\n"
                f"Headlines:\n{joined_headlines}"
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            
            lines = response.choices[0].message.content.strip().split("\n")
            rewritten = []
            for line in lines:
                if "." in line[:3]:
                    rewritten.append(line.split(".", 1)[1].strip())
                elif line.strip():
                    rewritten.append(line.strip())
            
            return rewritten[:len(headlines)]
        except Exception as e:
            logger.error(f"Error rewriting headlines: {e}")
            return headlines

    def get_color_code(self, category: str) -> str:
        """Returns the accent color based on news type"""
        category = category.lower()
        color_map = {
            "war": "#FF0000",        # Red
            "conflict": "#FF4500",   # OrangeRed
            "health": "#FFFFFF",     # White
            "celebrity": "#FF00FF",  # Magenta
            "economy": "#0000FF",    # Blue
            "tech": "#00FF00",       # Green
            "crime": "#8B0000",      # DarkRed
            "politics": "#4169E1",   # RoyalBlue
            "india": "#FF9933",      # saffron
            "cricket": "#1A5276",    # Deep Blue
            "movies": "#E91E63"      # Vivid Pink/Movie Style
        }
        return color_map.get(category, "#FFD700") # Default Gold
