from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from app.db.models import Hypothesis, Article, ValidationResult


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
    def create(db: Session, title: Optional[str], url: str, content: str) -> Article:
        """Create a new article."""
        article = Article(title=title, url=url, content=content)
        db.add(article)
        try:
            db.commit()
            db.refresh(article)
            return article
        except IntegrityError:
            db.rollback()
            # If it already exists, return the existing one
            return ArticleRepository.get_by_url(db, url)


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

