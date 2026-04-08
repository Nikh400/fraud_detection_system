from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Security Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_ISSUER: str = "fraud-detection-api"
    JWT_AUDIENCE: str = "fraud-detection-clients"

    # CORS Strategy
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost", "http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
    
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

settings = Settings()  # type: ignore
