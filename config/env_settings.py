from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """
    Configurações gerais do projeto — centralização de variáveis de ambiente.
    """
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    QDRANT_URL: str = Field(..., env="QDRANT_URL")
    LLM_TTL_HOURS: int = Field(..., env="LLM_TTL_HOURS")
    API_PORT: int = Field(..., env="API_PORT")
    MYSQL_HOST: str = Field(..., env="MYSQL_HOST")
    MYSQL_PORT: int = Field(..., env="MYSQL_PORT")
    MYSQL_DATABASE: str = Field(..., env="MYSQL_DATABASE")
    MYSQL_USER: str = Field(..., env="MYSQL_USER")
    MYSQL_PASSWORD: str = Field(..., env="MYSQL_PASSWORD")
    MYSQL_ROOT_PASSWORD: str = Field(..., env="MYSQL_ROOT_PASSWORD")
    CELERY_BROKER_URL: str = Field(..., env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(..., env="CELERY_RESULT_BACKEND")
    USER_MAX_CHAT_TOKENS: int = Field(4000, env="USER_MAX_CHAT_TOKENS")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }

@lru_cache()
def get_settings() -> Settings:
    return Settings()
