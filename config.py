"""
Configuration management for the Social Media Agent
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = Path(__file__).parent
env_path = BASE_DIR / ".env"

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv() # Fallback to standard loading
DATA_DIR = BASE_DIR / "data"
MEDIA_DIR = DATA_DIR / "generated_media"
LOGS_DIR = BASE_DIR / "logs"
ASSETS_DIR = BASE_DIR / "assets"
BACKGROUNDS_DIR = ASSETS_DIR / "backgrounds"
FONTS_DIR = ASSETS_DIR / "fonts"
AUDIO_DIR = ASSETS_DIR / "audio"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
MEDIA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)
BACKGROUNDS_DIR.mkdir(exist_ok=True)
FONTS_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)

# News API Configuration
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "")

# LLM Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
# Free LLM Options
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
XAI_API_KEY = os.getenv("XAI_API_KEY", "") # xAI Grok API Key

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # Default to free Grok
# Model defaults for each provider (Updated Nov 2025)
# Best models for social media content generation:
# - llama-3.3-70b-versatile: Latest, best quality (if available)
# - llama-3.1-70b-versatile: High quality, reliable
# - llama-3.1-8b-instant: Fast, good quality (default - best balance)
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")  # Default: Fast and reliable
GROK_VIDEO_MODEL = os.getenv("GROK_VIDEO_MODEL", "grok-imagine")  # Model for video generation
GROK_IMAGE_MODEL = os.getenv("GROK_IMAGE_MODEL", "grok-2-image-1212")  # Confirmed working image model

# Meta API Configuration
FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID", "")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET", "")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "")

# Publishing Toggles
# Set to 'false' to disable publishing to specific platforms (useful for testing)
ENABLE_PUBLISH_INSTAGRAM = os.getenv("ENABLE_PUBLISH_INSTAGRAM", "false").lower() == "true"
ENABLE_PUBLISH_FACEBOOK = os.getenv("ENABLE_PUBLISH_FACEBOOK", "false").lower() == "true"
ENABLE_PUBLISH_YOUTUBE = os.getenv("ENABLE_PUBLISH_YOUTUBE", "false").lower() == "true"

# YouTube API Configuration
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN", "")

# Scheduling Configuration
POST_TIMES = os.getenv("POST_TIMES", "09:00,14:00,20:00").split(",")
INDIA_POST_TIMES = os.getenv("INDIA_POST_TIMES", "10:00,15:00,21:00").split(",")
CRICKET_POST_TIMES = os.getenv("CRICKET_POST_TIMES", "11:00,16:00,22:00").split(",")
MOVIES_POST_TIMES = os.getenv("MOVIES_POST_TIMES", "08:00,13:00,19:00").split(",")
CATEGORIES = ["general", "india", "cricket", "movies"]
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")

# Media Generation Configuration
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "gtts")
BACKGROUND_VIDEO_PATH = BACKGROUNDS_DIR
FONT_PATH = FONTS_DIR / "arial.ttf"

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/social_media_agent.db")

# Monitoring Configuration
ENABLE_NOTIFICATIONS = os.getenv("ENABLE_NOTIFICATIONS", "true").lower() == "true"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Retry Configuration
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY_SECONDS = int(os.getenv("RETRY_DELAY_SECONDS", "60"))

# Video Configuration
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920  # 9:16 aspect ratio
VIDEO_FPS = 30
VIDEO_DURATION_SECONDS = 45  # Target duration

# Content Configuration
MAX_NEWS_ITEMS_TO_FETCH = 20
TOP_N_NEWS_TO_CONSIDER = 3
MIN_NEWS_AGE_HOURS = 0
MAX_NEWS_AGE_HOURS = 12

# Google Drive Assets (Optional - for cloud storage of large files)
# Extract ID from URL: drive.google.com/drive/folders/YOUR_ID_HERE
DRIVE_AUDIO_FOLDER_ID = os.getenv("DRIVE_AUDIO_FOLDER_ID", "")
DRIVE_BACKGROUNDS_FOLDER_ID = os.getenv("DRIVE_BACKGROUNDS_FOLDER_ID", "")
