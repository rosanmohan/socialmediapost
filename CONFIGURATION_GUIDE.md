# Configuration Guide - What You Need to Provide

This guide shows exactly what personal information and API keys you need to configure.

## 📋 Quick Checklist

### ✅ REQUIRED (Minimum to Run)
1. **News API Key** (at least one) - FREE
2. **LLM API Key** (choose one free option) - FREE
3. **Social Media API Credentials** (for platforms you want to post to)

### ⚠️ OPTIONAL
- Telegram notifications (for alerts)
- Custom backgrounds/fonts

---

## 1. News API Keys (REQUIRED - Choose at least ONE)

### Option A: NewsAPI.org (FREE - 100 requests/day)
1. Go to: https://newsapi.org/register
2. Sign up (free account)
3. Get your API key from dashboard
4. Add to `.env`: `NEWS_API_KEY=your_key_here`

### Option B: GNews API (FREE - 100 requests/day)
1. Go to: https://gnews.io/register
2. Sign up (free account)
3. Get your API key
4. Add to `.env`: `GNEWS_API_KEY=your_key_here`

**You can use BOTH for more news sources!**

---

## 2. LLM API Key (REQUIRED - Choose ONE FREE option)

### 🆓 Option A: Groq (RECOMMENDED - FREE, Very Fast)
1. Go to: https://console.groq.com/
2. Sign up (free account)
3. Go to API Keys section
4. Create new API key
5. Add to `.env`:
   ```
   LLM_PROVIDER=groq
   GROQ_API_KEY=your_key_here
   LLM_MODEL=llama-3.1-70b-versatile  # or leave empty for default
   ```

### 🆓 Option B: Hugging Face (FREE - No key needed for some models)
1. Go to: https://huggingface.co/join
2. Sign up (free account)
3. Go to Settings → Access Tokens
4. Create new token
5. Add to `.env`:
   ```
   LLM_PROVIDER=huggingface
   HUGGINGFACE_API_KEY=your_token_here
   LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2
   ```

### 🆓 Option C: Together AI (FREE tier available)
1. Go to: https://api.together.xyz/
2. Sign up (free account)
3. Get API key from dashboard
4. Add to `.env`:
   ```
   LLM_PROVIDER=together
   TOGETHER_API_KEY=your_key_here
   LLM_MODEL=mistralai/Mixtral-8x7B-Instruct-v0.1
   ```

### 🆓 Option D: OpenRouter (FREE models available)
1. Go to: https://openrouter.ai/
2. Sign up (free account)
3. Get API key from keys page
4. Add to `.env`:
   ```
   LLM_PROVIDER=openrouter
   OPENROUTER_API_KEY=your_key_here
   LLM_MODEL=google/gemini-flash-1.5  # Free model
   ```

### 💰 Paid Options (for later upgrade)
- **OpenAI**: `LLM_PROVIDER=openai` + `OPENAI_API_KEY=...`
- **Anthropic**: `LLM_PROVIDER=anthropic` + `ANTHROPIC_API_KEY=...`

---

## 3. Social Media API Credentials

### Instagram & Facebook (Meta)

**You need:**
1. Facebook App ID
2. Facebook App Secret
3. Long-lived Access Token
4. Instagram Business Account ID
5. Facebook Page ID

**Setup Steps:**
1. Go to: https://developers.facebook.com/
2. Click "My Apps" → "Create App"
3. Choose "Business" type
4. Add products:
   - "Instagram Basic Display"
   - "Facebook Login"
5. Get App ID and App Secret from Settings → Basic
6. Go to: https://developers.facebook.com/tools/explorer/
7. Select your app
8. Add permissions: `instagram_basic`, `pages_show_list`, `pages_read_engagement`
9. Generate token → Extend to long-lived (60 days)
10. Get Instagram Business Account ID from Meta Business Suite
11. Get Facebook Page ID from your page settings

**Add to `.env`:**
```
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_long_lived_token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_ig_account_id
FACEBOOK_PAGE_ID=your_page_id
```

### YouTube

**You need:**
1. OAuth Client ID
2. OAuth Client Secret
3. Refresh Token

**Setup Steps:**
1. Go to: https://console.cloud.google.com/
2. Create new project
3. Enable "YouTube Data API v3"
4. Go to Credentials → Create Credentials → OAuth client ID
5. Choose "Desktop app"
6. Download JSON file
7. Run this Python script once to get refresh token:

```python
from google_auth_oauthlib.flow import InstalledAppFlow
import json

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
CLIENT_SECRETS_FILE = "client_secret.json"  # Your downloaded file

flow = InstalledAppFlow.from_client_secrets_file(
    CLIENT_SECRETS_FILE, SCOPES)
creds = flow.run_local_server(port=0)

print(f"Client ID: {creds.client_id}")
print(f"Client Secret: {creds.client_secret}")
print(f"Refresh Token: {creds.refresh_token}")
```

**Add to `.env`:**
```
YOUTUBE_CLIENT_ID=your_client_id
YOUTUBE_CLIENT_SECRET=your_client_secret
YOUTUBE_REFRESH_TOKEN=your_refresh_token
```

---

## 4. Optional: Telegram Notifications

1. Message @BotFather on Telegram
2. Create a bot: `/newbot`
3. Get bot token
4. Get your chat ID: Message @userinfobot
5. Add to `.env`:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

---

## 5. Scheduling (Optional - Has Defaults)

Default: Posts at 9:00 AM, 2:00 PM, 8:00 PM (IST)

To change, edit `.env`:
```
POST_TIMES=09:00,14:00,20:00  # 24-hour format
TIMEZONE=Asia/Kolkata  # Your timezone
```

---

## 📝 Summary: Minimum Required

To get started with **FREE options only**, you need:

1. ✅ **NewsAPI.org key** (or GNews) - FREE
2. ✅ **Groq API key** (or other free LLM) - FREE
3. ⚠️ **Social media credentials** (only if you want to auto-post)

**Note:** You can test the agent WITHOUT social media credentials - it will generate videos but won't post them.

---

## 🚀 Quick Start Configuration

Create `.env` file with minimum:

```env
# News (REQUIRED - choose one)
NEWS_API_KEY=your_newsapi_key

# LLM (REQUIRED - choose one free option)
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_key

# Social Media (OPTIONAL - add when ready)
# FACEBOOK_APP_ID=
# FACEBOOK_APP_SECRET=
# FACEBOOK_ACCESS_TOKEN=
# INSTAGRAM_BUSINESS_ACCOUNT_ID=
# FACEBOOK_PAGE_ID=
# YOUTUBE_CLIENT_ID=
# YOUTUBE_CLIENT_SECRET=
# YOUTUBE_REFRESH_TOKEN=

# Scheduling (OPTIONAL - has defaults)
POST_TIMES=09:00,14:00,20:00
TIMEZONE=Asia/Kolkata
```

---

## 🔒 Security Notes

- **NEVER commit `.env` file to git** (already in .gitignore)
- Keep API keys secret
- Rotate keys periodically
- Use environment variables in production

---

## ❓ Need Help?

- Check `setup_guide.md` for detailed API setup
- Run `python quick_start.py` to test components
- Check logs in `logs/` directory



