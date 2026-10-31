"""Configuration, environment variables , and model client setup"""

from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BITEHARBOR_", env_file=".env", extra="ignore")

    openai_api_key: SecretStr | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"
    data_dir: Path = Path(".biteharbor")
    timeout_seconds: float = Field(default=30, gt=0, le=120)
    max_tool_iterations: int = Field(default=5, ge=1, le=10)


settings = Settings()


def get_llm(temperature: float = 0.0):
    """Return an initialized ChatOpenAI instance."""
    from langchain_openai import ChatOpenAI

    api_key = settings.openai_api_key.get_secret_value() if settings.openai_api_key else None
    return ChatOpenAI(
        model=settings.model,
        api_key=api_key,
        temperature=temperature,
        timeout=settings.timeout_seconds,
        max_retries=2,
    )


def get_embeddings():
    """Return an initialized OpenAIEmbeddings instance."""
    from langchain_openai import OpenAIEmbeddings

    api_key = settings.openai_api_key.get_secret_value() if settings.openai_api_key else None
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=api_key,
        request_timeout=settings.timeout_seconds,
        max_retries=2,
    )
