from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # AWS Configuration
    AWS_REGION: str = Field(default="us-east-1", env="AWS_REGION")
    AWS_PROFILE: str = Field(default="default", env="AWS_PROFILE")
    AWS_ACCESS_KEY_ID: str = Field(default="", env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = Field(default="", env="AWS_SECRET_ACCESS_KEY")
    
    # Ollama Configuration
    OLLAMA_HOST: str = Field(default="http://localhost:11434", env="OLLAMA_HOST")
    OLLAMA_MODEL: str = Field(default="llama3.2:latest", env="OLLAMA_MODEL")
    
    # Database Configuration
    USE_DATABASE: bool = Field(default=True, env="USE_DATABASE")
    DATABASE_URL: str = Field(default="sqlite:///./costsense.db", env="DATABASE_URL")
    POSTGRES_URL: str = Field(default="postgresql://postgres:password@localhost:5432/costoptimization", env="POSTGRES_URL")
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # API Configuration
    BACKEND_URL: str = Field(default="http://localhost:8000", env="BACKEND_URL")
    FRONTEND_URL: str = Field(default="http://localhost:3000", env="FRONTEND_URL")
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000"], env="CORS_ORIGINS")
    
    # Security
    SECRET_KEY: str = Field(default="your-super-secret-key-change-this-in-production", env="SECRET_KEY")
    ENCRYPTION_KEY: str = Field(default="your-encryption-key-for-sensitive-data", env="ENCRYPTION_KEY")
    
    # Strands Agents Configuration
    STRANDS_MODEL_PROVIDER: str = Field(default="ollama", env="STRANDS_MODEL_PROVIDER")
    STRANDS_DEFAULT_MODEL: str = Field(default="llama2", env="STRANDS_DEFAULT_MODEL")
    STRANDS_SESSION_STORAGE: str = Field(default="postgresql", env="STRANDS_SESSION_STORAGE")
    
    # Application Settings
    DEBUG: bool = Field(default=True, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    MAX_CONCURRENT_AGENTS: int = Field(default=5, env="MAX_CONCURRENT_AGENTS")
    AGENT_TIMEOUT: int = Field(default=300, env="AGENT_TIMEOUT")
    CACHE_EXPIRY_HOURS: int = Field(default=24, env="CACHE_EXPIRY_HOURS")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }