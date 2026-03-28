from __future__ import annotations

from functools import lru_cache

from qdrant_client import QdrantClient

from config.env_settings import get_settings


class VectorDbClientFactory:
    def __init__(self, settings=None) -> None:
        self._settings = settings or get_settings()

    @lru_cache(maxsize=1)
    def get_client(self) -> QdrantClient:
        return QdrantClient(url=self._settings.QDRANT_URL)

    def collection_exists(self, client: QdrantClient, collection_name: str) -> bool:
        try:
            client.get_collection(collection_name=collection_name)
            return True
        except Exception as exc:
            status_code = getattr(exc, "status_code", None)
            if status_code == 404:
                return False
            message = str(exc).lower()
            if "not found" in message or "404" in message:
                return False
            raise
