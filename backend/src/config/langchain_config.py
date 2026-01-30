"""LangChain configuration for Azure Cost Optimization Platform"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class LangChainSettings(BaseSettings):
    """LangChain-specific configuration settings"""

    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:latest"
    OLLAMA_TEMPERATURE: float = 0.7
    OLLAMA_MAX_TOKENS: int = 2000
    OLLAMA_TIMEOUT: int = 120

    # LangChain Configuration
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_ENDPOINT: Optional[str] = None
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "costsense-azure"

    # Agent Configuration
    MAX_CONCURRENT_AGENTS: int = 5
    AGENT_TIMEOUT: int = 300
    AGENT_MAX_RETRIES: int = 3
    AGENT_VERBOSE: bool = True

    model_config = SettingsConfigDict(
        env_file=".env.azure",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache()
def get_langchain_settings() -> LangChainSettings:
    """Get cached LangChain settings instance"""
    return LangChainSettings()


def get_ollama_llm():
    """
    Get configured Ollama LLM instance

    Returns:
        Ollama: Configured Ollama LLM ready for use with LangChain
    """
    from langchain_community.llms import Ollama

    settings = get_langchain_settings()

    try:
        llm = Ollama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=settings.OLLAMA_TEMPERATURE,
            num_predict=settings.OLLAMA_MAX_TOKENS,
            timeout=settings.OLLAMA_TIMEOUT
        )
        logger.info(f"Ollama LLM initialized with model: {settings.OLLAMA_MODEL}")
        return llm
    except Exception as e:
        logger.error(f"Failed to initialize Ollama LLM: {e}")
        raise


def test_ollama_connection() -> bool:
    """
    Test Ollama connection and model availability

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        llm = get_ollama_llm()
        response = llm.invoke("Hello")
        logger.info("Ollama connection successful")
        return True
    except Exception as e:
        logger.error(f"Ollama connection failed: {e}")
        return False
