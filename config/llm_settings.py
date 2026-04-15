from enum import Enum
from functools import lru_cache
from typing import Optional, Union

from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.models.openai import OpenAIChat

from config.env_settings import get_settings


settings = get_settings()
TTL_HOURS = settings.LLM_TTL_HOURS * 60 * 60


class LLMModel(str, Enum):
    SMALL = "gpt-5-nano"
    MEDIUM = "gpt-4o-mini"
    EMBEDDING = "text-embedding-3-small"


def _create_llm(model: LLMModel, api_key: Optional[str] = None) -> Union[OpenAIChat, OpenAIEmbedder]:
    if model == LLMModel.EMBEDDING:
        return OpenAIEmbedder(
            id=model.value,
            api_key=api_key,
        )

    return OpenAIChat(
        id=model.value,
        cache_response=api_key is None,
        cache_ttl=TTL_HOURS,
        api_key=api_key,
    )


@lru_cache(maxsize=None)
def _get_default_llm(model: LLMModel) -> Union[OpenAIChat, OpenAIEmbedder]:
    return _create_llm(model=model)


def get_llm(model: LLMModel, api_key: Optional[str] = None) -> Union[OpenAIChat, OpenAIEmbedder]:
    if api_key:
        return _create_llm(model=model, api_key=api_key)
    return _get_default_llm(model=model)
