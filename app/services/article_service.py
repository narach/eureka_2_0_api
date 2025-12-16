import logging
from sqlalchemy.orm import Session
from typing import List, Tuple
from app.db.repositories import ArticleRepository
from app.db.models import Article
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
        db: Session,
        article_urls: List[str],
        topic: str | None = None,
        main_item: str | None = None,
        secondary_item: str | None = None,
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
                continue
            
            processed_urls.add(url_str)
            
            try:
                # Check if article already exists in database
                existing_article = ArticleRepository.get_by_url(db, url_str)
                if existing_article:
                    # Article already exists in database, count as uploaded
                    uploaded_count += 1
                    continue
                
                # Fetch and parse article content
                article_content = await fetch_article_content(url_str)
                
                if not article_content:
                    logger.error(f"Failed to extract content from: {url_str}")
                    failed_urls.append(url_str)
                    continue
                
                # Extract title from content
                article_title = ArticleService._extract_article_title(article_content)
                
                # Save article to database
                ArticleRepository.create(
                    db=db,
                    title=article_title,
                    url=url_str,
                    content=article_content,
                    topic=topic,
                    main_item=main_item,
                    secondary_item=secondary_item,
                )
                
                uploaded_count += 1
                
            except Exception as e:
                # Any error during processing marks the article as failed
                logger.error(f"Error processing article {url_str}: {str(e)}")
                failed_urls.append(url_str)
        
        failed_count = len(failed_urls)
        return uploaded_count, failed_count, failed_urls
    
    @staticmethod
    async def upload_article(
        db: Session,
        url: str,
        title: str | None = None,
        topic: str | None = None,
        main_item: str | None = None,
        secondary_item: str | None = None,
    ):
        """
        Upload a single article to the database.
        
        Args:
            db: Database session
            url: Article URL
            title: Article title (optional, will be extracted from content if not provided)
            topic: Optional topic
            main_item: Optional main item
            secondary_item: Optional secondary item
            
        Returns:
            Article object (existing or newly created)
        """
        url_str = str(url).strip()
        
        if not url_str:
            raise ValueError("URL cannot be empty")
        
        # Check if article already exists in database
        existing_article = ArticleRepository.get_by_url(db, url_str)
        if existing_article:
            return existing_article
        
        # Fetch and parse article content
        article_content = await fetch_article_content(url_str)
        
        if not article_content:
            logger.error(f"Failed to extract content from: {url_str}")
            raise ValueError(f"Failed to extract content from: {url_str}")
        
        # Use provided title or extract from content
        if title:
            article_title = title.strip()
        else:
            article_title = ArticleService._extract_article_title(article_content)
        
        # Save article to database
        article = ArticleRepository.create(
            db=db,
            title=article_title,
            url=url_str,
            content=article_content,
            topic=topic,
            main_item=main_item,
            secondary_item=secondary_item,
        )
        
        return article
    
    @staticmethod
    async def upload_articles_batch(
        db: Session,
        excel_data: bytes,
    ) -> tuple[int, int]:
        """
        Upload multiple articles from an Excel file.
        
        Args:
            db: Database session
            excel_data: Excel file content as bytes
            
        Returns:
            Tuple of (uploaded_count, failed_count)
        """
        import pandas as pd
        from io import BytesIO
        
        uploaded_count = 0
        failed_count = 0
        
        try:
            # Read Excel file
            df = pd.read_excel(BytesIO(excel_data), engine='openpyxl')
            
            # Validate required columns - all 4 are mandatory: Research, Topic, Title, URL
            required_columns = ['Research', 'Topic', 'Title', 'URL']
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"Excel file must contain columns: {', '.join(required_columns)}")
            
            # Process each row
            for row_index, (idx, row) in enumerate(df.iterrows(), start=0):
                row_num = row_index + 2  # +2 because Excel rows are 1-indexed and we skip header
                try:
                    # Extract all 4 mandatory fields
                    # Research ID (first column, mandatory)
                    research_value = row.get('Research')
                    if research_value is None or (isinstance(research_value, float) and pd.isna(research_value)):
                        logger.warning(f"Row {row_num}: Missing research ID, skipping row")
                        failed_count += 1
                        continue
                    
                    try:
                        research_id = int(research_value)
                    except (ValueError, TypeError):
                        logger.warning(f"Row {row_num}: Invalid research ID '{research_value}', skipping row")
                        failed_count += 1
                        continue
                    
                    # Topic (mandatory)
                    topic_value = row.get('Topic')
                    if topic_value is None or (isinstance(topic_value, float) and pd.isna(topic_value)):
                        logger.warning(f"Row {row_num}: Missing topic, skipping row")
                        failed_count += 1
                        continue
                    
                    topic = str(topic_value).strip()
                    if not topic or topic == 'nan':
                        logger.warning(f"Row {row_num}: Empty topic, skipping row")
                        failed_count += 1
                        continue
                    
                    # Title (mandatory)
                    title_value = row.get('Title')
                    if title_value is None or (isinstance(title_value, float) and pd.isna(title_value)):
                        logger.warning(f"Row {row_num}: Missing title, skipping row")
                        failed_count += 1
                        continue
                    
                    title = str(title_value).strip()
                    if not title or title == 'nan':
                        logger.warning(f"Row {row_num}: Empty title, skipping row")
                        failed_count += 1
                        continue
                    
                    # URL (mandatory)
                    url_value = row.get('URL')
                    if url_value is None or (isinstance(url_value, float) and pd.isna(url_value)):
                        logger.warning(f"Row {row_num}: Missing URL, skipping row")
                        failed_count += 1
                        continue
                    
                    url = str(url_value).strip()
                    if not url or url == 'nan':
                        logger.warning(f"Row {row_num}: Empty URL, skipping row")
                        failed_count += 1
                        continue
                    
                    # Check if article already exists with same URL and research_id
                    existing_article = ArticleRepository.get_by_url_and_research(db, url, research_id)
                    if existing_article:
                        uploaded_count += 1
                        continue
                    
                    # Fetch article content
                    article_content = await fetch_article_content(url)
                    if not article_content:
                        logger.error(f"Row {row_num}: Failed to extract content from URL: {url}")
                        failed_count += 1
                        continue
                    
                    # Process topic to extract main_item and secondary_item
                    # The repository will handle this automatically
                    main_item = None
                    secondary_item = None
                    
                    # Save article to database
                    ArticleRepository.create(
                        db=db,
                        title=title,
                        url=url,
                        content=article_content,
                        topic=topic,
                        main_item=main_item,
                        secondary_item=secondary_item,
                        research_id=research_id,
                    )
                    
                    uploaded_count += 1
                    
                except Exception as e:
                    # Log error but continue processing other articles
                    logger.error(f"Row {row_num}: Error processing article - {str(e)}")
                    failed_count += 1
                    continue
            
            return uploaded_count, failed_count
            
        except Exception as e:
            logger.error(f"Error reading Excel file: {str(e)}")
            raise ValueError(f"Failed to process Excel file: {str(e)}")
    
    @staticmethod
    def get_articles_by_research_id(db: Session, research_id: int) -> List[Article]:
        """
        Get all articles by research_id.
        
        Args:
            db: Database session
            research_id: Research ID
            
        Returns:
            List of articles with the specified research_id
        """
        return ArticleRepository.get_by_research_id(db, research_id)

