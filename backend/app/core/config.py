"""
Nur Scents Customer Success Agent - Configuration Settings
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""

    # Project
    PROJECT_NAME: str = "Nur Scents Customer Success Agent"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://nurscents.pk",
    ]

    # Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "nur_scents_db"
    POSTGRES_USER: str = "nur_scents_user"
    POSTGRES_PASSWORD: str = "nur_scents_pass"
    POSTGRES_SSL_MODE: str = "prefer"

    @property
    def DATABASE_URL(self) -> str:
        """Generate database URL"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_GROUP_ID: str = "nur_scents_agent_group"
    KAFKA_AUTO_OFFSET_RESET: str = "earliest"

    # Kafka Topics
    KAFKA_TOPIC_WHATSAPP_EVENTS: str = "whatsapp.events"
    KAFKA_TOPIC_EMAIL_EVENTS: str = "email.events"
    KAFKA_TOPIC_WEB_EVENTS: str = "web.events"
    KAFKA_TOPIC_ORDER_EVENTS: str = "orders.events"
    KAFKA_TOPIC_AGENT_EVENTS: str = "agent.events"
    KAFKA_TOPIC_ESCALATION_EVENTS: str = "escalations.events"

    # Gemini AI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: int = 1024

    # Twilio WhatsApp
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_NUMBER: str = ""
    TWILIO_PHONE_NUMBER: str = ""

    # Gmail API
    GMAIL_CREDENTIALS_PATH: str = ""
    GMAIL_TOKEN_PATH: str = ""
    GMAIL_SCOPES: str = "https://www.googleapis.com/auth/gmail.modify"
    GMAIL_WATCH_LABEL: str = "INBOX"

    # Owner/Business
    OWNER_NAME: str = "Ammar"
    OWNER_PHONE: str = "+92XXXXXXXXXX"
    OWNER_EMAIL: str = "ammar@nurscents.pk"
    OWNER_TIMEZONE: str = "Asia/Karachi"

    BUSINESS_NAME: str = "Nur Scents"
    BUSINESS_CURRENCY: str = "PKR"
    BUSINESS_LANGUAGE: str = "ur,en"
    BUSINESS_CITY: str = "Karachi"
    BUSINESS_COUNTRY: str = "Pakistan"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE_PATH: str = "./logs/app.log"
    LOG_ROTATION: int = 100  # MB
    LOG_RETENTION: int = 30  # days

    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    HEALTH_CHECK_INTERVAL: int = 30

    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE: int = 60
    MAX_ORDERS_PER_HOUR: int = 10
    SPAM_DETECTION_ENABLED: bool = True

    # Data Paths
    DATA_DIR: str = "./data"
    PRODUCTS_DATA_PATH: str = "./data/nur_scents_products.json"
    BUSINESS_RULES_PATH: str = "./data/business_rules.json"

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
