from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "DocuStream"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = "postgresql://docustream_user:secretpassword@localhost:5432/docustream"

    # JWT
    SECRET_KEY: str = "super-secret-docustream-jwt-key-change-in-production-abcdef123456"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Google Gemini API
    GEMINI_API_KEY: str = ""
    EMBEDDING_MODEL: str = "text-embedding-004"
    EMBEDDING_DIMENSIONS: int = 768
    LLM_MODEL: str = "gemini-1.5-flash"

    # Backward compatibility / fallback
    OPENAI_API_KEY: str = ""

    # Upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 50

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
