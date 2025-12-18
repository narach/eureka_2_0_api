import logging
import httpx
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from sqlalchemy.orm import Session
from app.models import (
    ArticleUploadRequest,
    ArticleUploadResponse,
    ArticleListResponse,
    ArticleItem,
    ArticleBatchUploadResponse,
    ArticleSearchResponse,
)
from app.db.base import get_db
from app.db.models import Article
from app.services.article_service import ArticleService

logger = logging.getLogger(__name__)

router = APIRouter()
article_service = ArticleService()


@router.get("", response_model=ArticleListResponse)
def get_articles(
    db: Session = Depends(get_db),
):
    """
    Fetch all available articles from the database.
    
    Returns a list of articles with id, title, url, topic, research_id, main_item, and secondary_item (content is excluded).
    """
    articles = db.query(Article).all()
    
    article_items = [
        ArticleItem(
            id=article.id,
            title=article.title or "Untitled Article",
            url=article.url,
            topic=article.topic,
            research_id=article.research_id,
            main_item=article.main_item,
            secondary_item=article.secondary_item,
        )
        for article in articles
    ]
    
    return ArticleListResponse(articles=article_items)


@router.post("/upload", response_model=ArticleUploadResponse)
async def upload_article(
    request: ArticleUploadRequest,
    db: Session = Depends(get_db),
):
    """
    Upload a single article to the database.
    
    Parses article content from the provided URL and saves it to the database.
    If an article already exists (by URL), it returns the existing article.
    
    - **url**: Article URL (required)
    - **title**: Article title (optional, will be extracted from content if not provided)
    - **topic**: Optional topic in format "main_item - secondary_item". If provided, main_item and secondary_item will be populated automatically.
    - **main_item**: Optional main item. If provided along with secondary_item, topic will be populated automatically.
    - **secondary_item**: Optional secondary item. If provided along with main_item, topic will be populated automatically.
    
    Returns the uploaded article details.
    """
    try:
        article = await article_service.upload_article(
            db=db,
            url=request.url,
            title=request.title,
            topic=request.topic,
            main_item=request.main_item,
            secondary_item=request.secondary_item,
        )
        
        return ArticleUploadResponse(
            article=ArticleItem(
                id=article.id,
                title=article.title or "Untitled Article",
                url=article.url,
                topic=article.topic,
                research_id=article.research_id,
                main_item=article.main_item,
                secondary_item=article.secondary_item,
            ),
            message="Article uploaded successfully",
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


@router.post("/upload_batch", response_model=ArticleBatchUploadResponse)
async def upload_articles_batch(
    file: UploadFile = File(..., description="Excel file with columns: Topic, Title, URL"),
    db: Session = Depends(get_db),
):
    """
    Upload multiple articles from an Excel file.
    
    The Excel file must have the following columns:
    - **Research**: Research ID (mandatory, should reference researches.id)
    - **Topic**: Article topic (mandatory)
    - **Title**: Article title (mandatory)
    - **URL**: Article URL (mandatory)
    - **Main Item**: Main item (optional, if not provided will be extracted from topic or left empty)
    - **Secondary Item**: Secondary item (optional, if not provided will be extracted from topic or left empty)
    
    File format:
    - 1st line: Headers [Research, Topic, Title, URL, Main Item, Secondary Item]
    - 2nd and subsequent lines: Data [research_id, topic, title, url, main_item, secondary_item]
    
    The first 4 fields (Research, Topic, Title, URL) are mandatory. If any of these is missing or invalid, 
    the row will be skipped with a warning logged and processing will continue with the next row.
    
    Main Item and Secondary Item are optional. If provided, they will be used directly. 
    If not provided, they will be extracted from the topic field (if topic contains "-") or left empty.
    
    Each row will be processed to:
    1. Validate all mandatory fields are present and valid
    2. Parse the article content from the URL
    3. Save the article to the database with the provided research_id, topic, title, main_item, and secondary_item
    
    If parsing fails for an article, it will be logged but won't stop the batch processing.
    
    Returns statistics about uploaded and failed articles.
    """
    # Validate file type
    if not file.filename or not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="File must be an Excel file (.xlsx or .xls)",
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Process batch upload
        uploaded_count, failed_count = await article_service.upload_articles_batch(
            db=db,
            excel_data=file_content,
        )
        
        return ArticleBatchUploadResponse(
            uploaded_articles=uploaded_count,
            failed_articles=failed_count,
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error in batch upload: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process batch upload: {str(e)}",
        )


@router.get("/search", response_model=ArticleSearchResponse)
def search_articles_by_research(
    research_id: int = Query(
        ...,
        description="Research ID to filter articles",
    ),
    db: Session = Depends(get_db),
):
    """
    Search articles by research_id.
    
    Returns a list of articles with id, title, url, topic, research_id, main_item, and secondary_item.
    """
    try:
        articles = article_service.get_articles_by_research_id(db=db, research_id=research_id)
        
        article_items = [
            ArticleItem(
                id=article.id,
                title=article.title or "Untitled Article",
                url=article.url,
                topic=article.topic,
                research_id=article.research_id,
                main_item=article.main_item,
                secondary_item=article.secondary_item,
            )
            for article in articles
        ]
        
        return ArticleSearchResponse(articles=article_items)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search articles: {str(e)}",
        )

