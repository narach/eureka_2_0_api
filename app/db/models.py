from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.base import Base


class Hypothesis(Base):
    __tablename__ = "hypotheses"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False, unique=True, index=True)
    
    # Relationships
    validation_results = relationship("ValidationResult", back_populates="hypothesis")


class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=True)
    url = Column(String, nullable=False, unique=True, index=True)
    content = Column(Text, nullable=False)
    
    # Relationships
    validation_results = relationship("ValidationResult", back_populates="article")


class ValidationResult(Base):
    __tablename__ = "validation_results"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hypothesis_id = Column(Integer, ForeignKey("hypotheses.id"), nullable=False, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False, index=True)
    relevancy = Column(Float, nullable=False)
    key_take = Column(Text, nullable=False)
    validity = Column(Float, nullable=False)
    
    # Relationships
    hypothesis = relationship("Hypothesis", back_populates="validation_results")
    article = relationship("Article", back_populates="validation_results")

