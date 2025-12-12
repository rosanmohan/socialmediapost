"""
Google Drive Asset Manager
Allows using Google Drive folders as cloud storage for assets (backgrounds/audio).
"""
import io
import os
import random
import config
from loguru import logger
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

class GoogleDriveAssets:
    def __init__(self):
        self.creds = None
        self.service = None
        self.scopes = ['https://www.googleapis.com/auth/drive.readonly']
        
    def _authenticate(self):
        """Authenticate with Google Drive"""
        if self.service:
            return

        # Try to load from refresh token (Production/GitHub Actions)
        if config.YOUTUBE_REFRESH_TOKEN and config.YOUTUBE_CLIENT_ID and config.YOUTUBE_CLIENT_SECRET:
             try:
                self.creds = Credentials(
                    None,
                    refresh_token=config.YOUTUBE_REFRESH_TOKEN,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=config.YOUTUBE_CLIENT_ID,
                    client_secret=config.YOUTUBE_CLIENT_SECRET,
                    scopes=self.scopes
                )
                self.service = build('drive', 'v3', credentials=self.creds)
                return
             except Exception as e:
                 logger.warning(f"Failed to auth with env vars: {e}")

        # Fallback: Local client_secret.json (For local testing)
        if os.path.exists('client_secret.json'):
             try:
                 flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', self.scopes)
                 self.creds = flow.run_local_server(port=0)
                 self.service = build('drive', 'v3', credentials=self.creds)
                 return
             except Exception as e:
                 logger.warning(f"Failed to auth with client_secret.json: {e}")
                 
    def download_random_file(self, folder_id: str, local_dir: str, extensions: list = None) -> str:
        """Download a random file from a Drive folder to a local directory"""
        try:
            self._authenticate()
            if not self.service:
                logger.error("Google Drive service not initialized")
                return None

            # List files in folder
            query = f"'{folder_id}' in parents and trashed = false"
            results = self.service.files().list(
                q=query, pageSize=100, fields="files(id, name, mimeType, size)"
            ).execute()
            items = results.get('files', [])

            if not items:
                logger.warning(f"No files found in Drive folder: {folder_id}")
                return None

            # Filter by extension if needed
            if extensions:
                items = [f for f in items if any(f['name'].lower().endswith(ext) for ext in extensions)]
                
            if not items:
                logger.warning(f"No matching files found in Drive folder")
                return None

            # Pick random file
            file_to_download = random.choice(items)
            file_id = file_to_download['id']
            file_name = file_to_download['name']
            
            # Ensure local dir exists
            os.makedirs(local_dir, exist_ok=True)
            local_path = os.path.join(local_dir, "drive_" + file_name)
            
            # Check if file already exists locally
            if os.path.exists(local_path):
                logger.info(f"File already exists locally: {local_path}")
                return local_path

            logger.info(f"Downloading from Drive: {file_name}")
            
            request = self.service.files().get_media(fileId=file_id)
            fh = io.FileIO(local_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            return local_path
            
        except Exception as e:
            logger.error(f"Error downloading from Drive: {e}")
            return None
