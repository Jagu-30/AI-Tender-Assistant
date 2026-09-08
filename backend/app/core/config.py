import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Tender Assistant"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("JWT_SECRET", "super-secret-jwt-key-change-in-production-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database
    db_path: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "tender_assistant.db")).replace("\\", "/")
    DATABASE_URL: str = os.getenv("DATABASE_URL_OVERRIDE", f"sqlite+aiosqlite:///{db_path}")

    # API Keys & External Services
    SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock")

    # File Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./storage/uploads")
    MAX_FILE_SIZE_MB: int = 25

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

settings = Settings()
