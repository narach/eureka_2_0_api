from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import EntityTypeListResponse, EntityTypeItem
from app.db.base import get_db
from app.services.entity_type_service import EntityTypeService

router = APIRouter()
entity_type_service = EntityTypeService()


@router.get("", response_model=EntityTypeListResponse)
def get_entity_types(
    db: Session = Depends(get_db),
):
    """
    Fetch all available entity types from the database.
    
    Returns a list of entity types with id and name.
    """
    try:
        entity_types = entity_type_service.get_all_entity_types(db)
        
        entity_type_items = [
            EntityTypeItem(
                id=entity_type.id,
                name=entity_type.name,
            )
            for entity_type in entity_types
        ]
        
        return EntityTypeListResponse(entity_types=entity_type_items)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch entity types: {str(e)}",
        )

