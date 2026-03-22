from fastapi import APIRouter, BackgroundTasks, Depends, status, HTTPException, UploadFile, File, Form, Query
from functools import lru_cache

from schemas.chat_request import ChatRequest
from schemas.chat_response import ChatResponse
from schemas.upload_response import UploadResponse
from schemas.delete_response import DeleteResponse
from schemas.file_item import FileItem
from api.services import LeiService
from api.exceptions import AgentError, UserStorageLimitError

router = APIRouter()

@lru_cache
def get_law_service() -> LeiService:
    return LeiService()

@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_200_OK,
)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    userHash: str | None = Form(None),
    service: LeiService = Depends(get_law_service),
):
    if not userHash or not userHash.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="userHash is required.",
        )
    try:
        return await service.enqueue_upload(
            file,
            userHash=userHash,
            background_tasks=background_tasks,
        )
    except UserStorageLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(e),
        )
    except AgentError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )

@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
def chat(
    payload: ChatRequest,
    service: LeiService = Depends(get_law_service),
):
    try:
        return service.chat(payload)
    except UserStorageLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(e),
        )
    except AgentError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )

@router.get(
    "/files",
    response_model=list[FileItem],
    status_code=status.HTTP_200_OK,
)
def list_files(
    userHash: str = Query(...),
    service: LeiService = Depends(get_law_service),
):
    if not userHash or not userHash.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="userHash is required.",
        )
    try:
        files = service.list_files(userHash)
    except UserStorageLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(e),
        )
    except AgentError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )
    return files

@router.delete(
    "/files/{file_id}",
    response_model=DeleteResponse,
    status_code=status.HTTP_200_OK,
)
def delete_file(
    file_id: str,
    userHash: str = Query(...),
    service: LeiService = Depends(get_law_service),
):
    if not userHash or not userHash.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="userHash is required.",
        )
    try:
        return service.delete_file(file_id, userHash)
    except AgentError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )
