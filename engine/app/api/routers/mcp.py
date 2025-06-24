import logging
import uuid
from fastapi import APIRouter, status, HTTPException, Depends
from app.mcp.MCPManager import MCPManager
from app.api.schema.mcp import RunMCPResp, RunMCPReq
from app.api import deps
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

logger = logging.getLogger("app.api.routers.matrix")

router = APIRouter()


@router.post(
    "/run-mcp",
    status_code=status.HTTP_200_OK,
    summary="Run MCP Request",
    response_model=RunMCPResp,
)
async def run_mcp(
    *,
    req: RunMCPReq, 
    mcp_manager: MCPManager = Depends(deps.get_mcp_manager)
):
    try:
        session_id = uuid.uuid4()

        postgres_endpoint = req.postgres_endpoint

        runner = await mcp_manager.start_pg_mcp(
            db_endpoint=postgres_endpoint,
            project_name=str(session_id)
        )

        response = RunMCPResp(
            session_id=session_id,
            runner_endpoint=runner.runner_sse_endpoint
        )

        return response
    
    except HTTPException as e:
        logger.error(f"HTTP Exception in run_mcp: {e.detail}")
        raise e
    
    except Exception as e:
        logger.error(f"Unexpected error in run_mcp: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the request."
        )
    


@router.get(
    "/list-tools",
    status_code=status.HTTP_200_OK,
    summary="Run MCP Request",
)
async def list_tools():
    try:
        client = streamablehttp_client("http://localhost:8080/mcp/")

        read_stream, write_stream, _ = await client.__aenter__()

        session = ClientSession(read_stream, write_stream)

        await session.__aenter__()

        await session.initialize()

        available_tools = await session.list_tools()

        await session.__aexit__(None, None, None)
        await client.__aexit__(None, None, None)

        return available_tools
    
    
    except HTTPException as e:
        logger.error(f"HTTP Exception in run_mcp: {e.detail}")
        raise e
    
    except Exception as e:
        logger.error(f"Unexpected error in run_mcp: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the request."
        )
    