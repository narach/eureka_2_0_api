import httpx
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import ArticleUploadRequest, ArticleUploadResponse
from app.db.base import get_db
from app.services.article_service import ArticleService

router = APIRouter()
article_service = ArticleService()


@router.post("/upload", response_model=ArticleUploadResponse)
async def upload_articles(
    request: ArticleUploadRequest,
    db: Session = Depends(get_db),
):
    """
    Upload multiple articles to the database.
    
    Parses article content from the provided URLs and saves them to the database.
    If an article already exists (by URL), it is skipped and counted as uploaded.
    
    - **article_urls**: Array of article URLs to upload
    
    Returns statistics about uploaded and failed articles.
    """
    try:
        uploaded_count, failed_count, failed_urls = await article_service.upload_articles(
            db=db,
            article_urls=[str(url) for url in request.article_urls],
        )
        
        return ArticleUploadResponse(
            uploaded_articles_amount=uploaded_count,
            failed_articles_amount=failed_count,
            failed_articles=failed_urls,
        )
    
    except httpx.HTTPStatusError as e:
        # Return the actual HTTP status code from the error
        raise HTTPException(
            status_code=e.response.status_code,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        # For other errors, return 500 with the actual error message
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

