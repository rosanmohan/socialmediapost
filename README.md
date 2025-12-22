# Social Media Posting Agent 🤖

An automated 24/7 agent that finds trending news, generates engaging 9:16 vertical videos, and auto-posts to Instagram Reels, YouTube Shorts, and Facebook.

## Features

- ✅ **24/7 Automated Operation**: Runs continuously with scheduled posts (2-3 times per day)
- ✅ **News Discovery**: Fetches trending news from multiple sources (NewsAPI, GNews, RSS feeds)
- ✅ **AI Content Generation**: Uses LLM (OpenAI/Anthropic) to generate scripts, captions, and hashtags
- ✅ **Video Generation**: Creates 9:16 vertical videos with text overlays and TTS audio
- ✅ **Multi-Platform Publishing**: Auto-posts to Instagram, YouTube Shorts, and Facebook
- ✅ **Database Logging**: Tracks all posts, news items, and publishing status
- ✅ **Error Handling**: Robust retry logic and error notifications

## Architecture

```
┌─────────────┐
│  Scheduler  │ (Runs 24/7, triggers 2-3x daily)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Pipeline   │ (Orchestrates all components)
└──────┬──────┘
       │
       ├──► News Service (Fetch & Rank News)
       ├──► Content Generator (LLM → Script/Caption/Hashtags)
       ├──► Media Generator (Create 9:16 Video)
       └──► Publishers (Instagram/YouTube/Facebook)
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- FFmpeg (for video processing)
- API keys for:
  - NewsAPI.org or GNews API
  - OpenAI or Anthropic (for content generation)
  - Meta Graph API (Facebook & Instagram)
  - YouTube Data API v3

### 2. Installation

```bash
# Clone or navigate to project directory
cd SocialMediaPost

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (if not already installed)
# Windows: Download from https://ffmpeg.org/download.html
# macOS: brew install ffmpeg
# Linux: sudo apt-get install ffmpeg
```

### 3. Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` and fill in your API keys:

```env
# News APIs (at least one required)
NEWS_API_KEY=your_newsapi_key
GNEWS_API_KEY=your_gnews_key

# LLM (choose one)
OPENAI_API_KEY=your_openai_key
# OR
ANTHROPIC_API_KEY=your_anthropic_key
LLM_PROVIDER=openai  # or anthropic
LLM_MODEL=gpt-4-turbo-preview

# Meta API (Facebook & Instagram)
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_long_lived_token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_ig_account_id
FACEBOOK_PAGE_ID=your_page_id

# YouTube API
YOUTUBE_CLIENT_ID=your_client_id
YOUTUBE_CLIENT_SECRET=your_client_secret
YOUTUBE_REFRESH_TOKEN=your_refresh_token

# Scheduling
POST_TIMES=09:00,14:00,20:00  # 24-hour format
TIMEZONE=Asia/Kolkata
```

### 4. API Setup Guides

#### Meta (Facebook & Instagram)
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create an app → Add Instagram Basic Display and Facebook Login
3. Get App ID and App Secret
4. Generate long-lived access token
5. Get your Instagram Business Account ID and Facebook Page ID

#### YouTube
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project → Enable YouTube Data API v3
3. Create OAuth 2.0 credentials
4. Run OAuth flow once to get refresh token
5. Add refresh token to `.env`

#### News APIs
- **NewsAPI**: Sign up at [newsapi.org](https://newsapi.org/)
- **GNews**: Sign up at [gnews.io](https://gnews.io/)

### 5. Optional: Add Background Assets

Place background videos/images in `assets/backgrounds/`:
- Supported: `.mp4`, `.jpg`, `.png`
- Recommended: 9:16 aspect ratio (1080x1920)

Place fonts in `assets/fonts/`:
- Default: Arial (system font)
- Custom: Add `.ttf` files

## Usage

## Usage

### Run Manually (Local)
```bash
python main.py
```
This will fetch the latest news, generate a Viral-style video, and auto-post if enabled.

### Run Automated (GitHub Actions)
The agent is already configured to run automatically on a schedule via GitHub Actions.
- **Workflow:** `Run Social Media Agent`
- **Schedule:** 5 times daily (7:00 AM, 11:00 AM, 3:00 PM, 7:00 PM, 11:00 PM IST)
- **Manual Trigger:** Go to GitHub Actions → Select workflow → click "Run workflow".

### Run as Background Service (Linux/macOS)
```bash
# Using nohup
nohup python main.py --mode schedule > agent.log 2>&1 &

# Or using systemd (create service file)
```

### Run as Windows Service
Use Task Scheduler or a service wrapper like NSSM (Non-Sucking Service Manager).

## Project Structure

```
SocialMediaPost/
├── main.py                 # Main entry point (Runs Viral Pipeline)
├── pipeline_viral.py       # Viral Single-Story orchestrator
├── media_generator_viral.py # High-impact video generator
├── viral_content_service.py # Hook & story logic
├── voice_service.py        # AI voiceover (Edge-TTS)
├── news_service.py         # News fetching & ranking
├── publishers.py           # Social media publishing
├── royalty_free_audio.py    # Background music manager
├── google_drive_assets.py  # Drive integration
├── database.py             # Database models
├── config.py               # Configuration
├── requirements.txt        # Dependencies
├── .env                    # Environment variables (local setup)
├── data/                   # Database & generated media cache
├── logs/                   # Application logs
└── assets/                 # Backgrounds, fonts, local audio
    ├── backgrounds/
    └── fonts/
```

## Database Schema

- **news_items**: Fetched news articles
- **posts**: Generated posts with content
- **publish_logs**: Publishing status per platform
- **system_logs**: System-level logs and errors

## Monitoring

- Check logs in `logs/` directory
- Query database for post history
- Set up Telegram/email notifications (configure in `.env`)

## Troubleshooting

### Video Generation Fails
- Ensure FFmpeg is installed and in PATH
- Check video file permissions
- Verify background assets exist

### Publishing Fails
- Verify API credentials are correct
- Check token expiration (refresh if needed)
- Review platform rate limits
- Check logs for specific error messages

### No News Found
- Verify News API keys are valid
- Check internet connection
- Review news source availability

## Rate Limits & Best Practices

- **Instagram**: ~25 posts per day (respect limits)
- **YouTube**: No strict limit, but avoid spam
- **Facebook**: Varies by account type
- **News APIs**: Check your plan's limits

## Legal & Policy Notes

⚠️ **Important**:
- Use official APIs only (no scraping)
- Respect platform terms of service
- Generate original content (don't copy full articles)
- Credit sources when appropriate
- Review content before auto-posting (especially for sensitive topics)

## License

This project is provided as-is for educational and personal use.

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review database for error details
3. Verify all API credentials are correct
4. Ensure all dependencies are installed

---

**Built with ❤️ for automated social media content creation**



