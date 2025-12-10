# 🚀 START HERE - Quick Setup Guide

## ✅ What's Already Done

1. ✅ All Python packages installed
2. ✅ Database initialized
3. ✅ Project structure created
4. ✅ `.env` file created (needs your API keys)

## 📝 What YOU Need to Do (5 minutes)

### Step 1: Get FREE API Keys

#### A. News API (REQUIRED)
1. Go to: https://newsapi.org/register
2. Sign up (free - 100 requests/day)
3. Copy your API key

#### B. LLM API (REQUIRED - Choose ONE)
**Recommended: Groq (Fastest & Free)**
1. Go to: https://console.groq.com/
2. Sign up (free)
3. Go to API Keys
4. Create new key
5. Copy the key

**OR use other free options:**
- Hugging Face: https://huggingface.co/join
- Together AI: https://api.together.xyz/
- OpenRouter: https://openrouter.ai/

### Step 2: Edit `.env` File

Open `.env` file in this folder and add your keys:

```env
# News API (REQUIRED)
NEWS_API_KEY=paste_your_newsapi_key_here

# LLM (REQUIRED - use Groq for free)
LLM_PROVIDER=groq
GROQ_API_KEY=paste_your_groq_key_here
```

**That's it!** You can test the agent now.

### Step 3: Test the Agent

```bash
python quick_start.py
```

This will test all components.

### Step 4: Run a Test Post

```bash
python main.py --mode run --slot test
```

This will:
- Fetch news
- Generate content
- Create video
- (Won't post without social media credentials)

### Step 5: Start 24/7 Scheduler (When Ready)

```bash
python main.py --mode schedule
```

---

## 📍 File Location

Your `.env` file is here:
```
C:\Users\rosan\OneDrive\Documents\SocialMediaPost\.env
```

---

## 🔐 Social Media APIs (OPTIONAL - For Auto-Posting)

You can add these later when you want to auto-post:

- **Instagram/Facebook**: See `CONFIGURATION_GUIDE.md`
- **YouTube**: See `CONFIGURATION_GUIDE.md`

**Note:** The agent will work and generate videos WITHOUT these. It just won't auto-post.

---

## 📚 More Help

- `CONFIGURATION_GUIDE.md` - Detailed API setup
- `WHAT_TO_CONFIGURE.md` - Quick reference
- `README.md` - Full documentation

---

## ⚡ Quick Commands

```bash
# Test components
python quick_start.py

# Run once (test)
python main.py --mode run --slot test

# Start 24/7 scheduler
python main.py --mode schedule
```

---

**You're ready! Just add your API keys to `.env` and you're good to go! 🎉**



