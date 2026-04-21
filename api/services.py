from fastapi import UploadFile
from agno.agent import RunOutput
from openai import AuthenticationError

from schemas.chat_request import ChatRequest
from schemas.chat_history_delete_response import ChatHistoryDeleteResponse
from schemas.chat_message_item import ChatMessageItem
from schemas.chat_response import ChatResponse
from schemas.upload_response import UploadResponse
from schemas.delete_response import DeleteResponse
from schemas.file_item import FileItem
from api.chat_history.store import ChatHistoryStore
from api.exceptions import AgentError, UserTokenLimitError
from api.ingestion.constants import MAX_USER_STORAGE_BYTES
from api.ingestion.orchestrator import UploadOrchestrator
from api.ingestion.job_store import JobStore
from celery_app import celery_app
from config.env_settings import get_settings
from vectordb.files_repository import FileRepository

from agents.chat_responder import get_chat_responder_agent
from vectordb.knowledge import KnowledgeProvider


class LeiService:
    def __init__(self, upload_orchestrator: UploadOrchestrator | None = None) -> None:
        self._upload_orchestrator = upload_orchestrator or UploadOrchestrator()
        self._knowledge_provider = KnowledgeProvider()
        self._file_repository = FileRepository()
        self._job_store = JobStore()
        self._chat_history_store = ChatHistoryStore()
        self._settings = get_settings()

    def chat(self, payload: ChatRequest, api_key: str | None = None) -> ChatResponse:
        user_hash = payload.userHash.strip() if payload.userHash else ""
        if not user_hash:
            raise AgentError("userHash is required.")
        selected_document_ids = payload.documentIds or []

        effective_api_key = api_key.strip() if api_key and api_key.strip() else None

        if effective_api_key is None:
            total_tokens = self._chat_history_store.get_total_tokens_for_user(user_hash)
            if total_tokens >= self._settings.USER_MAX_CHAT_TOKENS:
                raise UserTokenLimitError("User token limit exceeded.")

        if selected_document_ids:
            valid_hashes = self._file_repository.list_ready_content_hashes_for_user(user_hash)
            invalid_ids = sorted(doc_id for doc_id in selected_document_ids if doc_id not in valid_hashes)
            if invalid_ids:
                raise AgentError("Invalid documentIds for user.")

        chat_responder = get_chat_responder_agent(
            knowledge=self._knowledge_provider.get_knowledge(
                user_hash,
                api_key=effective_api_key,
                document_ids=selected_document_ids,
            ),
            api_key=effective_api_key,
        )
        try:
            result: RunOutput = chat_responder.run(
                input=payload.question,
                user_id=user_hash,
                knowledge_filters={"meta_data.hash": selected_document_ids} if selected_document_ids else None,
            )
        except AuthenticationError as exc:
            raise AgentError("Invalid OpenAI API key.") from exc

        content = result.content if isinstance(result.content, str) else str(result.content)
        metrics = result.metrics
        model = result.model
        run_id = result.run_id

        self._chat_history_store.create_message(
            user_hash=user_hash,
            role="user",
            content=payload.question,
            status="completed",
            model=model,
            run_id=run_id,
        )
        self._chat_history_store.create_message(
            user_hash=user_hash,
            role="assistant",
            content=content,
            status="completed",
            model=model,
            run_id=run_id,
            input_tokens=None if effective_api_key is not None else getattr(metrics, "input_tokens", None),
            output_tokens=None if effective_api_key is not None else getattr(metrics, "output_tokens", None),
            total_tokens=None if effective_api_key is not None else getattr(metrics, "total_tokens", None),
        )

        return ChatResponse(answer=content)

    async def enqueue_upload(
        self,
        file: UploadFile,
        userHash: str | None = None,
        api_key: str | None = None,
    ) -> UploadResponse:
        if not userHash or not userHash.strip():
            raise AgentError("userHash is required.")
        normalized_user_hash = userHash.strip()
        effective_api_key = api_key.strip() if api_key and api_key.strip() else None

        result = await self._upload_orchestrator.enqueue_upload(
            file,
            normalized_user_hash,
            max_bytes=MAX_USER_STORAGE_BYTES,
        )

        if not result.is_existing and result.job_id:
            celery_app.send_task("process_upload", args=[result.job_id, effective_api_key])

        return UploadResponse(
            success=result.success,
            message=result.message,
            job_id=result.job_id,
            status=result.status,
        )

    def process_upload_job(self, job_id: str, api_key: str | None = None) -> None:
        self._upload_orchestrator.process_upload_job(job_id, api_key=api_key)

    def list_files(self, userHash: str) -> list[FileItem]:
        return self._file_repository.list_files_for_user(userHash)

    def list_chat_history(self, userHash: str) -> list[ChatMessageItem]:
        return self._chat_history_store.get_messages_for_user(userHash)

    def delete_chat_history(self, userHash: str) -> ChatHistoryDeleteResponse:
        normalized_user_hash = userHash.strip() if userHash else ""
        if not normalized_user_hash:
            raise AgentError("userHash is required.")

        deleted_count = self._chat_history_store.delete_messages_for_user(normalized_user_hash)
        return ChatHistoryDeleteResponse(
            success=True,
            message="Chat history deleted successfully.",
            deleted_count=deleted_count,
            user_hash=normalized_user_hash,
        )

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
