import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    email_user: str = ""
    email_pass: str = ""
    
    # AI Configuration
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"

    # Google Sheets Configuration
    google_sheet_id: str = ""
    google_credentials_file: str = "credentials.json"

    # OAuth 2.0 Configuration
    google_client_id: str = ""
    google_client_secret: str = ""
    redirect_uri: str = "http://localhost:8000/api/auth/callback"
    frontend_url: str = "http://localhost:3000"
    
    # Security
    encryption_key: str = ""  # Used for encrypting stored tokens
    secret_key: str = "super-secret-key-for-jwt" # Change this in production

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
