import uuid
from typing import Optional
from pydantic import BaseModel, Field

# ===== Workspace Create ======
class WorkspaceCreateReq(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, alias="workspace_name")
    description: Optional[str] = Field(None, max_length=255, alias="workspace_description")

class WorkspaceCreateResp(BaseModel):
    id: uuid.UUID
    
    name: str
    description: str

    model_config = {
        "from_attributes": True,
    }

# =============================

# ===== Get Workspace ======
class WorkspaceGetReq(BaseModel):
    model_config = {"extra": "forbid"}
    
    workspace_id: Optional[uuid.UUID] = Field(None, alias="workspace_id")
    workspace_name: Optional[str] = Field(None, min_length=1, max_length=255, alias="workspace_name")

class WorkspaceGetResp(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = Field(None, max_length=255)

    model_config = {
        "from_attributes": True,
    }
# =============================