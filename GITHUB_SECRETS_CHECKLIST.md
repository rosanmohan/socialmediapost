# GitHub Secrets Setup - Complete Checklist

## 🎯 Where to Add Secrets

Go to: https://github.com/rosanmohan/socialmediapost/settings/secrets/actions

Click **"New repository secret"** for each one below.

---

## 🔑 Required Secrets for All Platforms

### YouTube (3 secrets)

| Secret Name | Value | Where to Get |
|-------------|-------|--------------|
| `YOUTUBE_CLIENT_ID` | `your_client_id_here` | From `youtube_credentials_backup.txt` |
| `YOUTUBE_CLIENT_SECRET` | `your_client_secret_here` | From `youtube_credentials_backup.txt` |
| `YOUTUBE_REFRESH_TOKEN` | `your_refresh_token_here` | From `youtube_credentials_backup.txt` |

### Facebook (2 secrets)

| Secret Name | Value | Where to Get |
|-------------|-------|--------------|
| `FACEBOOK_ACCESS_TOKEN` | `your_long_lived_token_here` | From `facebook_token_20251220_231326.txt` |
| `FACEBOOK_PAGE_ID` | `your_page_id_here` | From your `.env` file |

### Instagram (1 secret)

| Secret Name | Value | Where to Get |
|-------------|-------|--------------|
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | Your Instagram Business Account ID | From Facebook Graph API Explorer |

---

## 📝 How to Get Instagram Business Account ID

If you don't have it yet:

1. Go to: https://developers.facebook.com/tools/explorer/
2. Select your app
3. Use your Facebook access token
4. Query: `me/accounts`
5. Find your page, copy the `id`
6. Query: `{page-id}?fields=instagram_business_account`
7. Copy the `instagram_business_account` → `id`

---

## ✅ Complete Checklist

Add these 6 secrets to GitHub:

- [ ] `YOUTUBE_CLIENT_ID`
- [ ] `YOUTUBE_CLIENT_SECRET`
- [ ] `YOUTUBE_REFRESH_TOKEN`
- [ ] `FACEBOOK_ACCESS_TOKEN`
- [ ] `FACEBOOK_PAGE_ID`
- [ ] `INSTAGRAM_BUSINESS_ACCOUNT_ID`

---

## 🚀 After Adding Secrets

### Step 1: Enable platforms in workflow

Edit `.github/workflows/schedule.yml` (lines 64-66):

```yaml
ENABLE_PUBLISH_YOUTUBE: "true"
ENABLE_PUBLISH_INSTAGRAM: "true"
ENABLE_PUBLISH_FACEBOOK: "true"
```

### Step 2: Commit and push

```bash
git add .github/workflows/schedule.yml
git commit -m "Enable all social media platforms"
git push origin main
```

### Step 3: Test in GitHub Actions

1. Go to: https://github.com/rosanmohan/socialmediapost/actions
2. Click **"Run Bulletin Scheduler"**
3. Click **"Run workflow"**
4. Wait for it to complete

**Expected result:**
```
✅ Video generated
✅ Posted to YouTube
✅ Posted to Instagram
✅ Posted to Facebook
✅ Pipeline completed successfully
```

---

## 📊 Summary

| Platform | Secrets Needed | Token Lifespan |
|----------|---------------|----------------|
| YouTube | 3 secrets | 6+ months (auto-refresh) |
| Facebook | 2 secrets | Never expires (page token) |
| Instagram | 1 secret | Never expires (uses Facebook token) |

**Total: 6 GitHub Secrets**

**Manual renewal needed:**
- YouTube: Every 6 months (2 minutes)
- Facebook: Never
- Instagram: Never

---

### Email Notifications (Failure Alerts - 5 secrets)

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `MAIL_SERVER` | `smtp.gmail.com` | Your SMTP mail server |
| `MAIL_PORT` | `465` | Usually 465 (SSL) or 587 (TLS) |
| `MAIL_USERNAME` | `your.email@gmail.com` | Your full email address |
| `MAIL_PASSWORD` | `your_app_password` | For Gmail: Use an "App Password" |
| `ALERT_RECIPIENT` | `your.email@gmail.com` | Where to send the alerts |

---

## ✅ Complete Checklist

Add these secrets to GitHub to enable everything:

- [ ] `YOUTUBE_CLIENT_ID`
- [ ] `YOUTUBE_CLIENT_SECRET`
- [ ] `YOUTUBE_REFRESH_TOKEN`
- [ ] `FACEBOOK_ACCESS_TOKEN`
- [ ] `FACEBOOK_PAGE_ID`
- [ ] `INSTAGRAM_BUSINESS_ACCOUNT_ID`
- [ ] `MAIL_SERVER`
- [ ] `MAIL_PORT`
- [ ] `MAIL_USERNAME`
- [ ] `MAIL_PASSWORD`
- [ ] `ALERT_RECIPIENT`

---

## 🎯 Quick Copy-Paste Values

Just copy these values when adding secrets to GitHub!
