# Eureka 2.0 API

Backend API for validating life science articles against hypotheses using LLM.

## Setup

1. Install Poetry if you haven't already:
   ```bash
   pip install poetry
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Start PostgreSQL database with Docker:
   ```bash
   docker-compose up -d
   ```

4. Create a `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```

5. Update `.env` with your configuration:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   OPENAI_MODEL=gpt-4o-mini
   DATABASE_URL=postgresql://eureka_user:eureka_password@localhost:5432/eureka_db
   ```

6. Run database migrations:
   ```bash
   poetry run alembic upgrade head
   ```

## Running the API

```bash
poetry run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

### POST `/api/v1/validate`

Validates a life science article against a hypothesis.

**Request Body:**
```json
{
  "hypothesis": "Your hypothesis here",
  "article_url": "https://example.com/article"
}
```

**Response:**
```json
{
  "result": {
    "relevancy": 85.5,
    "key_take": "The article discusses GLP-1 receptor mechanisms...",
    "validity": 92.0
  }
}
```

### POST `/api/v1/articles/upload`

Uploads multiple articles to the database. Parses article content and saves it for later validation.

**Request Body:**
```json
{
  "article_urls": [
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC12456317/",
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC7035886/"
  ]
}
```

**Response:**
```json
{
  "uploaded_articles_amount": 2,
  "failed_articles_amount": 0,
  "failed_articles": []
}
```

**Notes:**
- Duplicate URLs in the request are automatically deduplicated
- Articles that already exist in the database are counted as uploaded
- Failed articles are returned in the `failed_articles` array

### POST `/api/v1/hypotheses/create`

Creates a new hypothesis, searches for relevant PubMed articles, and validates the hypothesis against them.

**Request Body:**
```json
{
  "hypothesis": "Ozempic can be used to treat Type 2 Diabetes",
  "articles_amount": 3
}
```

**Response:**
```json
{
  "validation_results": [
    {
      "article": "https://pmc.ncbi.nlm.nih.gov/articles/PMC8859548/",
      "relevancy": 80,
      "key_take": "The article discusses GLP-1 receptor mechanisms...",
      "validity": 90
    }
  ],
  "failed_articles_amount": 1,
  "failed_articles": ["https://pmc.ncbi.nlm.nih.gov/articles/PMC12171229/"]
}
```

**Notes:**
- Searches for PubMed/PMC articles using LLM
- Automatically parses and saves articles to the database
- Validates hypothesis against each successfully loaded article
- `articles_amount` is configurable (default: 10, max: 50)
- All steps include debug-level logging

## Database

The API uses PostgreSQL with pgvector support (for future vectorization features). The database caches:
- **Articles**: Parsed article content to avoid re-parsing
- **Hypotheses**: Hypothesis titles for reuse
- **Validation Results**: Cached validation results for article+hypothesis combinations

### Database Schema

- **hypotheses**: Stores hypothesis titles
- **articles**: Stores article URLs, titles, and parsed content
- **validation_results**: Stores validation results linking hypotheses to articles

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── db/                   # Database layer
│   │   ├── __init__.py
│   │   ├── base.py          # Database connection and session management
│   │   ├── models.py         # SQLAlchemy models
│   │   └── repositories.py  # Database repository layer
│   ├── routers/
│   │   ├── __init__.py
│   │   └── validation.py    # Validation endpoint
│   └── services/
│       ├── __init__.py
│       ├── article_parser.py # Article content extraction
│       ├── llm_service.py   # LLM validation service
│       └── validation_service.py # Validation service with caching
├── alembic/                  # Database migrations
│   ├── versions/            # Migration files
│   ├── env.py
│   └── script.py.mako
├── docker-compose.yml        # PostgreSQL with pgvector
├── .env                     # Environment variables (create from .env.example)
├── .env.example
├── alembic.ini               # Alembic configuration
├── pyproject.toml
└── README.md
```

