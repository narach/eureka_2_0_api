import logging
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.db.repositories import HypothesisRepository
from app.services.llm_service import LLMService
from app.services.article_service import ArticleService
from app.services.validation_service import ValidationService
from app.models import AnalyticsResult

logger = logging.getLogger(__name__)


class HypothesisService:
    """Service for handling hypothesis creation with article search and validation."""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.article_service = ArticleService()
        self.validation_service = ValidationService()
    
    async def create_hypothesis_with_validation(
        self,
        db: Session,
        hypothesis_title: str,
        articles_amount: int = 10,
    ) -> Dict[str, Any]:
        """
        Create a new hypothesis, search for relevant articles, and validate.
        
        Steps:
        1. Search for relevant PubMed articles using LLM
        2. Parse and save articles to database
        3. Validate hypothesis against each successfully loaded article
        4. Return validation results
        
        Args:
            db: Database session
            hypothesis_title: The hypothesis to create and validate
            articles_amount: Number of articles to search for (default: 10)
            
        Returns:
            Dictionary with validation_results, failed_articles_amount, and failed_articles
        """
        # Step 1: Search for relevant articles using LLM
        try:
            article_urls = await self.llm_service.search_pubmed_articles(
                hypothesis=hypothesis_title,
                articles_amount=articles_amount,
            )
        except Exception as e:
            logger.error(f"Failed to search for articles: {str(e)}")
            raise
        
        if not article_urls:
            return {
                "validation_results": [],
                "failed_articles_amount": 0,
                "failed_articles": [],
            }
        
        # Step 2: Parse and save articles to database
        try:
            uploaded_count, failed_count, failed_urls = await self.article_service.upload_articles(
                db=db,
                article_urls=article_urls,
            )
        except Exception as e:
            logger.error(f"Failed to upload articles: {str(e)}")
            raise
        
        # Step 3: Validate hypothesis against each successfully uploaded article
        validation_results = []
        validation_failed_urls = []
        
        # Get successfully uploaded articles (those not in failed_urls)
        successful_urls = [url for url in article_urls if url not in failed_urls]
        
        for article_url in successful_urls:
            try:
                result = await self.validation_service.validate_hypothesis(
                    db=db,
                    hypothesis_title=hypothesis_title,
                    article_url=article_url,
                )
                
                validation_results.append({
                    "article": article_url,
                    "relevancy": result.relevancy,
                    "key_take": result.key_take,
                    "validity": result.validity,
                })
                
            except Exception as e:
                logger.error(f"Failed to validate article {article_url}: {str(e)}")
                validation_failed_urls.append(article_url)
        
        # Combine parsing failures and validation failures
        all_failed_urls = list(set(failed_urls + validation_failed_urls))
        
        return {
            "validation_results": validation_results,
            "failed_articles_amount": len(all_failed_urls),
            "failed_articles": all_failed_urls,
        }

