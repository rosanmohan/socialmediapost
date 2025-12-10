# Setup Guide - Social Media Posting Agent

This guide will walk you through setting up the agent step by step.

## Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Install FFmpeg

### Windows
1. Download from https://ffmpeg.org/download.html
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add `C:\ffmpeg\bin` to your PATH environment variable
4. Verify: `ffmpeg -version`

### macOS
```bash
brew install ffmpeg
```

### Linux
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

## Step 3: Get API Keys

### News API (Choose at least one)

#### NewsAPI.org
1. Go to https://newsapi.org/
2. Sign up for free account
3. Get your API key from dashboard
4. Free tier: 100 requests/day

#### GNews API
1. Go to https://gnews.io/
2. Sign up for free account
3. Get your API key
4. Free tier: 100 requests/day

### LLM API (Choose one)

#### OpenAI
1. Go to https://platform.openai.com/
2. Create account and add payment method
3. Go to API Keys section
4. Create new secret key
5. Recommended model: `gpt-4-turbo-preview` or `gpt-3.5-turbo`

#### Anthropic (Claude)
1. Go to https://console.anthropic.com/
2. Create account
3. Get API key
4. Recommended model: `claude-3-opus-20240229` or `claude-3-sonnet-20240229`

### Meta (Facebook & Instagram)

1. **Create Facebook App**
   - Go to https://developers.facebook.com/
   - Click "My Apps" → "Create App"
   - Choose "Business" type
   - Add "Instagram Basic Display" product
   - Add "Facebook Login" product

2. **Get App Credentials**
   - App ID: Found in app dashboard
   - App Secret: Settings → Basic → App Secret

3. **Get Access Token**
   - Go to Graph API Explorer: https://developers.facebook.com/tools/explorer/
   - Select your app
   - Add permissions: `instagram_basic`, `pages_show_list`, `pages_read_engagement`
   - Generate token → Extend to long-lived token
   - Use token exchange tool to get 60-day token

4. **Get Instagram Business Account ID**
   - Go to https://business.facebook.com/
   - Connect your Instagram Business account
   - Get Account ID from Meta Business Suite

5. **Get Facebook Page ID**
   - Go to your Facebook Page
   - Settings → Page Info
   - Page ID is shown there

### YouTube API

1. **Create Google Cloud Project**
   - Go to https://console.cloud.google.com/
   - Create new project

2. **Enable YouTube Data API v3**
   - APIs & Services → Library
   - Search "YouTube Data API v3"
   - Click Enable

3. **Create OAuth 2.0 Credentials**
   - APIs & Services → Credentials
   - Create Credentials → OAuth client ID
   - Application type: Desktop app
   - Download JSON file

4. **Get Refresh Token**
   - Run this Python script once:
   ```python
   from google_auth_oauthlib.flow import InstalledAppFlow
   from google.auth.transport.requests import Request
   import pickle
   
   SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
   CLIENT_SECRETS_FILE = "client_secret.json"  # Your downloaded file
   
   flow = InstalledAppFlow.from_client_secrets_file(
       CLIENT_SECRETS_FILE, SCOPES)
   creds = flow.run_local_server(port=0)
   
   print(f"Refresh Token: {creds.refresh_token}")
   ```
   - Save the refresh token

## Step 4: Configure Environment

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in all your API keys and credentials

3. Set your posting schedule:
   ```
   POST_TIMES=09:00,14:00,20:00
   TIMEZONE=Asia/Kolkata
   ```

## Step 5: Initialize Database

The database will be created automatically on first run, but you can test it:

```bash
python -c "from database import init_db; init_db(); print('Database initialized')"
```

## Step 6: Test Run

Run a test execution to verify everything works:

```bash
python main.py --mode run --slot test
```

This will:
- Fetch news
- Generate content
- Create video
- Attempt to publish (may fail if credentials are wrong, but you'll see where)

## Step 7: Start 24/7 Scheduler

Once testing is successful:

```bash
python main.py --mode schedule
```

The agent will now run 24/7 and post at your scheduled times.

## Troubleshooting

### "No module named 'moviepy'"
- Run: `pip install moviepy`

### "FFmpeg not found"
- Ensure FFmpeg is installed and in PATH
- Test: `ffmpeg -version`

### "Instagram publish failed"
- Verify Instagram Business account is connected
- Check access token hasn't expired
- Ensure video is under 60 seconds and 9:16 ratio

### "YouTube upload failed"
- Verify OAuth credentials are correct
- Check refresh token is valid
- Ensure video meets YouTube Shorts requirements

### "No news found"
- Check News API keys are valid
- Verify internet connection
- Check API rate limits haven't been exceeded

## Next Steps

1. Add custom background videos to `assets/backgrounds/`
2. Add custom fonts to `assets/fonts/`
3. Set up Telegram notifications (optional)
4. Monitor logs in `logs/` directory
5. Review database for post history

## Production Deployment

For production, consider:

1. **VPS/Cloud Server**: Deploy on AWS, DigitalOcean, or similar
2. **Process Manager**: Use `systemd`, `supervisord`, or `pm2`
3. **Monitoring**: Set up health checks and alerts
4. **Backup**: Regular database backups
5. **Log Rotation**: Already configured in code

Example systemd service file (`/etc/systemd/system/social-media-agent.service`):

```ini
[Unit]
Description=Social Media Posting Agent
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/SocialMediaPost
ExecStart=/usr/bin/python3 /path/to/SocialMediaPost/main.py --mode schedule
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable social-media-agent
sudo systemctl start social-media-agent
```



