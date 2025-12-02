"""
Application settings and configuration
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application configuration settings."""

    # Application settings
    app_name: str = "Chat Application"
    app_version: str = "0.1.0"
    debug: bool = True
    environment: str = "development"

    # API settings
    api_prefix: str = "/api/v1"
    api_title: str = "Chat Application API"
    api_description: str = "FastAPI Chat Application with Agent Pipeline"

    # Database settings
    database_url: str = "sqlite:///./my_database.db"
    echo_sql: bool = False

    # LLM settings
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    default_llm_provider: str = "openai"  # openai or anthropic
    default_model: str = "gpt-3.5-turbo"

    # Embedding settings
    embedding_provider: str = "openai"
    embedding_model: str = "text-embedding-3-small"

    # Authentication settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # LangGraph settings
    max_iterations: int = 10
    timeout: int = 300

    # File upload settings
    upload_directory: str = "./uploads"
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list = [".pdf", ".txt", ".doc", ".docx"]

    # Logging settings
    log_directory: str = "./logs"
    log_level: str = "INFO"

    # RAG settings
    devops_related_keywords: list = [
        "devops", "docker", "kubernetes", "ci/cd", "jenkins", "gitlab", 
        "github actions", "terraform", "ansible", "aws", "azure", "gcp",
        "deployment", "infrastructure", "monitoring", "logging", "cloud"
    ]

    # CORS settings
    cors_origins: list = ["http://localhost:3000", "http://localhost:8000"]
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]

    # Excluded routes from authentication
    # Note: registration is restricted to admin users, so remove register and root from excluded routes
    auth_excluded_routes: list = ["/health","/", "/api/v1/auth/login"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.log_directory, exist_ok=True)
os.makedirs(settings.upload_directory, exist_ok=True)
