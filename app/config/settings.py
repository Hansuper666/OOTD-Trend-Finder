import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "OOTD Trend Finder"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "Find trendy outfit of the day images based on your preferences"
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    PINTEREST_API_KEY: str = os.getenv("PINTEREST_API_KEY", "")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ootd.db")
    
    # Paths
    IMAGE_STORAGE_PATH: str = os.getenv("IMAGE_STORAGE_PATH", "./app/static/images")
    UPLOAD_PATH: str = os.getenv("UPLOAD_PATH", "./app/static/uploads")
    
    # AI Settings
    EMBEDDING_MODEL: str = "openai/clip-vit-base-patch32"
    TEXT_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    SIMILARITY_THRESHOLD: float = 0.1
    MAX_IMAGES_TO_RETURN: int = 10
    
    # Pinterest settings
    PINTEREST_SEARCH_LIMIT: int = 50
    PINTEREST_SEARCH_TERM: str = "outfit of the day"
    
    class Config:
        env_file = ".env"

settings = Settings() 