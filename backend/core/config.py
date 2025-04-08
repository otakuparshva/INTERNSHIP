from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "AI Recruitment System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://your-production-domain.com"
    ]
    
    # Allowed Hosts
    ALLOWED_HOSTS: List[str] = [
        "localhost",
        "127.0.0.1",
        "your-production-domain.com"
    ]
    
    # Database
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "ai_recruitment"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    
    # AWS
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_BUCKET_NAME: str
    
    # AI Configuration
    OPENAI_API_KEY: str = ""  # Optional, can be empty
    HUGGINGFACE_API_KEY: str = ""
    HF_MODEL: str = ""
    OLLAMA_MODEL: str = ""
    USE_OLLAMA_AS_BACKUP: bool = False
    
    # Email
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: str
    SMTP_FROM_NAME: str
    
    # Admin Configuration
    ADMIN_EMAIL: str = ""
    ADMIN_PASSWORD: str = ""
    
    # Recruiter Configuration
    RECRUITER_EMAIL: str = ""
    RECRUITER_PASSWORD: str = ""
    RECRUITER_NAME: str = ""
    RECRUITER_COMPANY: str = ""
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    DEFAULT_RATE_LIMIT: int = 60  # requests per minute
    DEFAULT_BURST_SIZE: int = 10
    AUTH_RATE_LIMIT: int = 30
    AUTH_BURST_SIZE: int = 5
    ADMIN_RATE_LIMIT: int = 120
    ADMIN_BURST_SIZE: int = 20
    API_RATE_LIMIT: int = 100
    API_BURST_SIZE: int = 15
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Backup
    BACKUP_DIR: str = "backups"
    MAX_BACKUPS: int = 10
    BACKUP_RETENTION_DAYS: int = 30
    
    # Security Headers
    SECURITY_HEADERS: dict = {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings() 