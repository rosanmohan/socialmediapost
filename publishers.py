"""
Publishers for Instagram, YouTube Shorts, and Facebook
Handles uploading and posting to each platform
"""
import os
import time
from typing import Dict, Optional
from loguru import logger
import config
from pathlib import Path

class InstagramPublisher:
    """Publish to Instagram Reels"""
    
    def __init__(self):
        self.access_token = config.FACEBOOK_ACCESS_TOKEN
        self.instagram_account_id = config.INSTAGRAM_BUSINESS_ACCOUNT_ID
    
    def publish(self, video_path: str, caption: str, hashtags: list) -> Dict:
        """Publish video to Instagram Reels"""
        # Check if credentials are configured
        if not self.access_token or not self.instagram_account_id:
            logger.debug("Instagram credentials not configured - skipping publish")
            return {"status": "failed", "error": "Credentials not configured"}
        
        # Check for placeholder values
        if (self.access_token == "your_facebook_access_token" or 
            self.instagram_account_id == "your_instagram_business_account_id"):
            logger.debug("Instagram credentials contain placeholder values - skipping publish")
            return {"status": "failed", "error": "Credentials not configured"}
        
        logger.info("Publishing to Instagram...")
        
        try:
            # Instagram Graph API requires two-step upload
            # Step 1: Create media container
            import requests
            
            hashtags_str = " ".join([f"#{tag}" for tag in hashtags[:30]])  # Limit hashtags
            full_caption = f"{caption}\n\n{hashtags_str}"
            
            # Create container
            container_url = f"https://graph.facebook.com/v18.0/{self.instagram_account_id}/media"
            
            # Upload video file
            with open(video_path, 'rb') as video_file:
                files = {'video_file': video_file}
                data = {
                    "media_type": "REELS",
                    "caption": full_caption[:2200],  # Instagram limit
                    "access_token": self.access_token
                }
                response = requests.post(container_url, files=files, data=data, timeout=300)
            
            if response.status_code != 200:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get("error", {}).get("message", response.text)
                error_code = error_data.get("error", {}).get("code", "")
                
                # Check for invalid token error
                if error_code == 190 or "Invalid OAuth access token" in error_msg:
                    logger.warning(f"Instagram access token invalid or expired: {error_msg}")
                    return {
                        "status": "failed", 
                        "error": "Invalid Instagram/Facebook access token. Please check FACEBOOK_ACCESS_TOKEN in .env file. Token may have expired or is invalid."
                    }
                
                logger.warning(f"Instagram publish failed: {error_msg}")
                return {"status": "failed", "error": error_msg}
            
            container_id = response.json().get("id")
            logger.info(f"Instagram container created: {container_id}")
            
            # Step 2: Publish container
            publish_url = f"https://graph.facebook.com/v18.0/{self.instagram_account_id}/media_publish"
            publish_params = {
                "creation_id": container_id,
                "access_token": self.access_token
            }
            
            # Wait a bit for processing
            time.sleep(5)
            
            publish_response = requests.post(publish_url, params=publish_params, timeout=60)
            
            if publish_response.status_code == 200:
                post_id = publish_response.json().get("id")
                logger.info(f"Instagram post published: {post_id}")
                return {"status": "success", "post_id": post_id, "platform": "instagram"}
            else:
                logger.error(f"Instagram publish failed: {publish_response.text}")
                return {"status": "failed", "error": publish_response.text}
                
        except Exception as e:
            logger.error(f"Error publishing to Instagram: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {"status": "failed", "error": str(e)}


class YouTubePublisher:
    """Publish to YouTube Shorts"""
    
    def __init__(self):
        self.client_id = config.YOUTUBE_CLIENT_ID
        self.client_secret = config.YOUTUBE_CLIENT_SECRET
        self.refresh_token = config.YOUTUBE_REFRESH_TOKEN
        self.youtube = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize YouTube API client"""
        # Check if credentials are configured
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            logger.debug("YouTube credentials not configured - skipping initialization")
            return
        
        # Check for placeholder values
        if (self.client_id == "your_youtube_client_id" or 
            self.client_secret == "your_youtube_client_secret" or 
            self.refresh_token == "your_youtube_refresh_token"):
            logger.debug("YouTube credentials contain placeholder values - skipping initialization")
            return
        
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            from google.auth.transport.requests import Request
            
            SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
            
            # Create credentials from refresh token
            creds = Credentials(
                token=None,
                refresh_token=self.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=SCOPES
            )
            
            # Refresh if needed
            if not creds.valid:
                creds.refresh(Request())
            
            self.youtube = build('youtube', 'v3', credentials=creds)
            logger.info("YouTube API client initialized successfully")
            
        except Exception as e:
            error_str = str(e)
            # Check for credential-related errors
            if "invalid_grant" in error_str or "expired" in error_str or "revoked" in error_str:
                logger.warning("YouTube OAuth token expired or invalid. Please regenerate your refresh token.")
                logger.debug(f"YouTube initialization error: {e}")
            else:
                logger.warning(f"YouTube client initialization failed: {e}")
                logger.debug("Make sure you have valid YouTube OAuth credentials")
    
    def publish(self, video_path: str, title: str, description: str, hashtags: list) -> Dict:
        """Publish video to YouTube Shorts"""
        if not self.youtube:
            logger.debug("YouTube client not initialized - skipping publish")
            return {"status": "failed", "error": "Client not initialized - check YouTube credentials"}
        
        logger.info("Publishing to YouTube...")
        
        try:
            hashtags_str = " ".join([f"#{tag}" for tag in hashtags[:10]])  # YouTube limit
            full_description = f"{description}\n\n{hashtags_str}\n\n#Shorts"
            
            # Ensure title includes #Shorts if not already
            if "#Shorts" not in title:
                title = f"{title} #Shorts"
            
            body = {
                'snippet': {
                    'title': title[:100],  # YouTube title limit
                    'description': full_description[:5000],  # YouTube description limit
                    'tags': hashtags[:10],
                    'categoryId': '24'  # Entertainment category
                },
                'status': {
                    'privacyStatus': 'public',
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Upload video
            insert_request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=video_path
            )
            
            response = insert_request.execute()
            video_id = response['id']
            
            logger.info(f"YouTube video uploaded: {video_id}")
            return {
                "status": "success",
                "post_id": video_id,
                "platform": "youtube",
                "url": f"https://www.youtube.com/watch?v={video_id}"
            }
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error publishing to YouTube: {e}")
            
            # Check for specific API not enabled error
            if "has not been used" in error_str or "is disabled" in error_str or "accessNotConfigured" in error_str:
                # Extract project ID if available
                import re
                project_match = re.search(r'project (\d+)', error_str)
                project_id = project_match.group(1) if project_match else "your-project"
                
                error_msg = f"YouTube Data API v3 is not enabled. Enable it at: https://console.developers.google.com/apis/api/youtube.googleapis.com/overview?project={project_id}"
                logger.error(error_msg)
                return {"status": "failed", "error": error_msg}
            
            import traceback
            logger.error(traceback.format_exc())
            return {"status": "failed", "error": str(e)}


class FacebookPublisher:
    """Publish to Facebook"""
    
    def __init__(self):
        self.access_token = config.FACEBOOK_ACCESS_TOKEN
        self.page_id = config.FACEBOOK_PAGE_ID
    
    def publish(self, video_path: str, caption: str, hashtags: list) -> Dict:
        """Publish video to Facebook"""
        # Check if credentials are configured
        if not self.access_token or not self.page_id:
            logger.debug("Facebook credentials not configured - skipping publish")
            return {"status": "failed", "error": "Credentials not configured"}
        
        # Check for placeholder values
        if (self.access_token == "your_facebook_access_token" or 
            self.page_id == "your_facebook_page_id"):
            logger.debug("Facebook credentials contain placeholder values - skipping publish")
            return {"status": "failed", "error": "Credentials not configured"}
        
        logger.info("Publishing to Facebook...")
        
        try:
            import requests
            
            hashtags_str = " ".join([f"#{tag}" for tag in hashtags[:30]])
            full_caption = f"{caption}\n\n{hashtags_str}"
            
            # Upload video to Facebook
            upload_url = f"https://graph-video.facebook.com/v18.0/{self.page_id}/videos"
            
            with open(video_path, 'rb') as video_file:
                files = {'file': video_file}
                data = {
                    'description': full_caption[:5000],  # Facebook limit
                    'access_token': self.access_token
                }
                
                response = requests.post(upload_url, files=files, data=data, timeout=300)
            
            if response.status_code == 200:
                video_id = response.json().get("id")
                logger.info(f"Facebook video uploaded: {video_id}")
                return {
                    "status": "success",
                    "post_id": video_id,
                    "platform": "facebook"
                }
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get("error", {}).get("message", response.text)
                error_code = error_data.get("error", {}).get("code", "")
                
                # Check for invalid token error
                if error_code == 190 or "Invalid OAuth access token" in error_msg:
                    logger.warning(f"Facebook access token invalid or expired: {error_msg}")
                    return {
                        "status": "failed", 
                        "error": "Invalid Facebook access token. Please check FACEBOOK_ACCESS_TOKEN in .env file. Token may have expired or is invalid."
                    }
                
                logger.warning(f"Facebook publish failed: {error_msg}")
                return {"status": "failed", "error": error_msg}
                
        except Exception as e:
            logger.error(f"Error publishing to Facebook: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {"status": "failed", "error": str(e)}


class PublisherManager:
    """Manages all publishers and coordinates posting"""
    
    def __init__(self):
        self.instagram = InstagramPublisher()
        self.youtube = YouTubePublisher()
        self.facebook = FacebookPublisher()
    
    def publish_all(self, video_path: str, content: Dict) -> Dict:
        """Publish to all platforms"""
        results = {}
        
        caption = content.get("caption", "")
        hashtags = content.get("hashtags", [])
        title = content.get("title", caption)
        
        # Publish to Instagram
        logger.info("Publishing to Instagram...")
        results["instagram"] = self.instagram.publish(video_path, caption, hashtags)
        time.sleep(2)  # Rate limiting
        
        # Publish to YouTube
        logger.info("Publishing to YouTube...")
        results["youtube"] = self.youtube.publish(video_path, title, caption, hashtags)
        time.sleep(2)  # Rate limiting
        
        # Publish to Facebook
        logger.info("Publishing to Facebook...")
        results["facebook"] = self.facebook.publish(video_path, caption, hashtags)
        
        return results

