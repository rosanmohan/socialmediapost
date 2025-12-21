# 🤖 THE MASTER AUTOMATION GUIDE
## Social Media Posting Agent: End-to-End Manual

This guide covers everything you need to keep your social media automation running forever with minimal effort.

---

## 🚀 1. How to Start the App (Local)

To run a manual test on your computer:

```bash
# 1. Ensure you are on the main branch
git checkout main

# 2. Update your .env (Make sure all keys are there)
python main_1.py
```

---

## 🚀 2. How to Start the App (GitHub Actions)

The app is already scheduled to run every few hours. To trigger it manually:
1. Go to your GitHub Repository.
2. Click the **"Actions"** tab.
3. Click **"Run Bulletin Scheduler"** on the left.
4. Click **"Run workflow"** -> **"Run workflow"**.

---

## 🔑 3. The "Infinite Automation" Strategy (Token Renewal)

Most API keys (OpenAI, NewsAPI, Cloudinary) never expire. Only **YouTube** and **Facebook/Instagram** tokens expire for security. 

Here is how to fix them in seconds when they do:

### 📺 YouTube (Renew Every 6 Months)
**Symptom:** Logs show `YouTube OAuth token expired` or `invalid_grant`.

1. **Run the auto-generator:**
   ```bash
   python get_youtube_refresh_token.py
   ```
2. **Follow the browser login.** The script will automatically update your `.env`.
3. **Update GitHub Secrets:** Copy the new `YOUTUBE_REFRESH_TOKEN` from the script output to your GitHub Secrets.

### 👥 Facebook & Instagram (Renew Every 60 Days / Never)
**Symptom:** Logs show `Invalid OAuth access token`.

1. **Run the auto-generator:**
   ```bash
   python get_facebook_long_lived_token.py
   ```
2. **Choose "Page Token" (Recommended):** If you choose "y" for a Page Access Token, **it will never expire** as long as your app is active!
3. **Update GitHub Secrets:** Copy the new `FACEBOOK_ACCESS_TOKEN` to your GitHub Secrets.

---

## 📋 4. Master Credentials Checklist

Ensure these **9 Secrets** are always correct in GitHub Settings:

| Name | Platform | Lifespan |
|------|----------|----------|
| `OPENAI_API_KEY` | Content | Permanent |
| `NEWS_API_KEY` | Data | Permanent |
| `DATABASE_URL` | Storage | Permanent |
| `YOUTUBE_REFRESH_TOKEN` | YouTube | 6 Months |
| `FACEBOOK_ACCESS_TOKEN` | FB/Insta| 60 Days (or Never) |
| `FACEBOOK_PAGE_ID` | Facebook | Permanent |
| `INSTAGRAM_BUSINESS_ID` | Instagram| Permanent |
| `CLOUDINARY_CLOUD_NAME` | Hosting | Permanent |
| `CLOUDINARY_API_KEY` | Hosting | Permanent |

---

## 🛠️ 5. Troubleshooting Common Issues

### ❌ Error: "Media processing has not been completed"
*   **Meaning:** Instagram is still "thinking" about your video.
*   **Solution:** Do nothing. Our code now has a **retry loop** that waits up to 3 minutes for Instagram to finish.

### ❌ Error: "Invalid Header format"
*   **Meaning:** Old binary upload error.
*   **Solution:** Fixed! We now use the **Cloudinary method**. Make sure your Cloudinary keys are correct in `.env`.

### ❌ Error: "requests is not defined"
*   **Meaning:** Code bug.
*   **Solution:** Fixed in the latest update on `main`.

---

## 🔄 6. Syncing Changes
Whenever you make a change locally and want it to go "live" on the scheduler:

```bash
git add .
git commit -m "Update configuration"
git push origin main
```

---

## 🎯 Summary of Maintenance
- **OpenAI/NewsAPI:** Set and forget.
- **Facebook:** Use the `get_facebook_long_lived_token.py` to get a **Page Token**. This is the "Gold" token that never expires.
- **YouTube:** Just run `get_youtube_refresh_token.py` twice a year.
- **Instagram:** Keep your Cloudinary free account active.

**You are now a Social Media Automation Master!** 🏆
