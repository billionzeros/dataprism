import logging

from app.utils import APP_LOGGER_NAME
from fastapi import APIRouter, status, HTTPException
from ..schema.chat import CreateChatReq, CreateChatResp
from app.services.chat import ChatService

router = APIRouter()

logger = logging.getLogger(APP_LOGGER_NAME)

@router.post(
    "/create",
    response_model=CreateChatResp,
    status_code=status.HTTP_200_OK,
    summary="Create a New Chat",
)
async def create_chat(req: CreateChatReq) -> CreateChatResp:
    """
    Create a new chat session and return the chat ID.
    """
    chat_service = ChatService.create()

    resp = CreateChatResp(
        chat_id=chat_service.chat_id,
    )

    return resp

@router.get(
    "/{chat_id}",
    response_model=CreateChatResp,
    status_code=status.HTTP_200_OK,
    summary="Get Chat by ID",
)
async def get_chat_by_id(chat_id: str) :
    """
    Get chat by ID.
    """
    try:
        chat_service = ChatService.get_chat(chat_id=chat_id)

        resp = CreateChatResp(
            chat_id=chat_service.chat_id,
        )

        return resp
    except HTTPException as e:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    
    except ValueError as e:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    

