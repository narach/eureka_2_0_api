from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from app.db.models import Hypothesis, Article, ValidationResult, EntityType, Research


class HypothesisRepository:
    """Repository for Hypothesis operations."""
    
    @staticmethod
    def get_by_title(db: Session, title: str) -> Optional[Hypothesis]:
        """Get hypothesis by title."""
        return db.query(Hypothesis).filter(Hypothesis.title == title).first()
    
    @staticmethod
    def get_by_id(db: Session, hypothesis_id: int) -> Optional[Hypothesis]:
        """Get hypothesis by ID."""
        return db.query(Hypothesis).filter(Hypothesis.id == hypothesis_id).first()
    
    @staticmethod
    def create(db: Session, title: str) -> Hypothesis:
        """Create a new hypothesis."""
        hypothesis = Hypothesis(title=title)
        db.add(hypothesis)
        try:
            db.commit()
            db.refresh(hypothesis)
            return hypothesis
        except IntegrityError:
            db.rollback()
            # If it already exists, return the existing one
            return HypothesisRepository.get_by_title(db, title)


class ArticleRepository:
    """Repository for Article operations."""
    
    @staticmethod
    def get_by_url(db: Session, url: str) -> Optional[Article]:
        """Get article by URL."""
        return db.query(Article).filter(Article.url == url).first()
    
    @staticmethod
    def get_by_id(db: Session, article_id: int) -> Optional[Article]:
        """Get article by ID."""
        return db.query(Article).filter(Article.id == article_id).first()
    
    @staticmethod
    def get_by_research_id(db: Session, research_id: int) -> List[Article]:
        """
        Get all articles by research_id.
        
        Args:
            db: Database session
            research_id: Research ID
            
        Returns:
            List of articles with the specified research_id
        """
        return db.query(Article).filter(Article.research_id == research_id).order_by(Article.id).all()
    
    @staticmethod
    def get_by_url_and_research(db: Session, url: str, research_id: Optional[int] = None) -> Optional[Article]:
        """
        Get article by URL and research_id.
        Handles NULL research_id properly (NULL != NULL in SQL).
        
        Args:
            db: Database session
            url: Article URL
            research_id: Research ID (can be None)
            
        Returns:
            Article if found, None otherwise
        """
        query = db.query(Article).filter(Article.url == url)
        
        if research_id is None:
            # Check for articles with NULL research_id
            query = query.filter(Article.research_id.is_(None))
        else:
            # Check for articles with specific research_id
            query = query.filter(Article.research_id == research_id)
        
        return query.first()
    
    @staticmethod
    def _process_topic_fields(
        topic: Optional[str] = None,
        main_item: Optional[str] = None,
        secondary_item: Optional[str] = None,
    ) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Process topic, main_item, and secondary_item fields.
        
        Logic:
        - If topic is provided, split it by "-" to populate main_item and secondary_item (removing trailing spaces)
        - If main_item and secondary_item are provided (and topic is not), concatenate them to populate topic
        - Topic takes precedence: if topic is provided, it will override main_item/secondary_item
        
        Returns:
            Tuple of (topic, main_item, secondary_item) with all fields populated
        """
        processed_topic = topic
        processed_main_item = main_item
        processed_secondary_item = secondary_item
        
        # If topic is provided, split it to populate main_item and secondary_item
        # Topic takes precedence over individually provided main_item/secondary_item
        if processed_topic:
            parts = [part.strip() for part in processed_topic.split("-", 1)]
            if len(parts) == 2:
                processed_main_item = parts[0].strip() if parts[0] else None
                processed_secondary_item = parts[1].strip() if parts[1] else None
            elif len(parts) == 1 and parts[0]:
                # Only one part, treat as main_item only
                processed_main_item = parts[0].strip()
                processed_secondary_item = None
        
        # If topic was not provided but main_item and secondary_item are, populate topic
        if not processed_topic and processed_main_item and processed_secondary_item:
            processed_topic = f"{processed_main_item} - {processed_secondary_item}"
        
        return processed_topic, processed_main_item, processed_secondary_item
    
    @staticmethod
    def create(
        db: Session,
        title: Optional[str],
        url: str,
        content: str,
        topic: Optional[str] = None,
        main_item: Optional[str] = None,
        secondary_item: Optional[str] = None,
        research_id: Optional[int] = None,
    ) -> Article:
        """Create a new article."""
        # Process topic fields
        processed_topic, processed_main_item, processed_secondary_item = (
            ArticleRepository._process_topic_fields(topic, main_item, secondary_item)
        )
        
        article = Article(
            title=title,
            url=url,
            content=content,
            topic=processed_topic,
            main_item=processed_main_item,
            secondary_item=processed_secondary_item,
            research_id=research_id,
        )
        db.add(article)
        try:
            db.commit()
            db.refresh(article)
            return article
        except IntegrityError:
            db.rollback()
            # If it already exists, return the existing one by URL and research_id
            return ArticleRepository.get_by_url_and_research(db, url, research_id)


class ValidationResultRepository:
    """Repository for ValidationResult operations."""
    
    @staticmethod
    def get_by_hypothesis_and_article(
        db: Session, hypothesis_id: int, article_id: int
    ) -> Optional[ValidationResult]:
        """Get validation result by hypothesis and article."""
        return (
            db.query(ValidationResult)
            .filter(
                ValidationResult.hypothesis_id == hypothesis_id,
                ValidationResult.article_id == article_id,
            )
            .first()
        )
    
    @staticmethod
    def create(
        db: Session,
        hypothesis_id: int,
        article_id: int,
        relevancy: float,
        key_take: str,
        validity: float,
    ) -> ValidationResult:
        """Create a new validation result."""
        result = ValidationResult(
            hypothesis_id=hypothesis_id,
            article_id=article_id,
            relevancy=relevancy,
            key_take=key_take,
            validity=validity,
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        return result


class EntityTypeRepository:
    """Repository for EntityType operations."""
    
    @staticmethod
    def get_all(db: Session) -> List[EntityType]:
        """Get all entity types."""
        return db.query(EntityType).order_by(EntityType.id).all()
    
    @staticmethod
    def get_by_id(db: Session, entity_type_id: int) -> Optional[EntityType]:
        """Get entity type by ID."""
        return db.query(EntityType).filter(EntityType.id == entity_type_id).first()
    
    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[EntityType]:
        """Get entity type by name."""
        return db.query(EntityType).filter(EntityType.name == name).first()


class ResearchRepository:
    """Repository for Research operations."""
    
    @staticmethod
    def get_all(db: Session) -> List[Research]:
        """Get all researches."""
        return db.query(Research).order_by(Research.id).all()
    
    @staticmethod
    def get_by_id(db: Session, research_id: int) -> Optional[Research]:
        """Get research by ID."""
        return db.query(Research).filter(Research.id == research_id).first()
    
    @staticmethod
    def search(
        db: Session,
        primary_item: Optional[str] = None,
        secondary_item: Optional[str] = None,
    ) -> List[Research]:
        """
        Search researches by primary_item and/or secondary_item.
        
        Args:
            db: Database session
            primary_item: Filter by primary_item (optional)
            secondary_item: Filter by secondary_item (optional)
            
        Returns:
            List of researches matching the criteria
        """
        query = db.query(Research)
        
        if primary_item is not None:
            query = query.filter(Research.primary_item == primary_item)
        
        if secondary_item is not None:
            query = query.filter(Research.secondary_item == secondary_item)
        
        return query.order_by(Research.id).all()

