import logging
from fastapi import FastAPI
from app.routers import validation, articles, hypotheses, entity_types, researches

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title="Eureka 2.0 API",
    description="Backend API for validating life science articles against hypotheses",
    version="0.1.0",
)

app.include_router(validation.router, prefix="/api/v1", tags=["validation"])
app.include_router(articles.router, prefix="/api/v1/articles", tags=["articles"])
app.include_router(hypotheses.router, prefix="/api/v1/hypotheses", tags=["hypotheses"])
app.include_router(entity_types.router, prefix="/api/v1/entity_types", tags=["entity_types"])
app.include_router(researches.router, prefix="/api/v1/researches", tags=["researches"])


@app.get("/")
async def root():
    return {"message": "Eureka 2.0 API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

