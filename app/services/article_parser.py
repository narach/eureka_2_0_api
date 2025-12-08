import logging
import httpx
from bs4 import BeautifulSoup
from typing import Optional

logger = logging.getLogger(__name__)


async def fetch_article_content(url: str) -> Optional[str]:
    """
    Fetches and extracts text content from an article URL.
    For PMC articles, extracts the main content.
    """
    logger.debug(f"Fetching article content from: {url}")
    
    # Basic browser-like headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    async with httpx.AsyncClient(timeout=30.0, headers=headers, follow_redirects=True) as client:
        response = await client.get(str(url))
        response.raise_for_status()
        logger.debug(f"Successfully fetched HTTP response from: {url}")
        
        soup = BeautifulSoup(response.text, "lxml")
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Try to find main content area
        # For PMC articles, look for specific content sections
        main_content = (
            soup.find("div", class_="tsec sec") or
            soup.find("div", id="maincontent") or
            soup.find("div", class_="article-content") or
            soup.find("article") or
            soup.find("main") or
            soup.find("div", class_="content")
        )
        
        if main_content:
            text = main_content.get_text(separator=" ", strip=True)
        else:
            # Fallback to body text, but exclude navigation and footer
            body = soup.find("body")
            if body:
                # Remove common non-content elements
                for elem in body.find_all(["nav", "header", "footer", "aside"]):
                    elem.decompose()
                text = body.get_text(separator=" ", strip=True)
            else:
                text = soup.get_text(separator=" ", strip=True)
        
        # Clean up excessive whitespace
        text = " ".join(text.split())
        
        return text if text else None

