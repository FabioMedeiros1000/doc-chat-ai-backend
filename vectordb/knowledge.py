from functools import lru_cache

from agno.knowledge.knowledge import Knowledge

from vectordb.connection import get_vector_db


def _normalize_userHash(userHash: str | None) -> str | None:
    if userHash and userHash.strip():
        return userHash.strip()
    return None


@lru_cache(maxsize=None)
def get_knowledge(userHash: str | None = None) -> Knowledge | None:
    normalized = _normalize_userHash(userHash)
    if normalized:
        return Knowledge(
            name=userHash,
            description=(
                f"Vector store do usuário com a hash {userHash}"
            ),
            vector_db=get_vector_db(userHash=normalized),
        )
    
    return None
