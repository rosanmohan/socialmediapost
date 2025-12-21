# Quick Setup Guide - Long-Lived Tokens

## 🎯 Goal
Get Facebook tokens that last **60 days** instead of 2 hours, and YouTube tokens that auto-refresh for 6 months.

---

## 📘 Part 1: Facebook Long-Lived Token (60 days)

### Step 1: Run the token generator
```bash
python get_facebook_long_lived_token.py
```

### Step 2: Follow the prompts

The script will ask for:
1. **Short-lived token** - Get from https://developers.facebook.com/tools/explorer/
2. **App ID** - From your Facebook App settings
3. **App Secret** - From your Facebook App settings
4. **Page ID** (optional) - For page tokens that never expire

### Step 3: Copy the token to .env

The script will give you a long-lived token. Add it to your `.env`:

```bash
FACEBOOK_ACCESS_TOKEN=your_long_lived_token_here
```

### ✅ Result:
- Token lasts **60 days** instead of 2 hours
- Or **never expires** if you use page token
- Auto-posting works for 60 days without manual intervention

---

## 📘 Part 2: YouTube Refresh Token (6 months)

### Step 1: Run the YouTube token generator
```bash
python get_youtube_refresh_token.py
```

### Step 2: Follow the browser OAuth flow

1. Browser will open
2. Sign in to your YouTube account
3. Grant permissions
4. Script will save the **refresh token**

### Step 3: Verify tokens in .env

Make sure your `.env` has:

```bash
YOUTUBE_CLIENT_ID=your_client_id
YOUTUBE_CLIENT_SECRET=your_client_secret
YOUTUBE_REFRESH_TOKEN=your_refresh_token
```

### ✅ Result:
- Refresh token lasts **6+ months**
- Access tokens auto-refresh every hour
- No manual intervention for 6 months

---

## 📘 Part 3: Enable Publishing

### Update your .env:

```bash
# Enable the platforms you want
ENABLE_PUBLISH_YOUTUBE=true
ENABLE_PUBLISH_INSTAGRAM=true
ENABLE_PUBLISH_FACEBOOK=true
```

### For Instagram, also add:

```bash
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_business_id
FACEBOOK_PAGE_ID=your_facebook_page_id
```

---

## 🧪 Part 4: Test Locally

```bash
python main_1.py
```

**Expected output:**
```
✅ Video generated
✅ Posted to YouTube
✅ Posted to Instagram
✅ Posted to Facebook
✅ Pipeline completed successfully
```

---

## 🚀 Part 5: Deploy to GitHub Actions

### Step 1: Add secrets to GitHub

Go to: **Settings** → **Secrets and variables** → **Actions**

Add these secrets:
- `FACEBOOK_ACCESS_TOKEN` (your long-lived token)
- `INSTAGRAM_BUSINESS_ACCOUNT_ID`
- `FACEBOOK_PAGE_ID`
- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`
- `YOUTUBE_REFRESH_TOKEN`

### Step 2: Enable in workflow

Edit `.github/workflows/schedule.yml` (lines 64-66):

```yaml
ENABLE_PUBLISH_YOUTUBE: "true"
ENABLE_PUBLISH_INSTAGRAM: "true"
ENABLE_PUBLISH_FACEBOOK: "true"
```

### Step 3: Commit and push

```bash
git add .
git commit -m "Enable social media posting with long-lived tokens"
git push origin main
```

### Step 4: Test in GitHub Actions

Go to **Actions** → **Run Bulletin Scheduler** → **Run workflow**

---

## ⏰ Token Renewal Schedule

| Platform | Token Type | Lifespan | Renewal Frequency |
|----------|-----------|----------|-------------------|
| Facebook (User) | Long-lived | 60 days | Every 60 days |
| Facebook (Page) | Page token | Never* | Never* |
| Instagram | Uses Facebook token | Same as Facebook | Same as Facebook |
| YouTube | Refresh token | 6+ months | Every 6 months |

*Page tokens don't expire as long as your app is active and you don't revoke permissions.

---

## 📅 Set Reminders

**Add to your calendar:**
- [ ] **Every 60 days:** Renew Facebook token (run `get_facebook_long_lived_token.py`)
- [ ] **Every 6 months:** Renew YouTube token (run `get_youtube_refresh_token.py`)

**Or use page tokens for Facebook/Instagram and only renew YouTube every 6 months!**

---

## 🐛 Troubleshooting

### "Token expired" error
→ Run the token generator script again

### "Invalid OAuth" error
→ Check that you granted all required permissions

### "Page token not working"
→ Make sure you're using the page ID, not the user ID

### YouTube "invalid_grant" error
→ Refresh token expired, run `get_youtube_refresh_token.py` again

---

## ✅ Success Checklist

- [ ] Ran `get_facebook_long_lived_token.py`
- [ ] Got 60-day token (or never-expiring page token)
- [ ] Added token to `.env`
- [ ] Ran `get_youtube_refresh_token.py`
- [ ] Got refresh token
- [ ] Added YouTube tokens to `.env`
- [ ] Tested locally with `python main_1.py`
- [ ] Added all tokens to GitHub Secrets
- [ ] Enabled platforms in workflow
- [ ] Tested in GitHub Actions
- [ ] Set calendar reminders for renewal

---

**You're now set up for automated posting with minimal manual intervention!** 🎉
