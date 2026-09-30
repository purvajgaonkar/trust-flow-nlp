"""
Trust Flow Configuration Management
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_NAME: str = "Trust Flow"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "*"]
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "*"]

    # Database
    DATABASE_URL: str = "sqlite:///./ai_shield.db"

    # Security
    MAX_INPUT_LENGTH: int = 50000
    MAX_FILE_SIZE_MB: int = 10
    RATE_LIMIT_PER_MINUTE: int = 100

    # Risk Thresholds
    BLOCK_THRESHOLD: float = 0.80
    REVIEW_THRESHOLD: float = 0.50
    SEMANTIC_SIMILARITY_THRESHOLD: float = 0.70

    # Fusion Weights
    WEIGHT_RULE: float = 0.25
    WEIGHT_FUZZY: float = 0.20
    WEIGHT_OBFUSCATION: float = 0.20
    WEIGHT_SEMANTIC: float = 0.20
    WEIGHT_TRANSFORMER: float = 0.15
    WEIGHT_LANGUAGE: float = 0.10

    # Models
    SPACY_MODEL: str = "en_core_web_sm"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    TRANSFORMER_MODEL: str = "bert-base-uncased"
    NLI_MODEL: str = "cross-encoder/nli-deberta-v3-small"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
