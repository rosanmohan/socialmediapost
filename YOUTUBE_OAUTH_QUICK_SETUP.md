# YouTube OAuth Setup - Quick Guide

## 🎯 Goal
Get a YouTube refresh token that lasts 6+ months and auto-refreshes access tokens.

---

## 📝 Prerequisites

You need a Google Cloud Project with YouTube Data API v3 enabled.

### Step 1: Create/Configure Google Cloud Project

1. Go to: https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Enable **YouTube Data API v3**:
   - Go to: https://console.cloud.google.com/apis/library/youtube.googleapis.com
   - Click "Enable"

### Step 2: Create OAuth Credentials

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. If prompted, configure OAuth consent screen:
   - User Type: **External**
   - App name: "Social Media Poster" (or any name)
   - User support email: Your email
   - Developer contact: Your email
   - Scopes: Add `https://www.googleapis.com/auth/youtube.upload`
   - Test users: Add your email
4. Create OAuth client ID:
   - Application type: **Desktop app**
   - Name: "Social Media Desktop"
5. Download the JSON file or copy:
   - **Client ID**
   - **Client Secret**

---

## 🔧 Step 3: Generate Refresh Token

### Option A: Use the built-in script (Recommended)

```bash
python get_youtube_refresh_token.py
```

**The script will:**
1. Ask for your Client ID and Client Secret
2. Open a browser for you to authorize
3. Save the refresh token automatically

### Option B: Manual setup

If the script doesn't work, add these to your `.env`:

```bash
YOUTUBE_CLIENT_ID=your_client_id_here
YOUTUBE_CLIENT_SECRET=your_client_secret_here
```

Then run:
```bash
python get_youtube_refresh_token.py
```

---

## ✅ Step 4: Verify in .env

After running the script, your `.env` should have:

```bash
YOUTUBE_CLIENT_ID=xxxxx.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=xxxxx
YOUTUBE_REFRESH_TOKEN=1//xxxxx
```

---

## 🧪 Step 5: Test

```bash
python main_1.py
```

**Expected output:**
```
✅ Video generated
✅ Posted to YouTube
✅ Posted to Facebook
✅ Pipeline completed successfully
```

---

## ⏰ Token Lifespan

| Token Type | Lifespan | Auto-Refresh? | Manual Renewal |
|------------|----------|---------------|----------------|
| Access Token | 1 hour | ✅ Yes (automatic) | Never |
| Refresh Token | 6+ months | ❌ No | 1-2 times/year |

**How it works:**
1. Your code uses the **refresh token** (lasts 6+ months)
2. The refresh token automatically gets new **access tokens** every hour
3. You only need to regenerate the refresh token 1-2 times per year

---

## 🐛 Common Issues

### "YouTube Data API v3 has not been used"
→ Enable the API: https://console.cloud.google.com/apis/library/youtube.googleapis.com

### "invalid_grant" error
→ Refresh token expired, run `get_youtube_refresh_token.py` again

### "redirect_uri_mismatch"
→ Add `http://localhost:8080/` to authorized redirect URIs in Google Cloud Console

### "Access blocked: This app's request is invalid"
→ Add your email to test users in OAuth consent screen

---

## 📅 Set Reminder

**Add to calendar:**
- [ ] **Every 6 months:** Renew YouTube refresh token
  - Run: `python get_youtube_refresh_token.py`
  - Takes 2 minutes

**Combined with Facebook:**
- Facebook page token: Never expires ✅
- YouTube refresh token: Every 6 months
- **Total manual work: 2 minutes every 6 months!**

---

## 🎯 Summary

**This is the BEST automation possible for YouTube:**
- ✅ Refresh token lasts 6+ months
- ✅ Access tokens auto-refresh every hour
- ✅ Only 2 minutes of work every 6 months
- ✅ No better option exists (YouTube doesn't offer never-expiring tokens)

**Ready to set it up?** Run:
```bash
python get_youtube_refresh_token.py
```
