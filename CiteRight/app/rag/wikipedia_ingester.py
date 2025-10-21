"""
Wikipedia data ingestion module for CiteRight-Multiverse
"""
import wikipedia
import requests
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import time
import logging

logger = logging.getLogger(__name__)

class WikipediaIngester:
    def __init__(self, language: str = "en"):
        """Initialize Wikipedia ingester with language setting"""
        wikipedia.set_lang(language)
        self.language = language
        
    def search_and_ingest(self, query: str, max_pages: int = 5) -> List[Dict[str, Any]]:
        """Search Wikipedia for articles related to query and ingest them"""
        try:
            # Search for articles
            search_results = wikipedia.search(query, results=max_pages)
            articles = []
            
            for title in search_results:
                try:
                    article = self._get_article(title)
                    if article:
                        articles.append(article)
                        time.sleep(0.5)  # Rate limiting
                except Exception as e:
                    logger.warning(f"Failed to fetch article '{title}': {e}")
                    continue
                    
            return articles
            
        except Exception as e:
            logger.error(f"Wikipedia search failed: {e}")
            return []
    
    def _get_article(self, title: str) -> Dict[str, Any]:
        """Get a single Wikipedia article with metadata"""
        try:
            # Get page object
            page = wikipedia.page(title)
            
            # Get additional metadata
            url = page.url
            summary = page.summary
            
            # Clean content (remove references, citations, etc.)
            content = self._clean_content(page.content)
            
            return {
                "title": title,
                "content": content,
                "summary": summary,
                "url": url,
                "source": title,
                "origin": "Wikipedia",
                "license": "CC BY-SA 3.0",
                "metadata": {
                    "page_id": page.pageid,
                    "revision_id": page.revision_id,
                    "last_modified": getattr(page, 'last_modified', None),
                    "categories": getattr(page, 'categories', []),
                    "links": getattr(page, 'links', [])[:10]  # Limit links
                }
            }
            
        except wikipedia.exceptions.DisambiguationError as e:
            # Handle disambiguation pages
            logger.info(f"Disambiguation page for '{title}', using first option: {e.options[0]}")
            return self._get_article(e.options[0])
            
        except Exception as e:
            logger.error(f"Failed to get article '{title}': {e}")
            return None
    
    def _clean_content(self, content: str) -> str:
        """Clean Wikipedia content by removing references and citations"""
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip reference sections and citations
            if line.startswith('== References ==') or line.startswith('== External links =='):
                break
            if line.startswith('== See also ==') or line.startswith('== Notes =='):
                break
            # Skip lines that are just references
            if line.strip().startswith('^') or line.strip().startswith('['):
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def get_article_by_title(self, title: str) -> Dict[str, Any]:
        """Get a specific Wikipedia article by title"""
        return self._get_article(title)
    
    def get_random_articles(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get random Wikipedia articles"""
        try:
            random_titles = wikipedia.random(pages=count)
            articles = []
            
            for title in random_titles:
                article = self._get_article(title)
                if article:
                    articles.append(article)
                time.sleep(0.5)  # Rate limiting
                
            return articles
            
        except Exception as e:
            logger.error(f"Failed to get random articles: {e}")
            return []


def ingest_wikipedia_content(query: str, max_pages: int = 5) -> List[Dict[str, Any]]:
    """Convenience function to ingest Wikipedia content"""
    ingester = WikipediaIngester()
    return ingester.search_and_ingest(query, max_pages)
