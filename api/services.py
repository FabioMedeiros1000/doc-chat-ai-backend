from fastapi import BackgroundTasks, UploadFile
from agno.agent import RunOutput

from schemas.chat_request import ChatRequest
from schemas.chat_response import ChatResponse
from schemas.upload_response import UploadResponse
from schemas.file_item import FileItem
from api.exceptions import AgentError, UserStorageLimitError
from api.ingestion.constants import (
    ERROR_FILE_TOO_LARGE,
    ERROR_MAX_USER_STORAGE,
    ERROR_NO_TEXT,
    MAX_USER_STORAGE_BYTES,
    UPLOAD_QUEUED_MESSAGE,
    UPLOAD_SUCCESS_MESSAGE,
)
from api.ingestion.file_utils import (
    build_metadata,
    cleanup_paths,
    compute_text_hash,
    read_upload_data,
    validate_extension,
    write_temp_bytes,
    write_temp_markdown,
)
from api.ingestion.indexer import index_markdown_file
from api.ingestion.job_store import (
    create_job,
    get_total_size_for_user,
    list_jobs_for_user,
    update_job,
)
from api.ingestion.text_extractors import extract_text
from vectordb.files_repository import list_files_for_user

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
        background_tasks: BackgroundTasks | None = None,
    ) -> UploadResponse:
        if not userHash or not userHash.strip():
            raise AgentError("userHash is required.")
        normalized_user_hash = userHash.strip()

        filename = file.filename or ""
        ext = validate_extension(filename)
        data = await read_upload_data(file)
        size = len(data)

        if size > MAX_USER_STORAGE_BYTES:
            raise UserStorageLimitError(ERROR_FILE_TOO_LARGE)

        total_size = get_total_size_for_user(normalized_user_hash)
        if total_size + size > MAX_USER_STORAGE_BYTES:
            raise UserStorageLimitError(ERROR_MAX_USER_STORAGE)

        job = create_job(
            normalized_user_hash,
            filename,
            file.content_type,
            size=len(data),
        )

        if background_tasks is None:
            await self._process_upload_data(
                data,
                ext,
                filename,
                file.content_type,
                normalized_user_hash,
                job.job_id,
            )
        else:
            background_tasks.add_task(
                self._process_upload_data,
                data,
                ext,
                filename,
                file.content_type,
                normalized_user_hash,
                job.job_id,
            )

        return UploadResponse(
            success=True,
            message=UPLOAD_QUEUED_MESSAGE,
            job_id=job.job_id,
            status=job.status,
        )

    async def upload_file(
        self,
        file: UploadFile,
        userHash: str | None = None,
    ) -> UploadResponse:
        if not userHash or not userHash.strip():
            raise AgentError("userHash is required.")
        normalized_user_hash = userHash.strip()

        filename = file.filename or ""
        ext = validate_extension(filename)
        data = await read_upload_data(file)
        size = len(data)

        if size > MAX_USER_STORAGE_BYTES:
            raise UserStorageLimitError(ERROR_FILE_TOO_LARGE)

        total_size = get_total_size_for_user(normalized_user_hash)
        if total_size + size > MAX_USER_STORAGE_BYTES:
            raise UserStorageLimitError(ERROR_MAX_USER_STORAGE)

        await self._process_upload_data(
            data,
            ext,
            filename,
            file.content_type,
            normalized_user_hash,
            None,
        )

        return UploadResponse(success=True, message=UPLOAD_SUCCESS_MESSAGE)

    async def _process_upload_data(
        self,
        data: bytes,
        ext: str,
        filename: str,
        content_type: str | None,
        user_hash: str,
        job_id: str | None,
    ) -> None:
        tmp_path = None
        md_path = None
        if job_id:
            update_job(job_id, status="processing")
        try:
            tmp_path = write_temp_bytes(data, ext)

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
                size=len(data),
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
        files = list_files_for_user(userHash)
        jobs = list_jobs_for_user(userHash)

        if not jobs:
            return files

        ready_ids = {file.id for file in files if file.id}
        job_items: list[FileItem] = []
        for job in jobs:
            if job.status == "ready" and job.content_hash and job.content_hash in ready_ids:
                continue
            job_items.append(
                FileItem(
                    id=job.content_hash if job.status == "ready" else None,
                    name=job.filename,
                    status=job.status,
                    job_id=job.job_id,
                    error_message=job.error_message,
                )
            )

        return files
