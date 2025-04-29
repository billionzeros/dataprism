import uuid
from typing import Optional
from pydantic import BaseModel, Field

# ===== Workspace Create ======
class WorkspaceCreateReq(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=255)

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
    workspace_id: uuid.UUID
    workspace_name: Optional[str] = Field(None, min_length=1, max_length=255)

class WorkspaceGetResp(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = Field(None, max_length=255)

    model_config = {
        "from_attributes": True,
    }
# =============================