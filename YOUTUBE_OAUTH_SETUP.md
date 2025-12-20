# YouTube OAuth Setup Guide
## How to Get a Refresh Token That Never Expires

### Problem
Your YouTube uploads are failing with "token expired" errors. This happens because:
- Access tokens expire after 1 hour
- Refresh tokens can expire if not used regularly or if revoked
- You need a fresh, valid refresh token

### Solution Overview
We'll generate a new refresh token that will:
- ✅ Never expire (as long as you use it regularly - which your bot does)
- ✅ Automatically refresh access tokens every hour
- ✅ Work seamlessly in GitHub Actions

---

## Step-by-Step Instructions

### Step 1: Verify Your Google Cloud Project Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create a new one)
3. Enable the **YouTube Data API v3**:
   - Go to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"

4. Configure OAuth Consent Screen:
   - Go to "APIs & Services" > "OAuth consent screen"
   - Choose "External" (unless you have a Google Workspace)
   - Fill in:
     - App name: "Social Media Bot"
     - User support email: Your email
     - Developer contact: Your email
   - Click "Save and Continue"
   - Skip "Scopes" (click "Save and Continue")
   - Add yourself as a test user (your email)
   - Click "Save and Continue"

5. Create OAuth 2.0 Credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client ID"
   - Application type: **Desktop app**
   - Name: "YouTube Upload Bot"
   - Click "Create"
   - Click "Download JSON"
   - Save the file as `client_secret.json` in your project folder

### Step 2: Generate the Refresh Token

1. Make sure `client_secret.json` is in your project folder
2. Open a terminal in your project directory
3. Run the token generator:
   ```bash
   python get_youtube_refresh_token.py
   ```

4. A browser window will open automatically
5. Login with your YouTube account
6. Click "Allow" to grant permissions
7. The script will display your credentials

### Step 3: Update Your Local Environment

1. Open your `.env` file
2. Update these three lines with the values from the script output:
   ```
   YOUTUBE_CLIENT_ID=your_actual_client_id
   YOUTUBE_CLIENT_SECRET=your_actual_client_secret
   YOUTUBE_REFRESH_TOKEN=your_actual_refresh_token
   ```
3. Save the file

### Step 4: Update GitHub Secrets

1. Go to your GitHub repository: https://github.com/rosanmohan/socialmediapost
2. Click "Settings" > "Secrets and variables" > "Actions"
3. Update or create these three secrets:
   - **YOUTUBE_CLIENT_ID**: (from script output)
   - **YOUTUBE_CLIENT_SECRET**: (from script output)
   - **YOUTUBE_REFRESH_TOKEN**: (from script output)

### Step 5: Test Locally (Optional)

```bash
python main_1.py
```

If it works locally, it will work in GitHub Actions!

---

## Important Notes

### ✅ Your Refresh Token Will NOT Expire If:
- You use it regularly (your bot runs 5 times daily, so ✅)
- You don't manually revoke access in Google Account settings
- You don't delete the OAuth app in Google Cloud Console

### ⚠️ Your Refresh Token WILL Expire If:
- You don't use it for 6 months (won't happen with your bot)
- You manually revoke access
- You delete/recreate the OAuth credentials

### 🔒 Security Best Practices:
- ✅ `client_secret.json` is in `.gitignore` (never commit it)
- ✅ Refresh token is in `.env` (never commit it)
- ✅ GitHub Secrets are encrypted
- ❌ Never share these credentials publicly

---

## Troubleshooting

### Error: "client_secret.json not found"
- Make sure you downloaded the OAuth credentials from Google Cloud Console
- Save it as `client_secret.json` in your project root folder

### Error: "invalid_grant" or "Token has been expired or revoked"
- Your old refresh token is invalid
- Follow this guide from Step 1 to generate a new one

### Error: "Access blocked: This app's request is invalid"
- Make sure you added yourself as a test user in OAuth consent screen
- Make sure YouTube Data API v3 is enabled

### Browser doesn't open automatically
- The script will print a URL
- Copy and paste it into your browser manually

### Still not working?
- Double-check all three values (CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN) are correct
- Make sure there are no extra spaces or quotes
- Verify the values in both `.env` AND GitHub Secrets match

---

## How It Works (Technical Details)

1. **Access Token** (expires in 1 hour):
   - Used for actual API calls
   - Your code automatically requests a new one when needed

2. **Refresh Token** (never expires if used):
   - Used to get new access tokens
   - Stored in your `.env` and GitHub Secrets
   - Your code uses it automatically via `creds.refresh(Request())`

3. **Client ID & Secret**:
   - Identifies your application to Google
   - Required to use the refresh token

Your `publishers.py` already handles all of this automatically. You just need valid credentials!
