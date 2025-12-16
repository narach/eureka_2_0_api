from typing import List
from pydantic import BaseModel, Field, HttpUrl


class HypothesisValidationRequest(BaseModel):
    hypothesis: str = Field(..., description="The hypothesis to validate against the article")
    article_url: HttpUrl = Field(..., description="URL of the article to validate")


class HypothesisValidationByArticleIdRequest(BaseModel):
    hypothesis: str = Field(..., description="The hypothesis to validate against the article")
    article_id: int = Field(..., description="ID of the article to validate")


class AnalyticsResult(BaseModel):
    relevancy: float = Field(
        ...,
        ge=0,
        le=100,
        description="Relevancy score (0-100%) reflecting how relevant the article is to the hypothesis",
    )
    key_take: str = Field(
        ...,
        description="2-3 sentence summary about validation results",
        min_length=10,
    )
    validity: float = Field(
        ...,
        ge=0,
        le=100,
        description="Validity score (0-100%) reflecting how much the article confirms or refutes the hypothesis",
    )


class HypothesisValidationResponse(BaseModel):
    result: AnalyticsResult


class ArticleUploadRequest(BaseModel):
    url: str = Field(..., description="Article URL")
    title: str | None = Field(default=None, description="Article title")
    topic: str | None = Field(
        default=None,
        description="Topic in format 'main_item - secondary_item'. If provided, main_item and secondary_item will be populated automatically.",
    )
    main_item: str | None = Field(
        default=None,
        description="Main item. If provided along with secondary_item, topic will be populated automatically.",
    )
    secondary_item: str | None = Field(
        default=None,
        description="Secondary item. If provided along with main_item, topic will be populated automatically.",
    )


class ArticleUploadResponse(BaseModel):
    id: int = Field(..., description="ID of the uploaded article")
    url: str = Field(..., description="Article URL")
    title: str | None = Field(default=None, description="Article title")
    topic: str | None = Field(default=None, description="Article topic")
    main_item: str | None = Field(default=None, description="Main item")
    secondary_item: str | None = Field(default=None, description="Secondary item")
    message: str = Field(..., description="Status message")


class HypothesisCreationRequest(BaseModel):
    hypothesis: str = Field(
        ...,
        description="The hypothesis to create and validate",
        min_length=1,
    )
    articles_amount: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Number of articles to search for (default: 10, max: 50)",
    )


class ValidationResultItem(BaseModel):
    article: str = Field(..., description="Article URL")
    relevancy: float = Field(..., ge=0, le=100, description="Relevancy score (0-100)")
    key_take: str = Field(..., description="Key takeaway from validation")
    validity: float = Field(..., ge=0, le=100, description="Validity score (0-100)")


class HypothesisCreationResponse(BaseModel):
    validation_results: List[ValidationResultItem] = Field(
        ...,
        description="List of validation results for each successfully processed article",
    )
    failed_articles_amount: int = Field(
        ...,
        ge=0,
        description="Number of articles that failed to process or validate",
    )
    failed_articles: List[str] = Field(
        ...,
        description="List of URLs that failed to process or validate",
    )


class ArticleListItem(BaseModel):
    id: int = Field(..., description="Article ID")
    title: str = Field(..., description="Article title")
    url: str = Field(..., description="Article URL")
    topic: str | None = Field(default=None, description="Article topic")
    main_item: str | None = Field(default=None, description="Main item")
    secondary_item: str | None = Field(default=None, description="Secondary item")


class ArticleListResponse(BaseModel):
    articles: List[ArticleListItem] = Field(
        ...,
        description="List of all available articles (without content)",
    )


class ArticleBatchUploadResponse(BaseModel):
    uploaded_articles: int = Field(
        ...,
        ge=0,
        description="Number of successfully uploaded articles",
    )
    failed_articles: int = Field(
        ...,
        ge=0,
        description="Number of articles that failed to upload",
    )


class ArticleSearchItem(BaseModel):
    id: int = Field(..., description="Article ID")
    title: str = Field(..., description="Article title")
    url: str = Field(..., description="Article URL")
    topic: str | None = Field(default=None, description="Article topic")
    research_id: int | None = Field(default=None, description="Research ID")


class ArticleSearchResponse(BaseModel):
    articles: List[ArticleSearchItem] = Field(
        ...,
        description="List of articles matching the search criteria",
    )


class EntityTypeItem(BaseModel):
    id: int = Field(..., description="Entity type ID")
    name: str = Field(..., description="Entity type name")


class EntityTypeListResponse(BaseModel):
    entity_types: List[EntityTypeItem] = Field(
        ...,
        description="List of all available entity types",
    )


class ResearchItem(BaseModel):
    id: int = Field(..., description="Research ID")
    primary_item: str = Field(..., description="Primary item")
    secondary_item: str = Field(..., description="Secondary item")


class ResearchListResponse(BaseModel):
    researches: List[ResearchItem] = Field(
        ...,
        description="List of all available researches",
    )


class ResearchSearchItem(BaseModel):
    id: int = Field(..., description="Research ID")
    primary_item: str = Field(..., description="Primary item")
    secondary_item: str = Field(..., description="Secondary item")


class ResearchSearchResponse(BaseModel):
    researches: List[ResearchSearchItem] = Field(
        ...,
        description="List of researches matching the search criteria",
    )