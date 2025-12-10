# Bulletin YouTube Shorts Generator

## Overview

`main_1.py` creates **20-second YouTube Shorts** with a different format than `main.py`:

- **Format**: News bulletin style
- **Content**: Top 5 trending news items displayed as a bulletin
- **Background**: Random background video from `assets/backgrounds/`
- **Audio**: Trending YouTube Shorts audio (if available)
- **Duration**: Exactly 20 seconds
- **Platform**: YouTube Shorts only

## How It Works

1. **Fetches Top 5 News**: Gets the top 5 trending news items
2. **Gets Royalty-Free Audio**: Always includes copyright-safe background music
   - Tries YouTube Audio Library (royalty-free)
   - Falls back to programmatically generated music
   - **Guaranteed to have audio** - no silent videos
3. **Creates Bulletin Video**: 
   - Random background video
   - News items displayed as numbered bulletins (1-5)
   - Each news item appears for equal time (4 seconds each)
   - Fade in/out animations
   - **Always includes background music** (copyright-safe)
4. **Uploads to YouTube**: Posts as a YouTube Short

## Usage

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run bulletin generator
python main_1.py
```

## Requirements

- All the same requirements as `main.py`
- **Audio is ALWAYS included** - no silent videos
- **Copyright-safe**: Uses only royalty-free music sources
- **Optional**: `yt-dlp` for accessing YouTube Audio Library
  ```bash
  pip install yt-dlp
  ```
  (If not installed, programmatically generated music will be used)

## Differences from main.py

| Feature | main.py | main_1.py |
|---------|---------|-----------|
| Duration | 40-50 seconds | 20 seconds |
| Content | Single news story with script | Top 5 news bulletin |
| Audio | TTS (text-to-speech) | Royalty-free background music (always included) |
| Text Style | Full script with timing | Numbered news items |
| Platforms | Instagram, YouTube, Facebook | YouTube only |
| Background | Random video | Random video |

## Files Created

- `media_generator_bulletin.py` - Generates 20-second bulletin videos
- `youtube_trending_audio.py` - Gets trending audio from YouTube Shorts
- `pipeline_bulletin.py` - Orchestrates the bulletin pipeline
- `main_1.py` - Entry point

## Notes

- Videos are exactly 20 seconds (YouTube Shorts requirement)
- **Audio is ALWAYS included** - uses royalty-free music (copyright-safe)
- **No copyright issues** - all audio sources are royalty-free and safe for YouTube
- News items are displayed as numbered bulletins (1-5)
- Each news item gets equal screen time (4 seconds each)
- Background videos are randomly selected from `assets/backgrounds/`
- Audio sources tried in order:
  1. YouTube Audio Library (royalty-free, if yt-dlp installed)
  2. Programmatically generated music (always works)
  3. Simple background tone (guaranteed fallback)

## Troubleshooting

**No audio in video?**
- Audio is **always included** - if you see this, it's a bug
- Check logs for audio generation errors
- Audio is generated programmatically if downloads fail

**Copyright concerns?**
- All audio sources are royalty-free and copyright-safe
- Uses YouTube Audio Library or programmatically generated music
- No risk of copyright claims

**YouTube upload fails?**
- Check your YouTube credentials in `.env`
- Make sure `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, and `YOUTUBE_REFRESH_TOKEN` are set

**No news items?**
- Check your news API keys in `.env`
- Make sure `NEWS_API_KEY` or `GNEWS_API_KEY` is configured

