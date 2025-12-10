"""
Utility functions for notifications, retries, and helpers
"""
import time
from functools import wraps
from typing import Callable, Any
from loguru import logger
import config

def retry_on_failure(max_retries: int = None, delay: int = None):
    """Decorator for retrying functions on failure"""
    max_retries = max_retries or config.MAX_RETRIES
    delay = delay or config.RETRY_DELAY_SECONDS
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}")
            
            raise last_exception
        return wrapper
    return decorator

def send_notification(message: str, level: str = "info"):
    """Send notification via configured channels"""
    if not config.ENABLE_NOTIFICATIONS:
        return
    
    try:
        # Telegram notification
        if config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID:
            send_telegram_notification(message, level)
        
        # Email notification (if configured)
        # Add email sending logic here if needed
        
    except Exception as e:
        logger.error(f"Error sending notification: {e}")

def send_telegram_notification(message: str, level: str = "info"):
    """Send Telegram notification"""
    # Check if Telegram is configured
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        return
    
    # Check for placeholder values
    if (config.TELEGRAM_BOT_TOKEN == "your_telegram_bot_token" or 
        config.TELEGRAM_CHAT_ID == "your_telegram_chat_id"):
        return
    
    try:
        import requests
        
        emoji_map = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        
        emoji = emoji_map.get(level, "ℹ️")
        formatted_message = f"{emoji} {message}"
        
        url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": config.TELEGRAM_CHAT_ID,
            "text": formatted_message,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        
    except Exception as e:
        logger.debug(f"Telegram notification failed: {e}")

def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for filesystem"""
    import re
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    return filename

def ensure_directory(path):
    """Ensure directory exists"""
    from pathlib import Path
    Path(path).mkdir(parents=True, exist_ok=True)



