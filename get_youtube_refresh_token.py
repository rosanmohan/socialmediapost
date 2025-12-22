"""
YouTube OAuth Refresh Token Generator
Run this script locally to get a fresh refresh token that won't expire.

Steps:
1. Make sure client_secret.json exists in this directory
2. Run: python get_youtube_refresh_token.py
3. A browser will open - login to your YouTube account
4. Copy the refresh token from the output
5. Update your .env file with the new YOUTUBE_REFRESH_TOKEN
6. Update GitHub Secrets with the new token
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes required for YouTube upload and Google Drive access
SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/drive.readonly'
]

def get_refresh_token():
    """Get a fresh YouTube OAuth refresh token"""
    
    # Check if client_secret.json exists
    if not os.path.exists('client_secret.json'):
        print("❌ ERROR: client_secret.json not found!")
        print("\nTo get this file:")
        print("1. Go to: https://console.cloud.google.com/")
        print("2. Select your project (or create one)")
        print("3. Go to 'APIs & Services' > 'Credentials'")
        print("4. Click 'Create Credentials' > 'OAuth 2.0 Client ID'")
        print("5. Choose 'Desktop app' as application type")
        print("6. Download the JSON file and save as 'client_secret.json'")
        return None
    
    print("🔐 Starting YouTube OAuth flow...")
    print("📱 A browser window will open. Please login to your YouTube account.\n")
    
    try:
        # Run the OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json',
            scopes=SCOPES
        )
        
        # This will open a browser for user authentication
        creds = flow.run_local_server(
            port=8080,
            prompt='consent',
            access_type='offline'
        )
        
        print("\n✅ Authentication successful!")
        print("\n" + "="*60)
        print("YOUR YOUTUBE CREDENTIALS")
        print("="*60)
        
        # Extract credentials from client_secret.json
        with open('client_secret.json', 'r') as f:
            client_data = json.load(f)
            if 'installed' in client_data:
                client_info = client_data['installed']
            elif 'web' in client_data:
                client_info = client_data['web']
            else:
                client_info = {}
        
        client_id = client_info.get('client_id', 'NOT_FOUND')
        client_secret = client_info.get('client_secret', 'NOT_FOUND')
        
        print(f"\nYOUTUBE_CLIENT_ID={client_id}")
        print(f"YOUTUBE_CLIENT_SECRET={client_secret}")
        print(f"YOUTUBE_REFRESH_TOKEN={creds.refresh_token}")
        
        print("\n" + "="*60)
        print("NEXT STEPS:")
        print("="*60)
        print("\n1. LOCAL SETUP (.env file):")
        print("   Copy the above 3 lines to your .env file")
        
        print("\n2. GITHUB SECRETS:")
        print("   a. Go to: https://github.com/rosanmohan/socialmediapost/settings/secrets/actions")
        print("   b. Update these 3 secrets:")
        print("      - YOUTUBE_CLIENT_ID")
        print("      - YOUTUBE_CLIENT_SECRET")
        print("      - YOUTUBE_REFRESH_TOKEN")
        
        print("\n3. IMPORTANT:")
        print("   ⚠️  This refresh token will NOT expire as long as you use it regularly")
        print("   ⚠️  Keep it secret - don't share it publicly")
        print("   ⚠️  If you revoke access in Google, you'll need to regenerate it")
        
        print("\n✅ Done! Your YouTube uploads should work now.\n")
        
        return {
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': creds.refresh_token
        }
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure client_secret.json is valid")
        print("2. Check that you enabled YouTube Data API v3 in Google Cloud Console")
        print("3. Make sure the OAuth consent screen is configured")
        return None

if __name__ == "__main__":
    print("\n" + "="*60)
    print("YOUTUBE REFRESH TOKEN GENERATOR")
    print("="*60 + "\n")
    
    result = get_refresh_token()
    
    if result:
        # Optionally save to a file for backup
        with open('youtube_credentials_backup.txt', 'w') as f:
            f.write(f"YOUTUBE_CLIENT_ID={result['client_id']}\n")
            f.write(f"YOUTUBE_CLIENT_SECRET={result['client_secret']}\n")
            f.write(f"YOUTUBE_REFRESH_TOKEN={result['refresh_token']}\n")
        print("💾 Credentials also saved to: youtube_credentials_backup.txt")
        print("   (You can delete this file after updating .env and GitHub Secrets)\n")
