from fastapi import UploadFile
from agno.agent import RunOutput

from schemas.chat_request import ChatRequest
from schemas.chat_response import ChatResponse
from schemas.upload_response import UploadResponse
from schemas.file_item import FileItem
from api.exceptions import AgentError
from api.ingestion.constants import ERROR_NO_TEXT, UPLOAD_SUCCESS_MESSAGE
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
from api.ingestion.text_extractors import extract_text
from vectordb.files_repository import list_files_for_user

from agents.chat_responder import get_chat_responder_agent

from vectordb.knowledge import get_knowledge

class LeiService:
    def chat(self, payload: ChatRequest) -> ChatResponse:
        chat_responder = get_chat_responder_agent(knowledge=get_knowledge(payload.userHash))
        result: RunOutput = chat_responder.run(input=payload.question)
        
        return ChatResponse(answer=result.content)

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

        tmp_path = None
        md_path = None
        try:
            tmp_path = write_temp_bytes(data, ext)

            text = extract_text(tmp_path)
            if not text or not text.strip():
                raise AgentError(ERROR_NO_TEXT)

            content_hash = compute_text_hash(text)
            metadata = build_metadata(
                filename,
                file.content_type,
                content_hash,
                normalized_user_hash,
                size=len(data),
            )
            md_path = write_temp_markdown(text)

            try:
                await index_markdown_file(
                    md_path,
                    content_hash,
                    metadata,
                    userHash=normalized_user_hash,
                )
            except Exception as e:
                raise AgentError(f'Error during indexing: {str(e)}') from e

            return UploadResponse(success=True, message=UPLOAD_SUCCESS_MESSAGE)
        finally:
            cleanup_paths(tmp_path, md_path)

    def list_files(self, userHash: str) -> list[FileItem]:
        return list_files_for_user(userHash)
