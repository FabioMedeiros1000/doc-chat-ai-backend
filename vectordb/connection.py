from __future__ import annotations

from agno.vectordb.qdrant import Qdrant
from qdrant_client.http.models import Distance

from config.env_settings import get_settings
from config.llm_settings import get_llm, LLMModel


class VectorDbConnection:
    def __init__(self, settings=None) -> None:
        self._settings = settings or get_settings()

    def get_vector_db(self, userHash: str) -> Qdrant:
        return Qdrant(
            collection=userHash,
            url=self._settings.QDRANT_URL,
            embedder=get_llm(LLMModel.EMBEDDING),
            distance=Distance.COSINE,
        )

