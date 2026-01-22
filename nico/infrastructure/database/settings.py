"""Environment configuration and settings management."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError(
            "DATABASE_URL environment variable is required. "
            "Please create a .env file with your database connection string."
        )
    
    # Embedding Service
    EMBEDDING_SERVICE_URL: str | None = os.getenv("EMBEDDING_SERVICE_URL")
    EMBEDDING_FALLBACK_LOCAL: bool = os.getenv(
        "EMBEDDING_FALLBACK_LOCAL", "true"
    ).lower() == "true"
    
    # Ollama
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text:latest")
    
    # Optional AI provider API keys
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY")
    GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY")
    
    # Application
    APP_NAME: str = "Nico"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get the database connection URL.
        
        Returns:
            PostgreSQL connection string
        """
        return cls.DATABASE_URL


# Global settings instance
settings = Settings()
