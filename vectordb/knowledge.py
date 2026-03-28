from __future__ import annotations

from functools import lru_cache

from agno.knowledge.knowledge import Knowledge

from vectordb.connection import VectorDbConnection


class KnowledgeProvider:
    def __init__(self, vector_db_connection: VectorDbConnection | None = None) -> None:
        self._vector_db_connection = vector_db_connection or VectorDbConnection()

    def _normalize_user_hash(self, user_hash: str | None) -> str | None:
        if user_hash and user_hash.strip():
            return user_hash.strip()
        return None

    def get_knowledge(self, userHash: str | None = None) -> Knowledge | None:
        normalized = self._normalize_user_hash(userHash)
        if normalized:
            return Knowledge(
                name=userHash,
                description=f"Vector store do usuario com a hash {userHash}",
                vector_db=self._vector_db_connection.get_vector_db(userHash=normalized),
            )
        return None
