import httpx
import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import HypothesisCreationRequest, HypothesisCreationResponse
from app.db.base import get_db
from app.services.hypothesis_service import HypothesisService

logger = logging.getLogger(__name__)
router = APIRouter()
hypothesis_service = HypothesisService()


@router.post("/create", response_model=HypothesisCreationResponse)
async def create_hypothesis(
    request: HypothesisCreationRequest,
    db: Session = Depends(get_db),
):
    """
    Create a new hypothesis and validate it against relevant articles.
    
    This endpoint:
    1. Searches for relevant PubMed articles using LLM
    2. Parses and saves articles to the database
    3. Validates the hypothesis against each successfully loaded article
    
    - **hypothesis**: The hypothesis to create and validate
    - **articles_amount**: Number of articles to search for (default: 10, max: 50)
    
    Returns validation results for each successfully processed article.
    """
    logger.debug(
        f"Creating hypothesis: {request.hypothesis[:100]} "
        f"with {request.articles_amount} articles"
    )
    
    try:
        result = await hypothesis_service.create_hypothesis_with_validation(
            db=db,
            hypothesis_title=request.hypothesis,
            articles_amount=request.articles_amount,
        )
        
        logger.debug(
            f"Hypothesis creation complete: {len(result['validation_results'])} "
            f"validations, {result['failed_articles_amount']} failed"
        )
        
        return HypothesisCreationResponse(**result)
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during hypothesis creation: {str(e)}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during hypothesis creation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

