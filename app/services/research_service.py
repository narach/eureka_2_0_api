from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.repositories import ResearchRepository
from app.db.models import Research


class ResearchService:
    """Service for handling research operations."""
    
    @staticmethod
    def get_all_researches(db: Session) -> List[Research]:
        """
        Get all researches from the database.
        
        Args:
            db: Database session
            
        Returns:
            List of all researches
        """
        return ResearchRepository.get_all(db)
    
    @staticmethod
    def search_researches(
        db: Session,
        primary_item: Optional[str] = None,
        secondary_item: Optional[str] = None,
    ) -> List[Research]:
        """
        Search researches by primary_item and/or secondary_item.
        
        Args:
            db: Database session
            primary_item: Filter by primary_item
            secondary_item: Filter by secondary_item
            
        Returns:
            List of researches matching the criteria
        """
        return ResearchRepository.search(
            db=db,
            primary_item=primary_item,
            secondary_item=secondary_item,
        )

