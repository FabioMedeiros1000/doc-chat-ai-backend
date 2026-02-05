from fastapi import UploadFile
from agno.agent import RunOutput

from schemas.chat_request import ChatRequest
from schemas.chat_response import ChatResponse
from schemas.upload_response import UploadResponse
from schemas.pergunta import Pergunta
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

from agents.chat_responder import agent as chat_responder

class LeiService:
    def chat(self, payload: ChatRequest) -> ChatResponse:
        result: RunOutput = chat_responder.run(payload.question)
        return ChatResponse(answer=result.content)

    async def upload_file(self, file: UploadFile) -> UploadResponse:
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
            metadata = build_metadata(filename, file.content_type, content_hash)
            md_path = write_temp_markdown(text)
            await index_markdown_file(md_path, content_hash, metadata)

            return UploadResponse(success=True, message=UPLOAD_SUCCESS_MESSAGE)
        finally:
            cleanup_paths(tmp_path, md_path)
