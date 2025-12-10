"""
News collection and ranking service
Fetches trending news from multiple sources and ranks them by popularity
"""
import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from fuzzywuzzy import fuzz
from loguru import logger
import config
from database import NewsItem, SessionLocal
import time

class NewsService:
    """Service to fetch and rank news articles"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def fetch_from_newsapi(self, query: str = "trending", max_results: int = 20) -> List[Dict]:
        """Fetch news from NewsAPI.org"""
        if not config.NEWS_API_KEY:
            logger.warning("NewsAPI key not configured")
            return []
        
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "sortBy": "popularity",
                "pageSize": max_results,
                "language": "en",
                "apiKey": config.NEWS_API_KEY
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for article in data.get("articles", []):
                if article.get("title") and article.get("url"):
                    articles.append({
                        "title": article["title"],
                        "description": article.get("description", ""),
                        "url": article["url"],
                        "source": article.get("source", {}).get("name", "Unknown"),
                        "published_at": self._parse_date(article.get("publishedAt", ""))
                    })
            
            logger.info(f"Fetched {len(articles)} articles from NewsAPI")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching from NewsAPI: {e}")
            return []
    
    def fetch_from_gnews(self, query: str = "trending", max_results: int = 20) -> List[Dict]:
        """Fetch news from GNews API"""
        if not config.GNEWS_API_KEY:
            logger.warning("GNews API key not configured")
            return []
        
        try:
            url = "https://gnews.io/api/v4/search"
            params = {
                "q": query,
                "token": config.GNEWS_API_KEY,
                "lang": "en",
                "max": max_results,
                "sortby": "popularity"
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for article in data.get("articles", []):
                if article.get("title") and article.get("url"):
                    articles.append({
                        "title": article["title"],
                        "description": article.get("description", ""),
                        "url": article["url"],
                        "source": article.get("source", {}).get("name", "Unknown"),
                        "published_at": self._parse_date(article.get("publishedAt", ""))
                    })
            
            logger.info(f"Fetched {len(articles)} articles from GNews")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching from GNews: {e}")
            return []
    
    def fetch_from_rss(self, rss_urls: List[str]) -> List[Dict]:
        """Fetch news from RSS feeds"""
        articles = []
        
        for url in rss_urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:10]:  # Limit per feed
                    if entry.get("title") and entry.get("link"):
                        articles.append({
                            "title": entry["title"],
                            "description": entry.get("description", ""),
                            "url": entry["link"],
                            "source": feed.feed.get("title", "RSS Feed"),
                            "published_at": self._parse_date(entry.get("published", ""))
                        })
            except Exception as e:
                logger.error(f"Error fetching RSS from {url}: {e}")
        
        return articles
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats"""
        if not date_str:
            return datetime.utcnow()
        
        formats = [
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S%z",
            "%a, %d %b %Y %H:%M:%S %Z",
            "%a, %d %b %Y %H:%M:%S %z"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        
        return datetime.utcnow()
    
    def fetch_all_news(self) -> List[Dict]:
        """Fetch news from all configured sources"""
        all_articles = []
        
        # Fetch from APIs
        all_articles.extend(self.fetch_from_newsapi())
        all_articles.extend(self.fetch_from_gnews())
        
        # Fetch from RSS feeds (popular news sources)
        rss_urls = [
            "https://feeds.bbci.co.uk/news/rss.xml",
            "https://rss.cnn.com/rss/edition.rss",
            "https://feeds.reuters.com/reuters/topNews",
            "https://www.theguardian.com/world/rss"
        ]
        all_articles.extend(self.fetch_from_rss(rss_urls))
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            url = article["url"]
            if url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        logger.info(f"Total unique articles fetched: {len(unique_articles)}")
        return unique_articles
    
    def score_article(self, article: Dict, all_articles: List[Dict]) -> float:
        """Score an article based on popularity metrics"""
        score = 0.0
        
        # Age factor (prefer recent news)
        if article.get("published_at"):
            age_hours = (datetime.utcnow() - article["published_at"]).total_seconds() / 3600
            if age_hours <= config.MAX_NEWS_AGE_HOURS:
                score += 10.0 * (1 - age_hours / config.MAX_NEWS_AGE_HOURS)
        
        # Source credibility (well-known sources get boost)
        credible_sources = ["BBC", "CNN", "Reuters", "The Guardian", "Associated Press", "AP"]
        source = article.get("source", "").upper()
        if any(cred in source for cred in credible_sources):
            score += 5.0
        
        # Title length (prefer concise titles)
        title_len = len(article.get("title", ""))
        if 30 <= title_len <= 100:
            score += 2.0
        
        # Description quality
        desc = article.get("description", "")
        if desc and len(desc) > 50:
            score += 2.0
        
        # Duplicate detection (penalize if similar to many others)
        title = article.get("title", "").lower()
        similar_count = sum(1 for a in all_articles 
                          if fuzz.ratio(title, a.get("title", "").lower()) > 70)
        if similar_count > 3:
            score -= 5.0  # Too many similar articles
        
        return score
    
    def rank_and_filter(self, articles: List[Dict]) -> List[Dict]:
        """Rank articles by score and filter"""
        # Score all articles
        scored_articles = []
        for article in articles:
            score = self.score_article(article, articles)
            article["score"] = score
            scored_articles.append(article)
        
        # Sort by score (descending)
        scored_articles.sort(key=lambda x: x["score"], reverse=True)
        
        # Filter by age
        now = datetime.utcnow()
        filtered = []
        for article in scored_articles:
            if article.get("published_at"):
                age_hours = (now - article["published_at"]).total_seconds() / 3600
                if config.MIN_NEWS_AGE_HOURS <= age_hours <= config.MAX_NEWS_AGE_HOURS:
                    filtered.append(article)
        
        # Return top N
        return filtered[:config.TOP_N_NEWS_TO_CONSIDER]
    
    def get_top_news(self) -> List[Dict]:
        """Main method: fetch and return top news articles"""
        logger.info("Fetching news from all sources...")
        all_articles = self.fetch_all_news()
        
        if not all_articles:
            logger.warning("No articles fetched")
            return []
        
        logger.info("Ranking and filtering articles...")
        top_articles = self.rank_and_filter(all_articles)
        
        logger.info(f"Selected {len(top_articles)} top articles")
        return top_articles
    
    def save_to_database(self, articles: List[Dict]) -> List[Dict]:
        """Save articles to database and return saved item info (with IDs)"""
        db = SessionLocal()
        saved_items_info = []
        
        try:
            for article in articles:
                # Check if already exists
                existing = db.query(NewsItem).filter_by(url=article["url"]).first()
                if existing:
                    # Return existing item info
                    saved_items_info.append({
                        "id": existing.id,
                        "url": existing.url,
                        "title": existing.title
                    })
                    continue
                
                news_item = NewsItem(
                    title=article["title"],
                    description=article.get("description", ""),
                    url=article["url"],
                    source=article.get("source", "Unknown"),
                    published_at=article.get("published_at", datetime.utcnow()),
                    score=article.get("score", 0.0)
                )
                db.add(news_item)
                db.flush()  # Flush to get the ID without committing
                
                # Extract ID before session closes
                saved_items_info.append({
                    "id": news_item.id,
                    "url": news_item.url,
                    "title": news_item.title
                })
            
            db.commit()
            logger.info(f"Saved {len(saved_items_info)} news items to database")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving to database: {e}")
        finally:
            db.close()
        
        return saved_items_info
    
    def get_unused_news(self, limit: int = 1) -> List[NewsItem]:
        """Get unused news items from database"""
        db = SessionLocal()
        try:
            items = db.query(NewsItem).filter_by(used_in_post=False).order_by(NewsItem.score.desc()).limit(limit).all()
            return items
        finally:
            db.close()

