from __future__ import annotations

from typing import Dict, List

from qdrant_client.http.models import FieldCondition, Filter, MatchValue
from sqlalchemy import select

from api.exceptions import AgentError
from db.models import IngestionJob
from db.session import get_session
from schemas.file_item import FileItem
from vectordb.client_factory import VectorDbClientFactory


class FileRepository:
    def __init__(self, client_factory: VectorDbClientFactory | None = None) -> None:
        self._client_factory = client_factory or VectorDbClientFactory()

    def list_files_for_user(self, user_hash: str) -> List[FileItem]:
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

    def delete_file_for_user(self, user_hash: str, content_hash: str) -> None:
        if not user_hash or not user_hash.strip():
            raise AgentError("userHash is required.")
        if not content_hash or not content_hash.strip():
            raise AgentError("content_hash is required.")

        client = self._client_factory.get_client()
        collection_name = user_hash.strip()

        try:
            if not self._client_factory.collection_exists(client, collection_name):
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
