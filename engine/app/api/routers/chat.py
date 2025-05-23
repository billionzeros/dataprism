import logging
from app.utils import APP_LOGGER_NAME
from fastapi import APIRouter, status, HTTPException
from ..schema.chat import CreateChatReq, CreateChatResp, TestChatReq, TestChatResp
from app.services.chat import ChatService
from app.pipeline.modules.chat import ChatModule

router = APIRouter()

logger = logging.getLogger(APP_LOGGER_NAME)


@router.post(
    "/test",
    status_code=status.HTTP_200_OK,
    summary="Test Chat Service",
    response_model=TestChatResp,
)
async def test_chat_service(req: TestChatReq):
    """
    Test the Chat DSPy Module.
    """

    chat_service = ChatService.create()

    module = ChatModule(chat_id=chat_service.chat_id, tools = [])

    result = module.forward(user_query=req.user_query)

    logger.info(f"Chat Service Test Result: {result}")

    response = TestChatResp(
        chat_id=chat_service.chat_id,
        user_query=req.user_query,
        final_answer=result.final_answer,
        thought_process=result.thought_process
    )

    return response

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
    

