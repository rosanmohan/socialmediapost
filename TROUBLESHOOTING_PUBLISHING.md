# 🔧 Troubleshooting Guide: Videos Not Being Published

## Problem
GitHub Actions runs successfully but videos are not being posted to YouTube, Facebook, and Instagram.

## Root Causes & Solutions

### 1. **Publishing Toggles Not Enabled** ⚠️ MOST LIKELY CAUSE

**Issue**: The environment variables `ENABLE_PUBLISH_YOUTUBE`, `ENABLE_PUBLISH_INSTAGRAM`, and `ENABLE_PUBLISH_FACEBOOK` are set to `false` by default in `config.py`.

**Check**: Look at the GitHub Actions logs for the "Debug Configuration" step. You should see:
```
ENABLE_PUBLISH_YOUTUBE: true
ENABLE_PUBLISH_INSTAGRAM: true
ENABLE_PUBLISH_FACEBOOK: true
```

**If they show `false`**:
- The workflow is NOT running on the `main` branch
- Check which branch triggered the workflow in the logs
- The toggles are only set to `true` when `github.ref == 'refs/heads/main'`

**Solution**:
- Ensure you're pushing to the `main` branch, not `dev`
- Or manually trigger the workflow from the `main` branch in GitHub Actions UI

---

### 2. **Videos Not Being Generated**

**Check**: Look for these log messages in the GitHub Actions output:
- `"🎬 Starting video generation..."`
- `"✅ Video generated successfully"`
- `"Video saved to: output/videos/..."`

**If missing**:
- The pipeline might be exiting early due to no news found
- Check for: `"No unused news stories found"`
- Check for: `"Pipeline Skipped"`

**Solution**:
- Wait for the next scheduled run
- Check the database has news items: `python -c "from database import SessionLocal, NewsItem; db = SessionLocal(); print(f'News items: {db.query(NewsItem).count()}')"`

---

### 3. **API Credentials Missing or Invalid**

**Check the "Debug Configuration" step** for:
```
YOUTUBE_CLIENT_ID: ✅ SET
YOUTUBE_CLIENT_SECRET: ✅ SET
YOUTUBE_REFRESH_TOKEN: ✅ SET
FACEBOOK_ACCESS_TOKEN: ✅ SET
FACEBOOK_PAGE_ID: ✅ SET
INSTAGRAM_BUSINESS_ACCOUNT_ID: ✅ SET
```

**If any show `❌ NOT SET`**:
- Go to GitHub repository → Settings → Secrets and variables → Actions
- Verify all required secrets are configured:
  - `YOUTUBE_CLIENT_ID`
  - `YOUTUBE_CLIENT_SECRET`
  - `YOUTUBE_REFRESH_TOKEN`
  - `FACEBOOK_ACCESS_TOKEN`
  - `FACEBOOK_PAGE_ID`
  - `INSTAGRAM_BUSINESS_ACCOUNT_ID`

---

### 4. **YouTube OAuth Token Expired**

**Symptoms**:
- YouTube publishing shows "failed" status
- Error message contains "invalid_grant" or "Token has been expired or revoked"

**Solution**:
1. Run the YouTube authentication script locally:
   ```bash
   python scripts/youtube_auth.py
   ```
2. Follow the browser authentication flow
3. Copy the new `YOUTUBE_REFRESH_TOKEN`
4. Update the GitHub Secret with the new token

---

### 5. **Facebook/Instagram Token Expired**

**Symptoms**:
- Instagram/Facebook publishing shows "failed"
- Error contains "OAuthException" or "Invalid OAuth access token"

**Solution**:
1. Go to [Facebook Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Generate a new long-lived Page Access Token
3. Update `FACEBOOK_ACCESS_TOKEN` in GitHub Secrets

---

### 6. **Wrong Branch Running**

**Check**: In the workflow logs, look for:
```
Branch: refs/heads/main
```

**If it shows `refs/heads/dev` or another branch**:
- Publishing is intentionally disabled on non-main branches
- This is a safety feature to prevent accidental posts during development

**Solution**:
- Push your changes to the `main` branch
- Or merge your `dev` branch into `main`

---

## Quick Diagnostic Steps

### Step 1: Check the Artifacts
After a workflow run:
1. Go to GitHub Actions → Select the workflow run
2. Scroll down to "Artifacts"
3. Download `pipeline-outputs-XXXXX`
4. Check if `output/videos/` contains any `.mp4` files
   - **If YES**: Videos are being generated ✅
   - **If NO**: Video generation is failing ❌

### Step 2: Check PIPELINE_STATUS.md
In the artifacts, open `PIPELINE_STATUS.md`:
```markdown
# 📊 Pipeline Execution Status

- ✅ **Youtube**: SUCCESS
- ✅ **Instagram**: SUCCESS
- ✅ **Facebook**: SUCCESS
```

**If you see**:
- `⏭️ **Platform**: SKIPPED` → Publishing is disabled
- `❌ **Platform**: FAILED` → Check the error message below it

### Step 3: Run Debug Config Locally
```bash
python debug_config.py
```

This will show you exactly what values are being loaded.

---

## Manual Test Publishing

To test if publishing works at all:

### Test YouTube:
```python
from publishers import YouTubePublisher
pub = YouTubePublisher()
result = pub.publish(
    video_path="output/videos/your_video.mp4",
    title="Test Video",
    description="Testing upload",
    hashtags=["test"]
)
print(result)
```

### Test Instagram:
```python
from publishers import InstagramPublisher
pub = InstagramPublisher()
result = pub.publish(
    video_path="output/videos/your_video.mp4",
    caption="Test caption #test",
    hashtags=["test"]
)
print(result)
```

### Test Facebook:
```python
from publishers import FacebookPublisher
pub = FacebookPublisher()
result = pub.publish(
    video_path="output/videos/your_video.mp4",
    caption="Test caption #test",
    hashtags=["test"]
)
print(result)
```

---

## Expected Workflow Behavior

### On `main` branch:
1. ✅ Videos are generated
2. ✅ Videos are published to all enabled platforms
3. ✅ Status is logged to `PIPELINE_STATUS.md`

### On `dev` branch:
1. ✅ Videos are generated
2. ⏭️ Publishing is SKIPPED (safety feature)
3. ✅ Status shows "skipped" for all platforms

---

## Next Steps

1. **Push this updated workflow to GitHub**:
   ```bash
   git add .github/workflows/schedule.yml debug_config.py
   git commit -m "Add debugging for publishing issues"
   git push origin main
   ```

2. **Manually trigger the workflow**:
   - Go to GitHub Actions
   - Select "Run Social Media Agent"
   - Click "Run workflow"
   - Select `main` branch
   - Click "Run workflow"

3. **Check the logs**:
   - Look for the "Debug Configuration" step
   - Verify all toggles show `true`
   - Check if videos are being generated
   - Download artifacts to see the actual video files

4. **If still failing**:
   - Share the complete logs from the "Debug Configuration" step
   - Share the `PIPELINE_STATUS.md` content
   - Share any error messages from the "Execute Automated Pipeline" step
