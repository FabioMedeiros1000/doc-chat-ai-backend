from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from api.exceptions import AgentError, UserStorageLimitError
from api.ingestion.constants import (
    ERROR_MAX_USER_STORAGE,
    ERROR_NO_TEXT,
    MAX_USER_STORAGE_BYTES,
    UPLOAD_QUEUED_MESSAGE,
)
from api.ingestion.dtos import UploadResult
from api.ingestion.hashers import ContentHasher
from api.ingestion.indexer import Indexer
from api.ingestion.job_store import JobStore
from api.ingestion.metadata import MetadataBuilder
from api.ingestion.storage import UploadStorage
from api.ingestion.text_extractors import TextExtractor
from api.ingestion.validators import UploadValidator


class UploadOrchestrator:
    def __init__(
        self,
        *,
        validator: UploadValidator | None = None,
        storage: UploadStorage | None = None,
        extractor: TextExtractor | None = None,
        hasher: ContentHasher | None = None,
        metadata_builder: MetadataBuilder | None = None,
        indexer: Indexer | None = None,
        job_store: JobStore | None = None,
    ) -> None:
        self._validator = validator or UploadValidator()
        self._storage = storage or UploadStorage()
        self._extractor = extractor or TextExtractor()
        self._hasher = hasher or ContentHasher()
        self._metadata_builder = metadata_builder or MetadataBuilder()
        self._indexer = indexer or Indexer()
        self._job_store = job_store or JobStore()

    async def enqueue_upload(
        self,
        file: UploadFile,
        user_hash: str,
        max_bytes: int = MAX_USER_STORAGE_BYTES,
    ) -> UploadResult:
        filename = file.filename or ""
        ext = self._validator.validate_extension(filename)
        tmp_info = await self._storage.save_stream(file, ext, max_bytes)

        metadata_hash = self._hasher.compute_metadata_hash(
            filename,
            file.content_type,
            tmp_info.size,
        )
        existing = self._job_store.find_job_by_metadata_hash(user_hash, metadata_hash)
        if existing:
            self._storage.cleanup_paths(tmp_info.path)
            status = existing.status if existing.status in ("queued", "processing") else "processing"
            return UploadResult(
                success=True,
                message="Arquivo ja enviado ou em processamento.",
                job_id=existing.job_id,
                status=status,
                is_existing=True,
            )

        total_size = self._job_store.get_total_size_for_user(user_hash)
        if total_size + tmp_info.size > max_bytes:
            self._storage.cleanup_paths(tmp_info.path)
            raise UserStorageLimitError(ERROR_MAX_USER_STORAGE)

        job = self._job_store.create_job(
            user_hash,
            filename,
            file.content_type,
            size=tmp_info.size,
            file_path=str(tmp_info.path),
            metadata_hash=metadata_hash,
        )

        return UploadResult(
            success=True,
            message=UPLOAD_QUEUED_MESSAGE,
            job_id=job.job_id,
            status=job.status,
            is_existing=False,
        )

    def process_upload_job(self, job_id: str, api_key: Optional[str] = None) -> None:
        job = self._job_store.get_job(job_id)
        if not job:
            return
        try:
            self._process_job(job, api_key=api_key)
        except Exception:
            return

    def _process_job(self, job, api_key: Optional[str] = None) -> None:
        file_path = job.file_path
        tmp_path: Path | None = None
        md_path: Path | None = None
        self._job_store.update_job(job.job_id, status="processing")
        try:
            tmp_path = Path(file_path)
            text = self._extractor.extract(tmp_path)
            if not text or not text.strip():
                raise AgentError(ERROR_NO_TEXT)

            content_hash = self._hasher.compute_text_hash(text)
            self._job_store.update_job(job.job_id, content_hash=content_hash)

            metadata = self._metadata_builder.build_metadata(
                job.filename,
                job.content_type,
                content_hash,
                job.user_hash,
                size=job.size,
            )
            md_path = self._storage.write_temp_markdown(text)

            try:
                asyncio.run(
                    self._indexer.index_markdown_file(
                        md_path,
                        content_hash,
                        metadata,
                        userHash=job.user_hash,
                        api_key=api_key,
                    )
                )
            except Exception as e:
                raise AgentError(f"Error during indexing: {str(e)}") from e

            self._job_store.update_job(job.job_id, status="ready")
        except AgentError as e:
            self._job_store.update_job(job.job_id, status="failed", error_message=str(e))
        except Exception as e:
            self._job_store.update_job(job.job_id, status="failed", error_message=str(e))
        finally:
            self._storage.cleanup_paths(tmp_path, md_path)
