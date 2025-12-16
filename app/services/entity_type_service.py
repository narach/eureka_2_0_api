from sqlalchemy.orm import Session
from typing import List
from app.db.repositories import EntityTypeRepository
from app.db.models import EntityType


class EntityTypeService:
    """Service for handling entity type operations."""
    
    @staticmethod
    def get_all_entity_types(db: Session) -> List[EntityType]:
        """
        Get all entity types from the database.
        
        Args:
            db: Database session
            
        Returns:
            List of all entity types
        """
        return EntityTypeRepository.get_all(db)

