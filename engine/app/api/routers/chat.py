import logging

from app.utils import APP_LOGGER_NAME
from dspy.streaming import StreamResponse
from fastapi import APIRouter, status, HTTPException
from ..schema.chat import CreateChatReq, CreateChatResp, TestChatReq, TestChatResp
from app.services.chat import ChatService
from app.pipeline.modules.matrix import MatrixModule
from app.pipeline.tools import FindRelevantDocuments, GetParquetFileSchemaTool, QueryParquetFileUsingStorageKeyTool, QueryParquetFileUsingUploadIdTool

router = APIRouter()

logger = logging.getLogger(APP_LOGGER_NAME)

@router.post(
    "/matrix",
    status_code=status.HTTP_200_OK,
    summary="Test Matrix Module",
    response_model=TestChatResp,
)
async def test_chat_service(req: TestChatReq):
    """
    Test the Chat DSPy Module.
    """
    try:

        chat_service = ChatService.create()

        tools = [
            FindRelevantDocuments,
            GetParquetFileSchemaTool,
            QueryParquetFileUsingStorageKeyTool,
            QueryParquetFileUsingUploadIdTool
        ]

        module = MatrixModule(session_id=chat_service.chat_id, tools = tools)

        result = await module.aforward(user_query=req.user_query)

        logger.info(f"Chat Service Test Result: {result}")

        answer = result.answer
        if not answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No relevant documents found or query execution failed."
            )
        
        logger.info(f"Answer: {answer}")

        response = TestChatResp(
            chat_id=chat_service.chat_id,
            user_query=req.user_query,
            answer=answer,
            reasoning=result.reasoning,
        )

        return response
    
    except HTTPException as e:
        logger.error(f"HTTP Exception in test_chat_service: {e.detail}")
        raise e
    
    except Exception as e:
        logger.error(f"Unexpected error in test_chat_service: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the request."
        )

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
    

