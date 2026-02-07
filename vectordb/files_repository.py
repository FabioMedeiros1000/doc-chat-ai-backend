from functools import lru_cache
from typing import Dict, List, Optional

from qdrant_client import QdrantClient
from api.exceptions import AgentError
from config.env_settings import get_settings
from schemas.file_item import FileItem

settings = get_settings()


@lru_cache(maxsize=1)
def _get_client() -> QdrantClient:
    return QdrantClient(url=settings.QDRANT_URL)


def _dedupe_files(points: List[object]) -> List[FileItem]:
    files_by_hash: Dict[str, FileItem] = {}
    for point in points:
        payload = getattr(point, "payload", None) or {}
        file_hash = payload.get("hash") or str(getattr(point, "id", "") or "")
        if not file_hash:
            continue
        uploaded_at = (
            payload.get("uploaded_at")
            or payload.get("uploadedAt")
            or "1970-01-01T00:00:00Z"
        )
        existing = files_by_hash.get(file_hash)
        if existing and existing.uploadedAt >= uploaded_at:
            continue
        files_by_hash[file_hash] = FileItem(
            id=str(file_hash),
            name=str(payload.get("filename") or ""),
            size=int(payload.get("size") or 0),
            uploadedAt=uploaded_at,
            status=payload.get("status"),
        )
    files = list(files_by_hash.values())
    files.sort(key=lambda item: item.uploadedAt, reverse=True)
    return files


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

    client = _get_client()
    collection_name = user_hash.strip()

    try:
        if not _collection_exists(client, collection_name):
            return []
        points: List[object] = []
        offset: Optional[object] = None
        while True:
            batch, offset = client.scroll(
                collection_name=collection_name,
                scroll_filter=None,
                with_payload=True,
                with_vectors=False,
                limit=256,
                offset=offset,
            )
            if not batch:
                break
            points.extend(batch)
            if offset is None:
                break
        return _dedupe_files(points)
    except Exception as exc:
        raise AgentError(f"Error listing files for user: {str(exc)}") from exc
