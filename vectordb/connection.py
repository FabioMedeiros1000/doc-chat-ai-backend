from agno.vectordb.qdrant import Qdrant
from qdrant_client.http.models import Distance
from functools import lru_cache

from config.llm_settings import get_llm, LLMModel
from config.env_settings import get_settings

settings = get_settings()

@lru_cache(maxsize=None)
def get_vector_db(collection_name: str) -> Qdrant:
    return Qdrant(
        collection=collection_name,
        url=settings.QDRANT_URL,
        embedder=get_llm(LLMModel.EMBEDDING),
        distance=Distance.COSINE,
    )
