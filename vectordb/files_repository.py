from functools import lru_cache
from typing import Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http.models import FieldCondition, Filter, MatchValue
from sqlalchemy import select

from api.exceptions import AgentError
from config.env_settings import get_settings
from db.models import IngestionJob
from db.session import get_session
from schemas.file_item import FileItem

settings = get_settings()


@lru_cache(maxsize=1)
def _get_client() -> QdrantClient:
    return QdrantClient(url=settings.QDRANT_URL)


def _collection_exists(client: QdrantClient, collection_name: str) -> bool:
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


def list_files_for_user(user_hash: str) -> List[FileItem]:
    if not user_hash or not user_hash.strip():
        raise AgentError("userHash is required.")

    session = get_session()
    try:
        stmt = (
            select(IngestionJob)
            .where(IngestionJob.user_hash == user_hash.strip())
            .order_by(IngestionJob.updated_at.desc())
        )
        jobs = list(session.execute(stmt).scalars().all())
    finally:
        session.close()

    if not jobs:
        return []

    seen_hashes: Dict[str, bool] = {}
    items: List[FileItem] = []
    for job in jobs:
        if job.status == "ready" and job.content_hash:
            if seen_hashes.get(job.content_hash):
                continue
            seen_hashes[job.content_hash] = True
        items.append(
            FileItem(
                id=job.content_hash if job.status == "ready" else None,
                name=job.filename,
                status=job.status,
                job_id=job.job_id,
                error_message=job.error_message,
            )
        )
    return items


def delete_file_for_user(user_hash: str, content_hash: str) -> None:
    if not user_hash or not user_hash.strip():
        raise AgentError("userHash is required.")
    if not content_hash or not content_hash.strip():
        raise AgentError("content_hash is required.")

    client = _get_client()
    collection_name = user_hash.strip()

    try:
        if not _collection_exists(client, collection_name):
            return
        client.delete(
            collection_name=collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="meta_data.hash",
                        match=MatchValue(value=content_hash.strip()),
                    )
                ]
            ),
        )
    except Exception as exc:
        raise AgentError(f"Error deleting file for user: {str(exc)}") from exc
