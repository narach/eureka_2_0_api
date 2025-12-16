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
    url = Column(String, nullable=False, index=True)  # Removed unique constraint - same URL can exist with different research_id
    content = Column(Text, nullable=False)
    topic = Column(String, nullable=True)
    main_item = Column(String, nullable=True)
    secondary_item = Column(String, nullable=True)
    research_id = Column(Integer, ForeignKey("researches.id"), nullable=True, index=True)
    
    # Relationships
    validation_results = relationship("ValidationResult", back_populates="article")
    research = relationship("Research", backref="articles")


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


class EntityType(Base):
    __tablename__ = "entity_types"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True, index=True)
    
    # Relationships
    diseases = relationship("Disease", back_populates="entity_type_rel")
    targets = relationship("Target", back_populates="entity_type_rel")
    drugs = relationship("Drug", back_populates="entity_type_rel")
    effects = relationship("Effect", back_populates="entity_type_rel")


class Disease(Base):
    __tablename__ = "diseases"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True, index=True)
    entity_type_id = Column(Integer, ForeignKey("entity_types.id"), nullable=True, index=True)
    
    # Relationships
    entity_type_rel = relationship("EntityType", back_populates="diseases")
    targets = relationship("Target", back_populates="disease")


class Target(Base):
    __tablename__ = "targets"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True, index=True)
    entity_type_id = Column(Integer, ForeignKey("entity_types.id"), nullable=True, index=True)
    disease_id = Column(Integer, ForeignKey("diseases.id"), nullable=True, index=True)
    
    # Relationships
    entity_type_rel = relationship("EntityType", back_populates="targets")
    disease = relationship("Disease", back_populates="targets")


class Drug(Base):
    __tablename__ = "drugs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True, index=True)
    entity_type_id = Column(Integer, ForeignKey("entity_types.id"), nullable=True, index=True)
    
    # Relationships
    entity_type_rel = relationship("EntityType", back_populates="drugs")
    effects = relationship("Effect", back_populates="drug")


class Effect(Base):
    __tablename__ = "effects"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)
    entity_type_id = Column(Integer, ForeignKey("entity_types.id"), nullable=True, index=True)
    drug_id = Column(Integer, ForeignKey("drugs.id"), nullable=True, index=True)
    effect_type = Column(String, nullable=True)  # 'generic' or 'side'
    
    # Relationships
    entity_type_rel = relationship("EntityType", back_populates="effects")
    drug = relationship("Drug", back_populates="effects")


class Research(Base):
    __tablename__ = "researches"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    primary_item = Column(String, nullable=False)
    secondary_item = Column(String, nullable=False)

