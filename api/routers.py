from fastapi import APIRouter, Depends, status, HTTPException
from functools import lru_cache

from schemas.resposta_simples import RespostaSimples
from schemas.trechos_lei import ListaTrechosLei
from schemas.resposta_legal import RespostaLegal
from schemas.pergunta import Pergunta
from api.services import LeiService
from api.exceptions import AgentError

router = APIRouter()

@lru_cache
def get_law_service() -> LeiService:
    return LeiService()

@router.post(
    "/retriever",
    response_model=ListaTrechosLei,
    status_code=status.HTTP_200_OK,
)
def retriever_laws(
    payload: Pergunta,
    service: LeiService = Depends(get_law_service),
):
    try:
        return service.retriever_laws(payload)
    except AgentError as e:
        
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )
        
@router.post(
    "/explain-law",
    response_model=str,
    status_code=status.HTTP_200_OK,
)
def explain_law(
    payload: Pergunta,
    service: LeiService = Depends(get_law_service),
):
    try:
        return service.explain_law(payload)
    except AgentError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )

@router.post(
    "/responder",
    response_model=RespostaLegal,
    status_code=status.HTTP_200_OK,
)
def responder(
    payload: Pergunta,
    service: LeiService = Depends(get_law_service),
):
    try:
        return service.responder(payload)
    except AgentError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )
        
@router.post(
    "/chat-responder",
    response_model=RespostaSimples,
    status_code=status.HTTP_200_OK,
)
def chat_responder(
    payload: Pergunta,
    service: LeiService = Depends(get_law_service),
):
    try:
        return service.chat_responder(payload)
    except AgentError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )
        
@router.post(
    "/technical-note",
    response_model=str,
    status_code=status.HTTP_200_OK,
)
def technical_note(
    payload: Pergunta,
    service: LeiService = Depends(get_law_service),
):
    try:
        return service.technical_note(payload)
    except AgentError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )
