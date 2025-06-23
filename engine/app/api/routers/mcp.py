import logging
import uuid
from fastapi import APIRouter, status, HTTPException, Depends
from app.mcp.MCPManager import MCPManager
from app.api.schema.mcp import RunMCPResp, RunMCPReq
from app.api import deps

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

        response = RunMCPResp(session_id=session_id)

        postgres_endpoint = req.postgres_endpoint

        await mcp_manager.start_pg_mcp(
            db_endpoint=postgres_endpoint,
            project_name=str(session_id)
        )

        response = RunMCPResp(
            session_id=session_id,
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