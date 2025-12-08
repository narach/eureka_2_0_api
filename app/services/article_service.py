import logging
from sqlalchemy.orm import Session
from typing import List, Tuple
from app.db.repositories import ArticleRepository
from app.services.article_parser import fetch_article_content

logger = logging.getLogger(__name__)


class ArticleService:
    """Service for handling article upload operations."""
    
    @staticmethod
    def _extract_article_title(content: str) -> str:
        """
        Extract article title from content.
        Uses first 200 characters of the first line as fallback.
        """
        if not content:
            return "Untitled Article"
        
        # Try to get the first meaningful line
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:  # Skip very short lines
                return line[:200]  # Limit to 200 chars
        
        # Fallback to first 200 chars
        return content[:200].strip() or "Untitled Article"
    
    @staticmethod
    async def upload_articles(
        db: Session, article_urls: List[str]
    ) -> Tuple[int, int, List[str]]:
        """
        Upload multiple articles to the database.
        
        Args:
            db: Database session
            article_urls: List of article URLs to upload (duplicates are handled)
            
        Returns:
            Tuple of (uploaded_count, failed_count, failed_urls)
        """
        uploaded_count = 0
        failed_urls = []
        processed_urls = set()  # Track processed URLs to handle duplicates
        
        for url in article_urls:
            url_str = str(url).strip()
            
            # Skip empty URLs
            if not url_str:
                continue
            
            # Skip if we've already processed this URL in this batch
            if url_str in processed_urls:
                logger.debug(f"Skipping duplicate URL: {url_str}")
                continue
            
            processed_urls.add(url_str)
            logger.debug(f"Processing article URL: {url_str}")
            
            try:
                # Check if article already exists in database
                existing_article = ArticleRepository.get_by_url(db, url_str)
                if existing_article:
                    # Article already exists in database, count as uploaded
                    logger.debug(f"Article already exists in database: {url_str}")
                    uploaded_count += 1
                    continue
                
                # Fetch and parse article content
                logger.debug(f"Fetching article content: {url_str}")
                article_content = await fetch_article_content(url_str)
                
                if not article_content:
                    logger.warning(f"Failed to extract content from: {url_str}")
                    failed_urls.append(url_str)
                    continue
                
                logger.debug(f"Successfully fetched content ({len(article_content)} chars) from: {url_str}")
                
                # Extract title from content
                article_title = ArticleService._extract_article_title(article_content)
                logger.debug(f"Extracted title: {article_title[:100]}")
                
                # Save article to database
                ArticleRepository.create(
                    db=db,
                    title=article_title,
                    url=url_str,
                    content=article_content,
                )
                
                logger.debug(f"Successfully saved article to database: {url_str}")
                uploaded_count += 1
                
            except Exception as e:
                # Any error during processing marks the article as failed
                logger.error(f"Error processing article {url_str}: {str(e)}")
                failed_urls.append(url_str)
        
        failed_count = len(failed_urls)
        return uploaded_count, failed_count, failed_urls

