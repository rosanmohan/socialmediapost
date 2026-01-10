from news_service import NewsService
import config

ns = NewsService()
print("Fetching news across all categories...")
all_news = ns.fetch_all_news()

# Save to DB
ns.save_to_database(all_news)

# Print counts
for cat in config.CATEGORIES:
    items = ns.get_unused_news(limit=10, category=cat)
    print(f"Category {cat.upper()}: {len(items)} unused items in DB")
    if items:
        print(f" - Top item: {items[0].title}")
