# Deploying to the Cloud (Free)

To run this 24/7 without your laptop, we will use **GitHub Actions** (to run the code) and **Neon.tech** (free Database to remember what was posted).

## Prerequisites
1.  A GitHub Account.
2.  A [Neon.tech](https://neon.tech) Account (Free).

## Step 1: Push to GitHub
1.  Create a new Repository on GitHub (Private).
2.  Upload all these files to it (or push via Git).

## Step 2: Set up Free Database
1.  Log in to [Neon.tech](https://neon.tech).
2.  Create a Project.
3.  Copy the **Connection String** (it looks like `postgres://user:pass@ep-xyz.aws.neon.tech/neondb...`).

## Step 3: Configure GitHub Secrets
Go to your GitHub Repository -> **Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**.

Add the following Secrets (copy values from your `.env` file):

| Secret Name | Value |
|-------------|-------|
| `DATABASE_URL` | **(The Neon Connection String from Step 2)** |
| `OPENAI_API_KEY` | (Your OpenAI Key) |
| `NEWS_API_KEY` | (Your News API Key) |
| `YOUTUBE_CLIENT_ID` | (Your Client ID) |
| `YOUTUBE_CLIENT_SECRET` | (Your Client Secret) |
| `YOUTUBE_REFRESH_TOKEN` | (Your Refresh Token) |

*(Add any other keys you use, like `FACEBOOK_ACCESS_TOKEN` if posting there)*

## Step 4: That's it!
The workflow file `.github/workflows/schedule.yml` is already set up to run at:
- 7:00 AM IST
- 11:00 AM IST
- 3:00 PM IST
- 7:00 PM IST
- 11:00 PM IST

You can also manually run it by going to the **Actions** tab in GitHub and clicking "Run workflow".
