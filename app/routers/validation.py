import httpx
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import HypothesisValidationRequest, HypothesisValidationResponse
from app.db.base import get_db
from app.services.validation_service import ValidationService

router = APIRouter()
validation_service = ValidationService()


@router.post("/validate", response_model=HypothesisValidationResponse)
async def validate_hypothesis(
    request: HypothesisValidationRequest,
    db: Session = Depends(get_db),
):
    """
    Validates a life science article against a hypothesis.
    
    - **hypothesis**: The hypothesis to validate
    - **article_url**: URL of the article to validate
    
    Returns analytics result with relevancy, key takeaways, and validity scores.
    Uses database caching to avoid re-parsing articles and re-validating hypotheses.
    """
    try:
        result = await validation_service.validate_hypothesis(
            db=db,
            hypothesis_title=request.hypothesis,
            article_url=str(request.article_url),
        )
        
        return HypothesisValidationResponse(result=result)
    
    except httpx.HTTPStatusError as e:
        # Return the actual HTTP status code from the error
        raise HTTPException(
            status_code=e.response.status_code,
            detail=str(e),
        )
    except HTTPException:
        raise
    except ValueError as e:
        # Validation errors (e.g., could not extract content)
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    except Exception as e:
        # For other errors, still return 500 but with the actual error message
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

