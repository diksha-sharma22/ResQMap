from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # pydantic-settings v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Prevent extra_forbidden on unknown env keys
    )

    # Application
    APP_NAME: str = "ResQMap"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = ""

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # HERE API
    HERE_API_KEY: str = ""
    HERE_BASE_URL: str = "https://weather.cc.api.here.com/weather/1.0"

    # Groq LLM
    GROQ_API_KEY: str = "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"
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    # AI Models
    MODEL_PATH: str = "./models"
    SATELLITE_MODEL: str = "satellite_DAMAGE_detection.h5"
    FLOOD_MODEL: str = "flood_detection.h5"



settings = Settings()
