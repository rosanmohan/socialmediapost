# News Sources Configuration

## Current Setup (After Update)

Your bot now fetches news from a **balanced mix of International and Indian sources**.

### News Sources Breakdown:

#### 1. NewsAPI (API-based)
- **Global Trending**: 15 articles
- **India-specific**: 10 articles
- **Total**: 25 articles from NewsAPI

#### 2. GNews API (API-based)
- **Global Trending**: 15 articles  
- **India-specific**: 10 articles
- **Total**: 25 articles from GNews

#### 3. RSS Feeds (Free, No API key needed)

**International Sources:**
- BBC News (UK)
- CNN (US)
- Reuters (International)
- The Guardian (UK)

**Indian Sources:**
- The Hindu (National News)
- Times of India (Top Stories)
- Hindustan Times (India News)
- NDTV (India)
- Indian Express (India Section)

### Total News Mix:
- **Approximately 60% International, 40% Indian**
- The system automatically ranks and selects the top 5 most relevant/trending stories
- Duplicates are automatically removed

---

## How to Adjust the Mix

### Want MORE Indian News?
Edit `news_service.py` line 145-149:

```python
# More Indian focus
all_articles.extend(self.fetch_from_newsapi(query="trending", max_results=10))
all_articles.extend(self.fetch_from_newsapi(query="India", max_results=20))  # Increased
all_articles.extend(self.fetch_from_gnews(query="trending", max_results=10))
all_articles.extend(self.fetch_from_gnews(query="India", max_results=20))  # Increased
```

### Want ONLY Indian News?
```python
# India only
all_articles.extend(self.fetch_from_newsapi(query="India", max_results=25))
all_articles.extend(self.fetch_from_gnews(query="India", max_results=25))
```

### Want ONLY International News?
```python
# International only
all_articles.extend(self.fetch_from_newsapi(query="trending", max_results=25))
all_articles.extend(self.fetch_from_gnews(query="trending", max_results=25))

# And remove Indian RSS feeds from lines 157-161
```

### Want Specific Topics?
You can change the query to anything:
```python
all_articles.extend(self.fetch_from_newsapi(query="technology", max_results=15))
all_articles.extend(self.fetch_from_newsapi(query="sports", max_results=10))
all_articles.extend(self.fetch_from_newsapi(query="business India", max_results=10))
```

---

## Adding More Indian RSS Feeds

You can add more Indian news sources to the RSS list (lines 157-161):

```python
# More Indian sources you can add:
"https://www.business-standard.com/rss/home_page_top_stories.rss",  # Business Standard
"https://www.livemint.com/rss/homepage",  # Mint (Business)
"https://www.theweek.in/news.rss",  # The Week
"https://www.news18.com/rss/india.xml",  # News18
"https://www.firstpost.com/rss/india.xml",  # Firstpost
```

---

## How the Ranking Works

The system automatically scores each article based on:
1. **Recency** (newer = higher score)
2. **Source credibility** (BBC, Reuters, etc. get bonus)
3. **Title quality** (not too short, not too long)
4. **Description quality** (has meaningful content)
5. **Uniqueness** (penalizes duplicate stories)

The top 5 highest-scoring articles are selected for your video.

---

## Testing Your Changes

After modifying `news_service.py`:

1. **Test locally:**
   ```bash
   python main_1.py
   ```

2. **Check the logs** to see which sources were used

3. **Push to GitHub:**
   ```bash
   git add news_service.py
   git commit -m "Add Indian news sources"
   git push
   ```

Your next scheduled run will use the updated sources!
