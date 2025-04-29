import uuid
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models.workspace import Workspace as WorkspaceModel

async def get_workspace(db: AsyncSession, workspace_id: uuid.UUID) -> Optional[WorkspaceModel]: 
    """
    Gets a single workspace by its ID.
    """
    statement = select(WorkspaceModel).where(WorkspaceModel.id == workspace_id)
    result = await db.execute(statement)
    return result.scalars().first()


async def get_workspace_by_name(db: AsyncSession, name: str) -> Optional[WorkspaceModel]: 
    """
    Gets a single workspace by its name.
    """
    statement = select(WorkspaceModel).where(WorkspaceModel.name == name)
    result = await db.execute(statement)
    return result.scalars().first()

async def get_workspaces(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[WorkspaceModel]:
    """
    Gets a list of workspaces.
    """
    statement = select(WorkspaceModel).offset(skip).limit(limit)
    result = await db.execute(statement)
    return list(result.scalars().all())

async def create_workspace(db: AsyncSession, workspace: WorkspaceModel) -> WorkspaceModel:
    """
    Creates a new workspace.
    """
    db.add(workspace)

    await db.flush()
    await db.refresh(workspace)
    
    return workspace