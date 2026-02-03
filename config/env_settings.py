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
    FIRECRAWL_API_KEY: str = Field(..., env="FIRECRAWL_API_KEY")
    QDRANT_URL: str = Field(..., env="QDRANT_URL")
    LLM_TTL_HOURS: int = Field(..., env="LLM_TTL_HOURS")
    API_PORT: int = Field(..., env="API_PORT")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }

@lru_cache()
def get_settings() -> Settings:
    return Settings()
