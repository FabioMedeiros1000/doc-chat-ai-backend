from fastapi import UploadFile
from agno.agent import RunOutput

from schemas.chat_request import ChatRequest
from schemas.chat_response import ChatResponse
from schemas.upload_response import UploadResponse
from schemas.delete_response import DeleteResponse
from schemas.file_item import FileItem
from api.exceptions import AgentError
from api.ingestion.constants import MAX_USER_STORAGE_BYTES
from api.ingestion.orchestrator import UploadOrchestrator
from api.ingestion.job_store import JobStore
from celery_app import celery_app
from vectordb.files_repository import FileRepository

from agents.chat_responder import get_chat_responder_agent
from vectordb.knowledge import KnowledgeProvider


class LeiService:
    def __init__(self, upload_orchestrator: UploadOrchestrator | None = None) -> None:
        self._upload_orchestrator = upload_orchestrator or UploadOrchestrator()
        self._knowledge_provider = KnowledgeProvider()
        self._file_repository = FileRepository()
        self._job_store = JobStore()

    def chat(self, payload: ChatRequest) -> ChatResponse:
        chat_responder = get_chat_responder_agent(
            knowledge=self._knowledge_provider.get_knowledge(payload.userHash)
        )
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

        result = await self._upload_orchestrator.enqueue_upload(
            file,
            normalized_user_hash,
            max_bytes=MAX_USER_STORAGE_BYTES,
        )

        if not result.is_existing and result.job_id:
            celery_app.send_task("process_upload", args=[result.job_id])

        return UploadResponse(
            success=result.success,
            message=result.message,
            job_id=result.job_id,
            status=result.status,
        )

    def process_upload_job(self, job_id: str) -> None:
        self._upload_orchestrator.process_upload_job(job_id)

    def list_files(self, userHash: str) -> list[FileItem]:
        return self._file_repository.list_files_for_user(userHash)

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

        self._file_repository.delete_file_for_user(normalized_user_hash, content_hash)
        self._job_store.delete_jobs_for_user(normalized_user_hash, content_hash)

        return DeleteResponse(
            success=True,
            message="File deleted successfully.",
            content_hash=content_hash,
        )
