import logging

from app.api import deps
from app.services import workspace as workspace_service
from app.utils import APP_LOGGER_NAME
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.workspace import Workspace as WorkspaceModel
from app.api.schema.workspace import WorkspaceCreateReq, WorkspaceCreateResp

logger = logging.getLogger(APP_LOGGER_NAME)

router = APIRouter()

@router.post(
    "/",
    summary="Create a new workspace",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "description": "Workspace created successfully",
            "model": WorkspaceCreateResp,
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad request",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
        },
    },
    tags=["Workspace"],
)
async def create_workspace(
    *,
    db: AsyncSession = Depends(deps.get_db),
    req: WorkspaceCreateReq
): 
    """
    Creates a new workspace. Requires a unique name.
    """
    logger.info(f"Recvived Request to create Workspace: {req.name}")

    try:
        workspace = await workspace_service.create_workspace(
            db=db,
            workspace=WorkspaceModel(
                name=req.name,
                description=req.description,
            ),
        )

        logger.info(f"Workspace created successfully: {workspace.id}")
        return workspace
    except Exception as e:
        logger.error(f"Error creating workspace: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )