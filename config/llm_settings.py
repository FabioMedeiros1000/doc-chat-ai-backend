from functools import lru_cache
from enum import Enum
from typing import Union

from agno.models.openai import OpenAIChat
from agno.knowledge.embedder.openai import OpenAIEmbedder
from config.env_settings import get_settings


settings = get_settings()   
TTL_HOURS = settings.LLM_TTL_HOURS * 60 * 60        

class LLMModel(str, Enum):
    SMALL = "gpt-5-nano"                  
    MEDIUM = "gpt-4o-mini"                
    EMBEDDING = "text-embedding-3-small"  


@lru_cache(maxsize=None)
def get_llm(model: LLMModel) -> Union[OpenAIChat, OpenAIEmbedder]:
    """
    Retorna uma instância única por modelo (cacheada).
    """

    if model == LLMModel.EMBEDDING:
        return OpenAIEmbedder(id=model.value)

    return OpenAIChat(
        id=model.value,
        cache_response=True,
        cache_ttl=TTL_HOURS
    )
