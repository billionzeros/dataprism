import logging
import uuid
from fastapi import APIRouter, status, HTTPException
from app.api.schema.matrix import AskMatrixReq, AskMatrixResp
from app.pipeline.modules.matrix import MatrixModule
from app.pipeline.tools import FindRelevantDocuments, GetParquetFileSchemaTool, QueryParquetFileUsingStorageKeyTool, QueryParquetFileUsingUploadIdTool

logger = logging.getLogger("app.api.routers.matrix")

router = APIRouter()


@router.post(
    "/ask-matrix",
    status_code=status.HTTP_200_OK,
    summary="Matrix Module",
    response_model=AskMatrixResp,
)
async def ask_matrix(req: AskMatrixReq):
    try:
        session_id = uuid.uuid4()

        logger.info(f"New Ask Matrix Request: {req.user_query} with session_id: {session_id}")

        tools = [
            FindRelevantDocuments,
            GetParquetFileSchemaTool,
            QueryParquetFileUsingStorageKeyTool,
            QueryParquetFileUsingUploadIdTool
        ]

        module = MatrixModule(session_id=session_id, tools = tools)

        result = await module.aforward(user_query=req.user_query)

        answer = result.answer
        if not answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No relevant documents found or query execution failed."
            )
        
        logger.info(f"Answer: {answer}")

        response = AskMatrixResp(
            chat_id=session_id,
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