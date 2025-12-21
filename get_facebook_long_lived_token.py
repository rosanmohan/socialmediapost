"""
Facebook Long-Lived Token Generator
Exchanges short-lived Facebook tokens (1-2 hours) for long-lived tokens (60 days)
"""
import requests
import os
from datetime import datetime, timedelta
from loguru import logger

def exchange_for_long_lived_token(short_lived_token: str, app_id: str, app_secret: str) -> dict:
    """
    Exchange a short-lived Facebook token for a long-lived token (60 days)
    
    Args:
        short_lived_token: The short-lived access token from Facebook
        app_id: Your Facebook App ID
        app_secret: Your Facebook App Secret
        
    Returns:
        dict with 'access_token' and 'expires_in' (seconds)
    """
    url = "https://graph.facebook.com/v18.0/oauth/access_token"
    
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_lived_token
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if "access_token" in data:
            expires_in = data.get("expires_in", 5184000)  # Default 60 days
            expiry_date = datetime.now() + timedelta(seconds=expires_in)
            
            logger.info(f"✅ Successfully generated long-lived token!")
            logger.info(f"📅 Token expires in: {expires_in / 86400:.0f} days")
            logger.info(f"📅 Expiry date: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}")
            
            return {
                "access_token": data["access_token"],
                "expires_in": expires_in,
                "expiry_date": expiry_date.isoformat()
            }
        else:
            logger.error(f"❌ Failed to get long-lived token: {data}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error exchanging token: {e}")
        return None


def get_page_access_token(user_access_token: str, page_id: str) -> dict:
    """
    Get a page access token that never expires (as long as the app is active)
    
    Args:
        user_access_token: Long-lived user access token
        page_id: Facebook Page ID
        
    Returns:
        dict with page access token info
    """
    url = f"https://graph.facebook.com/v18.0/{page_id}"
    
    params = {
        "fields": "access_token",
        "access_token": user_access_token
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if "access_token" in data:
            logger.info(f"✅ Successfully generated page access token!")
            logger.info(f"📝 This token doesn't expire (as long as your app is active)")
            
            return {
                "access_token": data["access_token"],
                "expires": "never (while app is active)"
            }
        else:
            logger.error(f"❌ Failed to get page token: {data}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error getting page token: {e}")
        return None


def main():
    """Interactive script to generate long-lived tokens"""
    print("\n" + "="*70)
    print("🔑 Facebook Long-Lived Token Generator")
    print("="*70)
    print("\nThis script will exchange your short-lived token for a long-lived token")
    print("that lasts 60 days instead of 1-2 hours.\n")
    
    # Get inputs
    print("📝 Step 1: Get your short-lived token")
    print("   Go to: https://developers.facebook.com/tools/explorer/")
    print("   Generate a token with these permissions:")
    print("   - pages_manage_posts")
    print("   - pages_read_engagement")
    print("   - instagram_basic")
    print("   - instagram_content_publish")
    print()
    
    short_lived_token = input("Enter your short-lived token: ").strip()
    
    print("\n📝 Step 2: Get your App credentials")
    print("   Go to: https://developers.facebook.com/apps/")
    print("   Select your app → Settings → Basic")
    print()
    
    app_id = input("Enter your App ID: ").strip()
    app_secret = input("Enter your App Secret: ").strip()
    
    # Exchange for long-lived token
    print("\n🔄 Exchanging for long-lived token...")
    result = exchange_for_long_lived_token(short_lived_token, app_id, app_secret)
    
    if not result:
        print("\n❌ Failed to generate long-lived token. Check your credentials and try again.")
        return
    
    long_lived_token = result["access_token"]
    
    # Optionally get page token (never expires)
    print("\n" + "="*70)
    print("📄 Optional: Get Page Access Token (Never Expires)")
    print("="*70)
    print("\nPage tokens don't expire as long as your app is active.")
    print("This is better than user tokens for automation.\n")
    
    get_page_token = input("Do you want to get a page access token? (y/n): ").strip().lower()
    
    if get_page_token == 'y':
        page_id = input("Enter your Facebook Page ID: ").strip()
        
        print("\n🔄 Getting page access token...")
        page_result = get_page_access_token(long_lived_token, page_id)
        
        if page_result:
            final_token = page_result["access_token"]
            token_type = "Page Access Token (Never Expires)"
        else:
            final_token = long_lived_token
            token_type = "Long-Lived User Token (60 days)"
    else:
        final_token = long_lived_token
        token_type = "Long-Lived User Token (60 days)"
    
    # Display results
    print("\n" + "="*70)
    print("✅ SUCCESS!")
    print("="*70)
    print(f"\n🎉 Token Type: {token_type}")
    print(f"\n🔑 Your Token:\n{final_token}")
    print("\n📝 Next Steps:")
    print("1. Copy the token above")
    print("2. Add it to your .env file:")
    print(f"   FACEBOOK_ACCESS_TOKEN={final_token}")
    print("\n3. This token will work for:")
    print("   - Facebook posting")
    print("   - Instagram posting (if you have Instagram Business Account)")
    
    if get_page_token == 'y':
        print("\n⏰ Renewal: This token doesn't expire (as long as your app is active)")
    else:
        print(f"\n⏰ Renewal: {result['expiry_date']}")
        print("   Run this script again before expiry to get a new token")
    
    print("\n" + "="*70)
    
    # Save to file
    save = input("\nSave token to file? (y/n): ").strip().lower()
    if save == 'y':
        filename = f"facebook_token_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write(f"Token Type: {token_type}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            if get_page_token != 'y':
                f.write(f"Expires: {result['expiry_date']}\n")
            f.write(f"\nFACEBOOK_ACCESS_TOKEN={final_token}\n")
        
        print(f"✅ Token saved to: {filename}")


if __name__ == "__main__":
    main()
