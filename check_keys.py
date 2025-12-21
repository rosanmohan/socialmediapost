
import os
import config
from loguru import logger

def check_keys():
    keys_to_check = [
        "OPENAI_API_KEY",
        "GROQ_API_KEY",
        "ANTHROPIC_API_KEY",
        "GNEWS_API_KEY",
        "NEWS_API_KEY"
    ]
    for key in keys_to_check:
        val = os.getenv(key)
        if val:
            logger.info(f"✅ {key} is SET (length: {len(val)})")
        else:
            logger.warning(f"❌ {key} is NOT SET")

if __name__ == "__main__":
    check_keys()
