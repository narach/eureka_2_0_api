import logging
from sqlalchemy.orm import Session
from typing import Optional
from app.db.repositories import (
    HypothesisRepository,
    ArticleRepository,
    ValidationResultRepository,
)
from app.services.article_parser import fetch_article_content
from app.services.llm_service import LLMService
from app.models import AnalyticsResult

logger = logging.getLogger(__name__)


class ValidationService:
    """Service for handling validation logic with database caching."""
    
    def __init__(self):
        self.llm_service = LLMService()
    
    async def validate_hypothesis(
        self, db: Session, hypothesis_title: str, article_url: str
    ) -> AnalyticsResult:
        """
        Validate a hypothesis against an article with database caching.
        
        Logic:
        1. Check if article exists by URL
        2. Check if hypothesis exists by title
        3. Check if validation result exists for article+hypothesis
        4. If article doesn't exist: parse, save article, validate, save result
        5. If article exists but hypothesis is new: validate, save result
        6. If both exist: return cached result
        """
        logger.debug(f"Validating hypothesis '{hypothesis_title[:100]}' against article: {article_url}")
        
        # Get or create hypothesis
        hypothesis = HypothesisRepository.get_by_title(db, hypothesis_title)
        if not hypothesis:
            logger.debug(f"Creating new hypothesis: {hypothesis_title[:100]}")
            hypothesis = HypothesisRepository.create(db, hypothesis_title)
        else:
            logger.debug(f"Using existing hypothesis (ID: {hypothesis.id})")
        
        # Check if article exists
        article = ArticleRepository.get_by_url(db, article_url)
        
        # Check if validation result already exists
        if article:
            existing_result = ValidationResultRepository.get_by_hypothesis_and_article(
                db, hypothesis.id, article.id
            )
            if existing_result:
                # Return cached result
                logger.debug(f"Using cached validation result for article: {article_url}")
                return AnalyticsResult(
                    relevancy=existing_result.relevancy,
                    key_take=existing_result.key_take,
                    validity=existing_result.validity,
                )
        
        # Article doesn't exist or validation doesn't exist
        if not article:
            logger.debug(f"Article not in database, fetching: {article_url}")
            # Parse article content
            article_content = await fetch_article_content(article_url)
            if not article_content:
                logger.error(f"Could not extract content from: {article_url}")
                raise ValueError("Could not extract content from the article URL")
            
            logger.debug(f"Fetched article content ({len(article_content)} chars)")
            
            # Extract title from content (first 200 chars as fallback)
            article_title = article_content[:200].split('\n')[0].strip()[:200]
            
            # Save article to database
            article = ArticleRepository.create(
                db, title=article_title, url=article_url, content=article_content
            )
            logger.debug(f"Saved article to database (ID: {article.id})")
        else:
            # Article exists, use its content
            logger.debug(f"Using existing article from database (ID: {article.id})")
            article_content = article.content
        
        # Validate hypothesis using LLM
        logger.debug("Calling LLM for hypothesis validation")
        result = await self.llm_service.validate_hypothesis(
            hypothesis=hypothesis_title,
            article_content=article_content,
        )
        logger.debug(f"LLM validation complete: relevancy={result.relevancy}, validity={result.validity}")
        
        # Save validation result to database
        ValidationResultRepository.create(
            db,
            hypothesis_id=hypothesis.id,
            article_id=article.id,
            relevancy=result.relevancy,
            key_take=result.key_take,
            validity=result.validity,
        )
        logger.debug("Saved validation result to database")
        
        return result

