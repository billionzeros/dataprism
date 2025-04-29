import logging
from typing import Optional
from app.api import deps
from app.services import workspace as workspace_service
from app.utils import APP_LOGGER_NAME
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.workspace import Workspace as WorkspaceModel
from app.api.schema.workspace import WorkspaceCreateReq, WorkspaceCreateResp, WorkspaceGetReq, WorkspaceGetResp

logger = logging.getLogger(APP_LOGGER_NAME)

router = APIRouter()

@router.get(
    "/{workspace_id}",
    summary="Get workspace by ID",
    response_model=WorkspaceCreateResp,
    tags=["Workspace"],
)
async def get_workspace(
    *,
    db: AsyncSession = Depends(deps.get_db),
    req: WorkspaceGetReq
): 
    """
    Retrieves a workspace by its ID.
    """
    logger.info("Received Request to get workspace")

    try:
        workspace: Optional[WorkspaceModel] = None
        if req.workspace_id is not None:
            workspace = await workspace_service.get_workspace(
                db=db,
                workspace_id=req.workspace_id,
            )

        if req.workspace_name is not None:
            workspace = await workspace_service.get_workspace_by_name(
                db=db,
                name=req.workspace_name,
            )

        if not workspace:
            logger.warning(f"Workspace not found: {req.workspace_id or req.workspace_name}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )
        logger.info(f"Retrieved workspace: {workspace.id}")

        response = WorkspaceGetResp(
            id=workspace.id,
            name=workspace.name,
            description=workspace.description,
        )

        return response
    except Exception as e:
        logger.error(f"Error retrieving workspace: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

@router.post(
    "/",
    summary="Create a new workspace",
    status_code=status.HTTP_201_CREATED,
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
        response = WorkspaceCreateResp(
            id=workspace.id,
            name=workspace.name,
            description="NA" or workspace.description,
        )

        return response
    except Exception as e:
        logger.error(f"Error creating workspace: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )