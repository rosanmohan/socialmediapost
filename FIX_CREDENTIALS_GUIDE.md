# 🔧 Fix Credentials Guide - Step by Step

## ✅ What's Working

1. ✅ **News Fetching** - Working perfectly (50 articles fetched)
2. ✅ **AI Content Generation** - Working (Groq API success)
3. ✅ **Video Generation** - Working (video created successfully)
4. ✅ **Thumbnail Generation** - Working
5. ✅ **Database** - Working

## ❌ What Needs Fixing

### 1. Instagram Publishing (OAuth Token Invalid)
**Error**: `Invalid OAuth access token - Cannot parse access token`

### 2. Facebook Publishing (OAuth Token Invalid)
**Error**: `Invalid OAuth access token - Cannot parse access token`

### 3. YouTube Publishing (OAuth Not Configured)
**Error**: `YouTube client not initialized`

### 4. Telegram Notifications (Optional - Not Critical)
**Error**: `404 Client Error: Not Found`

---

## 📋 Step-by-Step Fix Guide

### 🔵 FIX 1: Instagram & Facebook (Meta) Credentials

#### Step 1: Create Facebook App
1. Go to: **https://developers.facebook.com/**
2. Click **"My Apps"** → **"Create App"**
3. Choose **"Business"** type
4. Enter app name (e.g., "Social Media Agent")
5. Click **"Create App"**

#### Step 2: Add Products
1. In your app dashboard, click **"Add Product"**
2. Add these products:
   - **Instagram Basic Display** (for Instagram)
   - **Facebook Login** (for Facebook)
   - **Instagram Graph API** (if available)

#### Step 3: Get App Credentials
1. Go to **Settings** → **Basic**
2. Copy:
   - **App ID** → Add to `.env` as `FACEBOOK_APP_ID`
   - **App Secret** → Click "Show" and copy → Add to `.env` as `FACEBOOK_APP_SECRET`

#### Step 4: Get Access Token
1. Go to: **https://developers.facebook.com/tools/explorer/**
2. Select your app from dropdown
3. Click **"Generate Access Token"**
4. Add these permissions:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_show_list`
   - `pages_read_engagement`
   - `pages_manage_posts`
   - `business_management`
5. Click **"Generate Access Token"**
6. Copy the token
7. **Extend Token** (important!):
   - Click **"Debug"** button
   - Click **"Extend Access Token"**
   - Copy the long-lived token (60 days)
   - Add to `.env` as `FACEBOOK_ACCESS_TOKEN`

#### Step 5: Get Instagram Business Account ID
1. Go to: **https://business.facebook.com/**
2. Go to **Settings** → **Instagram Accounts**
3. Connect your Instagram Business account
4. Go to **Meta Business Suite**
5. Find your Instagram account
6. The Account ID is shown (format: numbers)
7. Add to `.env` as `INSTAGRAM_BUSINESS_ACCOUNT_ID`

#### Step 6: Get Facebook Page ID
1. Go to your Facebook Page
2. Click **Settings** → **Page Info**
3. Scroll down to find **Page ID** (numbers)
4. Or go to: `https://www.facebook.com/yourpagename`
5. View page source, search for "page_id"
6. Add to `.env` as `FACEBOOK_PAGE_ID`

#### Step 7: Update .env File
Add these lines to your `.env`:
```env
FACEBOOK_APP_ID=your_app_id_here
FACEBOOK_APP_SECRET=your_app_secret_here
FACEBOOK_ACCESS_TOKEN=your_long_lived_token_here
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_account_id_here
FACEBOOK_PAGE_ID=your_facebook_page_id_here
```

---

### 🔴 FIX 2: YouTube Credentials

#### Step 1: Create Google Cloud Project
1. Go to: **https://console.cloud.google.com/**
2. Click **"Select a project"** → **"New Project"**
3. Enter project name (e.g., "Social Media Agent")
4. Click **"Create"**

#### Step 2: Enable YouTube Data API
1. In your project, go to **"APIs & Services"** → **"Library"**
2. Search for **"YouTube Data API v3"**
3. Click on it → Click **"Enable"**

#### Step 3: Create OAuth 2.0 Credentials
1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. If prompted, configure OAuth consent screen:
   - User Type: **External** (or Internal if you have Google Workspace)
   - App name: "Social Media Agent"
   - User support email: Your email
   - Developer contact: Your email
   - Click **"Save and Continue"**
   - Scopes: Add `https://www.googleapis.com/auth/youtube.upload`
   - Click **"Save and Continue"**
   - Test users: Add your Google account email
   - Click **"Save and Continue"**
4. Back to Credentials:
   - Application type: **"Desktop app"**
   - Name: "Social Media Agent Desktop"
   - Click **"Create"**
5. Download the JSON file (save as `client_secret.json` in project folder)

#### Step 4: Get Refresh Token
1. Create a file `get_youtube_token.py`:
```python
from google_auth_oauthlib.flow import InstalledAppFlow
import json

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
CLIENT_SECRETS_FILE = "client_secret.json"

flow = InstalledAppFlow.from_client_secrets_file(
    CLIENT_SECRETS_FILE, SCOPES)
creds = flow.run_local_server(port=0)

print(f"\n✅ Success! Add these to your .env file:\n")
print(f"YOUTUBE_CLIENT_ID={creds.client_id}")
print(f"YOUTUBE_CLIENT_SECRET={creds.client_secret}")
print(f"YOUTUBE_REFRESH_TOKEN={creds.refresh_token}")
```

2. Run it:
```bash
python get_youtube_token.py
```

3. A browser window will open - sign in with your Google account
4. Grant permissions
5. Copy the output and add to `.env`

#### Step 5: Update .env File
Add these lines:
```env
YOUTUBE_CLIENT_ID=your_client_id_here
YOUTUBE_CLIENT_SECRET=your_client_secret_here
YOUTUBE_REFRESH_TOKEN=your_refresh_token_here
```

---

### 🟡 FIX 3: Telegram Notifications (Optional)

#### Step 1: Create Telegram Bot
1. Open Telegram
2. Search for **@BotFather**
3. Send: `/newbot`
4. Follow instructions:
   - Choose a name for your bot
   - Choose a username (must end with `bot`)
5. BotFather will give you a token
6. Copy the token

#### Step 2: Get Your Chat ID
1. Search for **@userinfobot** on Telegram
2. Start a conversation
3. It will reply with your chat ID (numbers)
4. Copy the chat ID

#### Step 3: Update .env File
Add these lines:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

---

## 📝 Complete .env Template

After getting all credentials, your `.env` should look like:

```env
# News APIs (Already working)
NEWS_API_KEY=your_newsapi_key
GNEWS_API_KEY=your_gnews_key

# LLM (Already working)
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_key

# Meta (Instagram & Facebook) - ADD THESE
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_long_lived_token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_account_id
FACEBOOK_PAGE_ID=your_facebook_page_id

# YouTube - ADD THESE
YOUTUBE_CLIENT_ID=your_client_id
YOUTUBE_CLIENT_SECRET=your_client_secret
YOUTUBE_REFRESH_TOKEN=your_refresh_token

# Telegram (Optional) - ADD THESE
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Scheduling (Already set)
POST_TIMES=09:00,14:00,20:00
TIMEZONE=Asia/Kolkata
```

---

## ✅ Testing After Adding Credentials

1. **Test Instagram/Facebook**:
   ```bash
   python main.py --mode run --slot test
   ```
   Check logs - should see "Instagram post published" or "Facebook video uploaded"

2. **Test YouTube**:
   Same command - should see "YouTube video uploaded"

3. **Test Telegram**:
   If configured, you'll receive notifications on errors/success

---

## ⚠️ Important Notes

1. **Access Tokens Expire**: Facebook tokens expire in 60 days. You'll need to refresh them.
2. **OAuth Consent**: YouTube may require app verification if you exceed quota.
3. **Rate Limits**: Each platform has rate limits - don't post too frequently.
4. **Test Mode**: Start with test posts before going live.

---

## 🎯 Priority Order

1. **YouTube** (Easiest to set up)
2. **Instagram/Facebook** (More complex, but most important)
3. **Telegram** (Optional - just for notifications)

---

## 📚 Additional Resources

- **Meta Developers**: https://developers.facebook.com/docs/
- **YouTube API**: https://developers.google.com/youtube/v3
- **Telegram Bot API**: https://core.telegram.org/bots/api

---

**Once you add these credentials, the agent will be fully functional!** 🚀



