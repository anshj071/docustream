from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "DocuStream"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = "postgresql://docustream_user:secretpassword@localhost:5432/docustream"

    # JWT Authentication Configuration
    SECRET_KEY: str = "super-secret-docustream-jwt-key-change-in-production-abcdef123456"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    class Config:
        env_file = ".env"

settings = Settings()
