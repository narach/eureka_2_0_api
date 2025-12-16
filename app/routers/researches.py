from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.models import (
    ResearchListResponse,
    ResearchItem,
    ResearchSearchResponse,
    ResearchSearchItem,
)
from app.db.base import get_db
from app.services.research_service import ResearchService

router = APIRouter()
research_service = ResearchService()


@router.get("", response_model=ResearchListResponse)
def get_researches(
    db: Session = Depends(get_db),
):
    """
    Fetch all available researches from the database.
    
    Returns a list of researches with id, primary_item, and secondary_item.
    """
    try:
        researches = research_service.get_all_researches(db)
        
        research_items = [
            ResearchItem(
                id=research.id,
                primary_item=research.primary_item,
                secondary_item=research.secondary_item,
            )
            for research in researches
        ]
        
        return ResearchListResponse(researches=research_items)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch researches: {str(e)}",
        )


@router.get("/search", response_model=ResearchSearchResponse)
def search_researches(
    primary_item: Optional[str] = Query(
        default=None,
        description="Filter by primary item",
    ),
    secondary_item: Optional[str] = Query(
        default=None,
        description="Filter by secondary item",
    ),
    db: Session = Depends(get_db),
):
    """
    Search researches by primary_item and/or secondary_item.
    
    You can search by:
    - **primary_item** only: Returns researches matching the primary_item
    - **secondary_item** only: Returns researches matching the secondary_item
    - **both**: Returns researches matching both primary_item and secondary_item
    
    Returns a list of researches with id, primary_item, and secondary_item.
    """
    try:
        researches = research_service.search_researches(
            db=db,
            primary_item=primary_item,
            secondary_item=secondary_item,
        )
        
        research_items = [
            ResearchSearchItem(
                id=research.id,
                primary_item=research.primary_item,
                secondary_item=research.secondary_item,
            )
            for research in researches
        ]
        
        return ResearchSearchResponse(researches=research_items)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search researches: {str(e)}",
        )

