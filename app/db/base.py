from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings, SettingsConfigDict

Base = declarative_base()


class DatabaseConfig(BaseSettings):
    database_url: str = "postgresql://eureka_user:eureka_password@localhost:5432/eureka_db"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


def get_database_url() -> str:
    """Get database URL from environment variables."""
    config = DatabaseConfig()
    return config.database_url


def create_db_engine(database_url: str = None):
    """Create SQLAlchemy engine."""
    if database_url is None:
        database_url = get_database_url()
    return create_engine(database_url, pool_pre_ping=True)


def get_session_factory(engine=None):
    """Get session factory."""
    if engine is None:
        engine = create_db_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Global engine and session factory
_engine = None
_session_factory = None


def init_db():
    """Initialize database connection."""
    global _engine, _session_factory
    if _engine is None:
        _engine = create_db_engine()
        _session_factory = get_session_factory(_engine)
    return _engine, _session_factory


def get_db():
    """Dependency for getting database session."""
    _, session_factory = init_db()
    session = session_factory()
    try:
        yield session
    finally:
        session.close()

