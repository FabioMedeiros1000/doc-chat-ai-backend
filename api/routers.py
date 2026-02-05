from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File
from functools import lru_cache

from schemas.chat_request import ChatRequest
from schemas.chat_response import ChatResponse
from schemas.upload_response import UploadResponse
from api.services import LeiService
from api.exceptions import AgentError

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
    file: UploadFile = File(...),
    service: LeiService = Depends(get_law_service),
):
    try:
        return await service.upload_file(file)
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
    except AgentError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )


