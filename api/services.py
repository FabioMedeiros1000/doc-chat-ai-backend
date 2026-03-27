from pathlib import Path

from fastapi import UploadFile
from agno.agent import RunOutput

from schemas.chat_request import ChatRequest
from schemas.chat_response import ChatResponse
from schemas.upload_response import UploadResponse
from schemas.delete_response import DeleteResponse
from schemas.file_item import FileItem
from api.exceptions import AgentError, UserStorageLimitError
from api.ingestion.constants import (
    ERROR_MAX_USER_STORAGE,
    ERROR_NO_TEXT,
    MAX_USER_STORAGE_BYTES,
    UPLOAD_QUEUED_MESSAGE,
    UPLOAD_SUCCESS_MESSAGE,
)
from api.ingestion.file_utils import (
    build_metadata,
    cleanup_paths,
    compute_metadata_hash,
    compute_text_hash,
    validate_extension,
    write_temp_markdown,
    write_upload_stream,
)
from api.ingestion.indexer import index_markdown_file
from api.ingestion.job_store import (
    create_job,
    delete_jobs_for_user,
    find_job_by_metadata_hash,
    get_job,
    get_total_size_for_user,
    update_job,
)
from api.ingestion.text_extractors import extract_text
from celery_app import celery_app
from vectordb.files_repository import list_files_for_user, delete_file_for_user

from agents.chat_responder import get_chat_responder_agent

from vectordb.knowledge import get_knowledge


class LeiService:
    def chat(self, payload: ChatRequest) -> ChatResponse:
        chat_responder = get_chat_responder_agent(knowledge=get_knowledge(payload.userHash))
        result: RunOutput = chat_responder.run(input=payload.question)

        return ChatResponse(answer=result.content)

    async def enqueue_upload(
        self,
        file: UploadFile,
        userHash: str | None = None,
    ) -> UploadResponse:
        if not userHash or not userHash.strip():
            raise AgentError("userHash is required.")
        normalized_user_hash = userHash.strip()

        filename = file.filename or ""
        ext = validate_extension(filename)
        tmp_path, size = await write_upload_stream(file, ext, MAX_USER_STORAGE_BYTES)

        metadata_hash = compute_metadata_hash(filename, file.content_type, size)
        existing = find_job_by_metadata_hash(normalized_user_hash, metadata_hash)
        if existing:
            cleanup_paths(tmp_path)
            return UploadResponse(
                success=True,
                message="Arquivo ja enviado ou em processamento.",
                job_id=existing.job_id,
                status=existing.status if existing.status in ("queued", "processing") else "processing",
            )

        total_size = get_total_size_for_user(normalized_user_hash)
        if total_size + size > MAX_USER_STORAGE_BYTES:
            cleanup_paths(tmp_path)
            raise UserStorageLimitError(ERROR_MAX_USER_STORAGE)

        job = create_job(
            normalized_user_hash,
            filename,
            file.content_type,
            size=size,
            file_path=str(tmp_path),
            metadata_hash=metadata_hash,
        )

        celery_app.send_task("process_upload", args=[job.job_id])

        return UploadResponse(
            success=True,
            message=UPLOAD_QUEUED_MESSAGE,
            job_id=job.job_id,
            status=job.status,
        )

    def process_upload_job(self, job_id: str) -> None:
        job = get_job(job_id)
        if not job:
            return
        try:
            self._process_upload_data_sync(job)
        except Exception:
            return

    def _process_upload_data_sync(self, job) -> None:
        file_path = job.file_path
        tmp_path = None
        md_path = None
        update_job(job.job_id, status="processing")
        try:
            tmp_path = Path(file_path)
            text = extract_text(tmp_path)
            if not text or not text.strip():
                raise AgentError(ERROR_NO_TEXT)
            content_hash = compute_text_hash(text)
            update_job(job.job_id, content_hash=content_hash)
            metadata = build_metadata(
                job.filename,
                job.content_type,
                content_hash,
                job.user_hash,
                size=job.size,
            )
            md_path = write_temp_markdown(text)
            try:
                import asyncio
                asyncio.run(
                    index_markdown_file(
                        md_path,
                        content_hash,
                        metadata,
                        userHash=job.user_hash,
                    )
                )
            except Exception as e:
                raise AgentError(f"Error during indexing: {str(e)}") from e
            update_job(job.job_id, status="ready")
        except AgentError as e:
            update_job(job.job_id, status="failed", error_message=str(e))
        except Exception as e:
            update_job(job.job_id, status="failed", error_message=str(e))
        finally:
            cleanup_paths(tmp_path, md_path)

    async def _process_upload_data(
        self,
        file_path: str,
        ext: str,
        filename: str,
        content_type: str | None,
        user_hash: str,
        job_id: str | None,
        size: int,
    ) -> None:
        tmp_path = None
        md_path = None
        if job_id:
            update_job(job_id, status="processing")
        try:
            tmp_path = Path(file_path)

            text = extract_text(tmp_path)
            if not text or not text.strip():
                raise AgentError(ERROR_NO_TEXT)

            content_hash = compute_text_hash(text)
            if job_id:
                update_job(job_id, content_hash=content_hash)
            metadata = build_metadata(
                filename,
                content_type,
                content_hash,
                user_hash,
                size=size,
            )
            md_path = write_temp_markdown(text)

            try:
                await index_markdown_file(
                    md_path,
                    content_hash,
                    metadata,
                    userHash=user_hash,
                )
            except Exception as e:
                raise AgentError(f"Error during indexing: {str(e)}") from e

            if job_id:
                update_job(job_id, status="ready")
        except AgentError as e:
            if job_id:
                update_job(job_id, status="failed", error_message=str(e))
                return
            raise
        except Exception as e:
            if job_id:
                update_job(job_id, status="failed", error_message=str(e))
                return
            raise AgentError(str(e)) from e
        finally:
            cleanup_paths(tmp_path, md_path)

    def list_files(self, userHash: str) -> list[FileItem]:
        return list_files_for_user(userHash)


    def delete_file(self, file_id: str, userHash: str) -> DeleteResponse:
        if not userHash or not userHash.strip():
            raise AgentError("userHash is required.")
        if not file_id or not file_id.strip():
            raise AgentError("file_id is required.")

        normalized_user_hash = userHash.strip()
        normalized_file_id = file_id.strip()
        content_hash = (
            normalized_file_id.replace("upload_", "", 1)
            if normalized_file_id.startswith("upload_")
            else normalized_file_id
        )

        delete_file_for_user(normalized_user_hash, content_hash)
        delete_jobs_for_user(normalized_user_hash, content_hash)

        return DeleteResponse(
            success=True,
            message="File deleted successfully.",
            content_hash=content_hash,
        )
