# How to Enable/Disable Social Media Publishing

This guide shows you exactly where to change settings to enable or disable YouTube, Instagram, or Facebook publishing.

---

## 🎯 Quick Answer

**For GitHub Actions (automated runs):**
Edit `.github/workflows/schedule.yml` lines 64-66

**For local testing:**
Edit your `.env` file (not tracked in git)

---

## 📝 Detailed Instructions

### Option 1: GitHub Actions (Production/Automated Runs)

**File:** `.github/workflows/schedule.yml`

**Location:** Lines 64-66

```yaml
# Publishing Toggles (Disable until credentials are configured)
ENABLE_PUBLISH_YOUTUBE: "false"      # ← Change to "true" to enable YouTube
ENABLE_PUBLISH_INSTAGRAM: "false"   # ← Change to "true" to enable Instagram
ENABLE_PUBLISH_FACEBOOK: "false"    # ← Change to "true" to enable Facebook
```

**Steps:**
1. Open `.github/workflows/schedule.yml`
2. Find the "Publishing Toggles" section (around line 64)
3. Change `"false"` to `"true"` for the platform you want to enable
4. Commit and push the changes
5. Make sure you have the credentials set in GitHub Secrets (see below)

**Example - Enable only YouTube:**
```yaml
ENABLE_PUBLISH_YOUTUBE: "true"       # ✅ Enabled
ENABLE_PUBLISH_INSTAGRAM: "false"   # ❌ Disabled
ENABLE_PUBLISH_FACEBOOK: "false"    # ❌ Disabled
```

---

### Option 2: Local Testing (.env file)

**File:** `.env` (in your project root)

**Add these lines:**
```bash
# Publishing Toggles
ENABLE_PUBLISH_YOUTUBE=false      # Change to true to enable YouTube
ENABLE_PUBLISH_INSTAGRAM=false   # Change to true to enable Instagram
ENABLE_PUBLISH_FACEBOOK=false    # Change to true to enable Facebook
```

**Steps:**
1. Open your `.env` file
2. Add or modify the `ENABLE_PUBLISH_*` variables
3. Set to `true` or `false` (no quotes needed in .env)
4. Save the file
5. Run `python main_1.py` locally

**Example - Enable Instagram and Facebook only:**
```bash
ENABLE_PUBLISH_YOUTUBE=false       # ❌ Disabled
ENABLE_PUBLISH_INSTAGRAM=true     # ✅ Enabled
ENABLE_PUBLISH_FACEBOOK=true      # ✅ Enabled
```

---

## 🔑 Required Credentials

Before enabling a platform, make sure you have the credentials configured:

### YouTube
**GitHub Secrets needed:**
- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`
- `YOUTUBE_REFRESH_TOKEN`

**How to get them:**
Run `python get_youtube_refresh_token.py` locally

### Instagram
**GitHub Secrets needed:**
- `FACEBOOK_ACCESS_TOKEN`
- `INSTAGRAM_BUSINESS_ACCOUNT_ID`

**How to get them:**
See `setup_guide.md` for Instagram setup instructions

### Facebook
**GitHub Secrets needed:**
- `FACEBOOK_ACCESS_TOKEN`
- `FACEBOOK_PAGE_ID`

**How to get them:**
See `setup_guide.md` for Facebook setup instructions

---

## 🚀 Quick Examples

### Scenario 1: "I want to test locally without publishing"
**File:** `.env`
```bash
ENABLE_PUBLISH_YOUTUBE=false
ENABLE_PUBLISH_INSTAGRAM=false
ENABLE_PUBLISH_FACEBOOK=false
```

### Scenario 2: "I want GitHub Actions to publish only to YouTube"
**File:** `.github/workflows/schedule.yml`
```yaml
ENABLE_PUBLISH_YOUTUBE: "true"
ENABLE_PUBLISH_INSTAGRAM: "false"
ENABLE_PUBLISH_FACEBOOK: "false"
```
**Also needed:** YouTube credentials in GitHub Secrets

### Scenario 3: "I want to publish to all platforms"
**File:** `.github/workflows/schedule.yml`
```yaml
ENABLE_PUBLISH_YOUTUBE: "true"
ENABLE_PUBLISH_INSTAGRAM: "true"
ENABLE_PUBLISH_FACEBOOK: "true"
```
**Also needed:** All platform credentials in GitHub Secrets

---

## ⚠️ Important Notes

1. **GitHub Actions vs Local:**
   - `.github/workflows/schedule.yml` controls GitHub Actions (automated runs)
   - `.env` controls local runs (when you run `python main_1.py`)
   - They are independent - changing one doesn't affect the other

2. **Credentials Required:**
   - Setting `ENABLE_PUBLISH_*` to `true` without credentials will cause failures
   - Always set up credentials BEFORE enabling a platform

3. **Default Behavior:**
   - If you don't set these variables, the default is `true` (enabled)
   - This is why we explicitly set them to `"false"` in the workflow

4. **Testing:**
   - Always test locally first with `.env` before enabling in GitHub Actions
   - Use `ENABLE_PUBLISH_*=false` to generate videos without uploading

---

## 📍 File Locations Summary

| What | Where | Format |
|------|-------|--------|
| GitHub Actions | `.github/workflows/schedule.yml` line 64-66 | `ENABLE_PUBLISH_YOUTUBE: "true"` |
| Local Testing | `.env` (root directory) | `ENABLE_PUBLISH_YOUTUBE=true` |
| Config Default | `config.py` line 60-62 | (Don't edit this) |

---

## 🎬 Current Status

As of now, **all platforms are disabled** in GitHub Actions:
- YouTube: ❌ Disabled
- Instagram: ❌ Disabled  
- Facebook: ❌ Disabled

This means the workflow will:
- ✅ Generate videos
- ✅ Save to database
- ⏭️ Skip all uploads
- ✅ Report success

To enable a platform, follow the instructions above!
