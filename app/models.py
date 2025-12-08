from typing import List
from pydantic import BaseModel, Field, HttpUrl


class HypothesisValidationRequest(BaseModel):
    hypothesis: str = Field(..., description="The hypothesis to validate against the article")
    article_url: HttpUrl = Field(..., description="URL of the article to validate")


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
    article_urls: List[HttpUrl] = Field(
        ...,
        description="Array of article URLs to upload",
        min_length=1,
    )


class ArticleUploadResponse(BaseModel):
    uploaded_articles_amount: int = Field(
        ...,
        ge=0,
        description="Number of successfully uploaded articles",
    )
    failed_articles_amount: int = Field(
        ...,
        ge=0,
        description="Number of articles that failed to upload",
    )
    failed_articles: List[str] = Field(
        ...,
        description="List of URLs that failed to upload",
    )


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

