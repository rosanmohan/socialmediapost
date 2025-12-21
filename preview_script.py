
import config
from viral_content_service import ViralContentService
from loguru import logger

def preview():
    svc = ViralContentService()
    headline = "The 'winners and losers' in Universal UK's plan to rival Disneyland Paris"
    content = "Universal UK's ambitious plan to build a massive theme park in Bedford could shake up the European tourism industry. Local businesses hope for a boost, while residents worry about traffic and infrastructure."
    
    script = svc.summarize_to_story(headline, content)
    hook = svc.generate_viral_hook(headline)
    
    print("\n" + "="*50)
    print("SCRIPT PREVIEW (CONCISE 100-WORD VERSION)")
    print(f"HOOK: {hook}")
    total_words = 0
    for i, part in enumerate(script):
        words = len(part.split())
        total_words += words
        print(f"Part {i+1} ({words} words): {part}")
    print(f"\nTOTAL WORDS: {total_words}")
    print("="*50 + "\n")

if __name__ == "__main__":
    preview()
