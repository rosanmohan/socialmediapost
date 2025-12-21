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
        """Generates a scroll-stopping hook strictly from the user's preferred list"""
        standard_hooks = [
            "This just happened...",
            "Nobody is talking about this news",
            "This could affect you next week",
            "Big update in 30 seconds"
        ]
        
        if not self.client:
            return standard_hooks[0]

        try:
            prompt = f"""
            News Headline: {headline}
            
            Choose the MOST appropriate viral hook from this list for this news:
            1. This just happened...
            2. Nobody is talking about this news
            3. This could affect you next week
            4. Big update in 30 seconds
            
            Return ONLY the exact text of the chosen hook.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20
            )
            hook = response.choices[0].message.content.strip().replace('"', '').replace('“', '').replace('”', '')
            
            # Validation: Ensure it's one of ours
            for h in standard_hooks:
                if h.lower() in hook.lower():
                    return h
            
            return standard_hooks[0] # Fallback
        except Exception as e:
            logger.error(f"Error generating hook: {e}")
            return standard_hooks[0]

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
            "politics": "#4169E1"    # RoyalBlue
        }
        return color_map.get(category, "#FFD700") # Default Gold
