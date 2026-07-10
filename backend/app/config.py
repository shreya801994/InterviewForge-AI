import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, model_validator
from typing import Optional

class Settings(BaseSettings):
    ENV: str = "development"

    # Database Configuration
    DATABASE_URL: Optional[str] = None
    
    # Security Configuration
    JWT_SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Gemini API Configuration
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    AI_MOCK_MODE: bool = False

    # CORS & Upload Configuration
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    MAX_PDF_SIZE_MB: int = 5

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @model_validator(mode="after")
    def validate_startup_config(self) -> "Settings":
        # Validate JWT secret presence and length
        if not self.JWT_SECRET_KEY or not self.JWT_SECRET_KEY.strip():
            raise ValueError("JWT_SECRET_KEY environment variable is required.")
        if len(self.JWT_SECRET_KEY) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long.")

        # In production mode, validate critical production dependencies
        if self.ENV == "production":
            if not self.DATABASE_URL or not self.DATABASE_URL.strip():
                raise ValueError("DATABASE_URL environment variable is required in production mode.")
            if not self.GEMINI_API_KEY or not self.GEMINI_API_KEY.strip():
                raise ValueError("GEMINI_API_KEY environment variable is required in production mode.")

        return self

    @property
    def JWT_SECRET(self) -> str:
        """Returns the secret key to maintain backwards compatibility with existing security code."""
        return self.JWT_SECRET_KEY or ""

    @property
    def get_db_url(self) -> str:
        """Returns the DATABASE_URL if provided, else falls back to local SQLite database."""
        if self.DATABASE_URL and self.DATABASE_URL.strip():
            # SQLAlchemy requires postgresql:// instead of postgres:// for some deployments (like Render/Supabase)
            url = self.DATABASE_URL
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            return url
        
        # Local SQLite DB path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, "interview_forge.db")
        return f"sqlite:///{db_path}"

settings = Settings()

