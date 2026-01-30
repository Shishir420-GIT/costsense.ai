from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database - Supports both PostgreSQL and Azure Cosmos DB for PostgreSQL
    # Standard PostgreSQL: postgresql://user:pass@localhost:5432/dbname
    # Azure Cosmos DB: postgresql://username:password@server.postgres.cosmos.azure.com:5432/citus?sslmode=require
    database_url: str = "postgresql://costsense:costsense@localhost:5432/costsense"

    # Database connection pool settings (adjust for production)
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_pre_ping: bool = True

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b-instruct"
    ollama_timeout: int = 120
    ollama_max_retries: int = 3

    # Application
    log_level: str = "INFO"
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    # AWS
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"

    # Azure
    azure_tenant_id: str = ""
    azure_client_id: str = ""
    azure_client_secret: str = ""
    azure_subscription_id: str = ""

    # GCP
    google_application_credentials: str = ""
    gcp_project_id: str = ""

    # ServiceNow
    servicenow_instance: str = ""
    servicenow_username: str = ""
    servicenow_password: str = ""

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]


settings = Settings()
