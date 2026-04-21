from __future__ import annotations

from typing import Optional, Sequence

from qdrant_client.http.models import Distance

from config.env_settings import get_settings
from config.llm_settings import LLMModel, get_llm
from vectordb.filtered_qdrant import FilteredQdrant


class VectorDbConnection:
    def __init__(self, settings=None) -> None:
        self._settings = settings or get_settings()

    def get_vector_db(
        self,
        userHash: str,
        api_key: Optional[str] = None,
        document_ids: Optional[Sequence[str]] = None,
    ) -> FilteredQdrant:
        default_filters = {"meta_data.hash": list(document_ids)} if document_ids else None
        return FilteredQdrant(
            collection=userHash,
            url=self._settings.QDRANT_URL,
            embedder=get_llm(LLMModel.EMBEDDING, api_key=api_key),
            distance=Distance.COSINE,
            default_filters=default_filters,
        )
