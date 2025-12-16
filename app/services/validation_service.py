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
        # Get or create hypothesis
        hypothesis = HypothesisRepository.get_by_title(db, hypothesis_title)
        if not hypothesis:
            hypothesis = HypothesisRepository.create(db, hypothesis_title)
        
        # Check if article exists
        article = ArticleRepository.get_by_url(db, article_url)
        
        # Check if validation result already exists
        if article:
            existing_result = ValidationResultRepository.get_by_hypothesis_and_article(
                db, hypothesis.id, article.id
            )
            if existing_result:
                # Return cached result
                return AnalyticsResult(
                    relevancy=existing_result.relevancy,
                    key_take=existing_result.key_take,
                    validity=existing_result.validity,
                )
        
        # Article doesn't exist or validation doesn't exist
        if not article:
            # Parse article content
            article_content = await fetch_article_content(article_url)
            if not article_content:
                logger.error(f"Could not extract content from: {article_url}")
                raise ValueError("Could not extract content from the article URL")
            
            # Extract title from content (first 200 chars as fallback)
            article_title = article_content[:200].split('\n')[0].strip()[:200]
            
            # Save article to database
            article = ArticleRepository.create(
                db, title=article_title, url=article_url, content=article_content
            )
        else:
            # Article exists, use its content
            article_content = article.content
        
        # Validate hypothesis using LLM
        try:
            result = await self.llm_service.validate_hypothesis(
                hypothesis=hypothesis_title,
                article_content=article_content,
            )
        except Exception as e:
            logger.error(f"Hypothesis validation failed for article {article_url}: {str(e)}")
            raise
        
        # Save validation result to database
        ValidationResultRepository.create(
            db,
            hypothesis_id=hypothesis.id,
            article_id=article.id,
            relevancy=result.relevancy,
            key_take=result.key_take,
            validity=result.validity,
        )
        
        return result
    
    async def validate_hypothesis_by_article_id(
        self, db: Session, hypothesis_title: str, article_id: int
    ) -> AnalyticsResult:
        """
        Validate a hypothesis against an article by article ID with database caching.
        
        Logic:
        1. Get article by ID from database
        2. Check if hypothesis exists by title
        3. Check if validation result exists for article+hypothesis
        4. If validation doesn't exist: validate, save result
        5. If validation exists: return cached result
        
        Args:
            db: Database session
            hypothesis_title: The hypothesis to validate
            article_id: ID of the article to validate
            
        Returns:
            AnalyticsResult with relevancy, key_take, and validity scores
        """
        # Get article by ID
        article = ArticleRepository.get_by_id(db, article_id)
        if not article:
            raise ValueError(f"Article with ID {article_id} not found")
        
        # Get or create hypothesis
        hypothesis = HypothesisRepository.get_by_title(db, hypothesis_title)
        if not hypothesis:
            hypothesis = HypothesisRepository.create(db, hypothesis_title)
        
        # Check if validation result already exists
        existing_result = ValidationResultRepository.get_by_hypothesis_and_article(
            db, hypothesis.id, article.id
        )
        if existing_result:
            # Return cached result
            return AnalyticsResult(
                relevancy=existing_result.relevancy,
                key_take=existing_result.key_take,
                validity=existing_result.validity,
            )
        
        # Validation doesn't exist, perform validation
        article_content = article.content
        if not article_content:
            logger.error(f"Article {article_id} has no content")
            raise ValueError(f"Article with ID {article_id} has no content")
        
        # Validate hypothesis using LLM
        try:
            result = await self.llm_service.validate_hypothesis(
                hypothesis=hypothesis_title,
                article_content=article_content,
            )
        except Exception as e:
            logger.error(f"Hypothesis validation failed for article ID {article_id}: {str(e)}")
            raise
        
        # Save validation result to database
        ValidationResultRepository.create(
            db,
            hypothesis_id=hypothesis.id,
            article_id=article.id,
            relevancy=result.relevancy,
            key_take=result.key_take,
            validity=result.validity,
        )
        
        return result

