"""
News router - Market news from RSS feeds
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict
import feedparser
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

# Trusted financial news RSS feeds
NEWS_FEEDS = [
    {
        "name": "Reuters Business",
        "url": "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best",
        "source": "Reuters"
    },
    {
        "name": "CNBC Markets",
        "url": "https://www.cnbc.com/id/10000664/device/rss/rss.html",
        "source": "CNBC"
    },
    {
        "name": "MarketWatch",
        "url": "https://feeds.marketwatch.com/marketwatch/topstories/",
        "source": "MarketWatch"
    },
    {
        "name": "Yahoo Finance",
        "url": "https://finance.yahoo.com/news/rssindex",
        "source": "Yahoo Finance"
    }
]


def parse_feed(feed_config: Dict) -> List[Dict]:
    """Parse RSS feed and return articles"""
    try:
        feed = feedparser.parse(feed_config["url"])
        articles = []
        
        for entry in feed.entries[:10]:  # Get top 10 from each feed
            try:
                # Parse published date
                pub_date = entry.get("published_parsed") or entry.get("updated_parsed")
                if pub_date:
                    pub_date_iso = datetime(*pub_date[:6]).isoformat() + "Z"
                else:
                    pub_date_iso = datetime.now().isoformat() + "Z"
                
                # Get description/summary
                description = entry.get("summary", "")
                if not description:
                    description = entry.get("description", "")
                
                # Clean HTML tags from description
                import re
                description = re.sub('<[^<]+?>', '', description)
                description = description.strip()[:300]  # Limit length
                
                articles.append({
                    "title": entry.get("title", "No title"),
                    "link": entry.get("link", ""),
                    "description": description,
                    "pubDate": pub_date_iso,
                    "source": feed_config["source"]
                })
            except Exception as e:
                logger.warning(f"Error parsing entry from {feed_config['source']}: {str(e)}")
                continue
        
        return articles
    except Exception as e:
        logger.error(f"Error fetching feed {feed_config['source']}: {str(e)}")
        return []


@router.get("")
async def get_news():
    """
    Get latest market news from multiple trusted sources
    
    Returns aggregated news articles from:
    - Reuters
    - CNBC
    - MarketWatch
    - Yahoo Finance
    """
    all_articles = []
    
    for feed_config in NEWS_FEEDS:
        articles = parse_feed(feed_config)
        all_articles.extend(articles)
    
    # Sort by publication date (newest first)
    all_articles.sort(
        key=lambda x: x["pubDate"],
        reverse=True
    )
    
    # Return top 20 articles
    return {
        "articles": all_articles[:20],
        "sources": [feed["source"] for feed in NEWS_FEEDS],
        "last_updated": datetime.now().isoformat() + "Z"
    }

