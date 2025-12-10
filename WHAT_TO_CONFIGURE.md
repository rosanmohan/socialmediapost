# 🔧 What You Need to Configure

## Summary: Personal Information Required

### ✅ MINIMUM REQUIRED (To Test the Agent)

1. **News API Key** (FREE)
   - Get from: https://newsapi.org/ (or https://gnews.io/)
   - Add to `.env` file: `NEWS_API_KEY=your_key`

2. **LLM API Key** (FREE - Choose ONE)
   - **Recommended: Groq** (fastest, free)
     - Get from: https://console.groq.com/
     - Add: `LLM_PROVIDER=groq` and `GROQ_API_KEY=your_key`
   - Or Hugging Face, Together AI, or OpenRouter (all free)

### ⚠️ OPTIONAL (For Auto-Posting)

3. **Instagram/Facebook Credentials** (if posting to these)
   - Facebook App ID & Secret
   - Access Token
   - Instagram Business Account ID
   - Facebook Page ID

4. **YouTube Credentials** (if posting to YouTube)
   - OAuth Client ID & Secret
   - Refresh Token

---

## 📍 Where to Add Your Information

**All configuration goes in the `.env` file**

1. Copy `env.example` to `.env`
2. Edit `.env` and add your keys
3. Save the file

**Location:** `C:\Users\rosan\OneDrive\Documents\SocialMediaPost\.env`

---

## 🎯 Quick Start (Minimum Config)

Create `.env` with just these 2 lines:

```env
NEWS_API_KEY=your_newsapi_key_here
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_key_here
```

This is enough to test the agent! It will generate videos but won't post them.

---

## 📚 Detailed Instructions

See `CONFIGURATION_GUIDE.md` for step-by-step setup of each API.

---

## 🔐 Security

- `.env` file is already in `.gitignore` (won't be committed)
- Keep your keys secret
- Don't share your `.env` file



