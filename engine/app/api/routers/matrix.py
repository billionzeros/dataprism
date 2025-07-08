import logging
import uuid
import dspy
from fastapi import APIRouter, status, HTTPException
from app.api.schema.matrix import AskMatrixReq, AskMatrixResp
from app.llm.modules.matrix import MatrixModule
from mcp.client.sse import sse_client
from mcp import ClientSession
from app.llm.tools import FindRelevantCSV, GetParquetFileSchemaTool, QueryParquetFileUsingStorageKeyTool, QueryParquetFileUsingUploadIdTool

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

        client = sse_client("http://localhost:8010/sse")

        read_stream, write_stream = await client.__aenter__()

        session = ClientSession(read_stream, write_stream)

        await session.__aenter__()

        await session.initialize()

        try:
            session_id = uuid.uuid4()

            logger.info(f"New Ask Matrix Request: {req.user_query} with session_id: {session_id}")

            available_pg_tools = await session.list_tools()

            pg_tools = [dspy.Tool.from_mcp_tool(session=session, tool=tool) for tool in available_pg_tools.tools]

            tools = [
                FindRelevantCSV,
                GetParquetFileSchemaTool,
                QueryParquetFileUsingStorageKeyTool,
                QueryParquetFileUsingUploadIdTool
            ]

            for tool in pg_tools:
                tools.append(tool)

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
        
        finally:
            logger.info("Closing session and client connection.")

            await session.__aexit__(None, None, None)
            await client.__aexit__(None, None, None)

    except HTTPException as e:
        logger.error(f"HTTP Exception in ask_matrix: {e.detail}")
        raise e
