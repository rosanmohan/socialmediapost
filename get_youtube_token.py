"""
Script to get YouTube OAuth refresh token
Run this once to get your YouTube credentials
"""
from google_auth_oauthlib.flow import InstalledAppFlow
import json
import os

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
CLIENT_SECRETS_FILE = "client_secret.json"

if not os.path.exists(CLIENT_SECRETS_FILE):
    print("=" * 60)
    print("ERROR: client_secret.json not found!")
    print("=" * 60)
    print("\nSteps to get client_secret.json:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a project")
    print("3. Enable 'YouTube Data API v3'")
    print("4. Create OAuth 2.0 credentials (Desktop app)")
    print("5. Download the JSON file")
    print("6. Save it as 'client_secret.json' in this folder")
    print("\nThen run this script again.")
    exit(1)

print("=" * 60)
print("YouTube OAuth Token Generator")
print("=" * 60)
print("\nA browser window will open.")
print("Please sign in with your Google account and grant permissions.")
print()

flow = InstalledAppFlow.from_client_secrets_file(
    CLIENT_SECRETS_FILE, SCOPES)
creds = flow.run_local_server(port=0)

print("\n" + "=" * 60)
print("✅ SUCCESS! Add these to your .env file:")
print("=" * 60)
print()
print(f"YOUTUBE_CLIENT_ID={creds.client_id}")
print(f"YOUTUBE_CLIENT_SECRET={creds.client_secret}")
print(f"YOUTUBE_REFRESH_TOKEN={creds.refresh_token}")
print()
print("=" * 60)
print("Copy the above lines and add them to your .env file")
print("=" * 60)



