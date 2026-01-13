# 🤖 Social Media Posting Agent

An automated 24/7 AI Agent that finds trending news, generates engaging 9:16 vertical videos (Viral & Bulletin styles), and auto-posts to **Instagram Reels**, **YouTube Shorts**, and **Facebook**.

---

## ✨ Features

- **24/7 Automation**: Runs on a schedule via GitHub Actions (or locally).
- **Multi-Pipeline Support**:
  - **Viral Stories**: Single high-impact niche stories (Cricket, Movies, India News).
  - **Bulletin News**: Top 5 breaking news summary (Daily Recap).
- **AI-Powered**: Uses LLM (Groq/OpenAI) for scripts and Edge-TTS for voiceovers.
- **Smart Scheduling**: 
  - **GitHub Actions**: Runs 3x daily (8 AM, 1 PM, 6 PM IST).
  - **Local**: Python schedulers for continuous operation.
- **Robust Publishing**: Handles tokens, retries, and fallback to email alerts.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.10+**
- **FFmpeg**: Must be installed and in your system PATH.
  - Windows: [Download FFmpeg](https://ffmpeg.org/download.html)
  - Linux: `sudo apt install ffmpeg`
  - Mac: `brew install ffmpeg`

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/rosanmohan/socialmediapost.git
cd socialmediapost

# Create Virtual Environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install Dependencies
pip install -r requirements.txt
```

### 3. Configuration (.env)
Create a `.env` file in the root directory and add the following keys:

```ini
# --- CORE CONFIG ---
TIMEZONE=Asia/Kolkata
LOG_LEVEL=INFO

# --- NEWS APIs (At least one required) ---
NEWS_API_KEY=your_newsapi_key_here
GNEWS_API_KEY=your_gnews_key_here

# --- LLM (AI Script Generation) ---
# We recommend Groq for speed/cost, or OpenAI for quality.
GROQ_API_KEY=your_groq_key
# OPENAI_API_KEY=your_openai_key

# --- GOOGLE / YOUTUBE ---
YOUTUBE_CLIENT_ID=...
YOUTUBE_CLIENT_SECRET=...
YOUTUBE_REFRESH_TOKEN=...
# Google Drive (for Assets)
DRIVE_AUDIO_FOLDER_ID=...
DRIVE_BACKGROUNDS_FOLDER_ID=...

# --- META (INSTAGRAM & FACEBOOK) ---
FACEBOOK_ACCESS_TOKEN=...
FACEBOOK_PAGE_ID=...
INSTAGRAM_BUSINESS_ACCOUNT_ID=...

# --- PUBLISHING TOGGLES (Local) ---
ENABLE_PUBLISH_YOUTUBE=true
ENABLE_PUBLISH_INSTAGRAM=true
ENABLE_PUBLISH_FACEBOOK=true
```

---

## 🛠️ Usage Commands (Run Locally)

### 1. Run "Viral" Single-Story Videos
These generate a generic "Viral" style video or focus on a specific niche.

```bash
# 🏏 Cricket News
python pipeline_viral.py --category cricket

# 🎬 Bollywood/Movies
python pipeline_viral.py --category movies

# 🇮🇳 India National News
python pipeline_viral.py --category india

# 🌍 General Trending
python pipeline_viral.py --category general
```

### 2. Run "Bulletin" Top 5 News
Generates a "Top 5 Breaking News" list video (standard daily update).

```bash
python main.py
```

### 3. Run Schedulers (Loop Mode)
Keep your computer running to auto-post at defined times.

```bash
# Schedule Viral Videos (Movies, Cricket, etc.)
python scheduler_viral.py

# Schedule Bulletin Videos (Top 5 list)
python scheduler_bulletin.py
```

---

## ☁️ GitHub Actions Automation

The project is configured to run automatically in the cloud.

### 📅 Schedule
The workflow (`.github/workflows/schedule.yml`) is set to run **3 times daily**:
*   **08:00 AM IST**
*   **01:00 PM IST**
*   **06:00 PM IST**

### 👆 Manual Trigger
1.  Go to the **Actions** tab in GitHub.
2.  Select **Run Social Media Agent**.
3.  Click **Run workflow**.
    *   *Note: This will immediately execute the Bulletin Pipeline (`main.py`) regardless of the time.*

### 🔐 GitHub Secrets
Ensure these secrets are set in your Repo Settings > Secrets and Variables > Actions:
*   `OPENAI_API_KEY` / `GROQ_API_KEY`
*   `NEWS_API_KEY` / `GNEWS_API_KEY`
*   `YOUTUBE_...` (Client ID, Secret, Refresh Token)
*   `FACEBOOK_...` (Access Token, Page ID, Instagram ID)
*   `EMAIL_TO` (For failure alerts)

---

## 🚑 Troubleshooting

### "No module named 'moviepy.editor'"
We pinned **moviepy==1.0.3** in `requirements.txt` to fix this. Run:
```bash
pip install moviepy==1.0.3
```

### Video Not Uploading?
*   Check `logs/` folder.
*   Verify `ENABLE_PUBLISH_*` flags are set to `true` in `.env`.
*   Check if your Token (Facebook/Google) has expired.

### Database Errors
If you see "column does not exist", run the migration script:
```bash
python migrate_database.py
```

---
**Maintained by:** Rosan Mohan
