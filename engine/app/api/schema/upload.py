import uuid
from pydantic import BaseModel
from typing import Optional


# ===== Upload Create ======
class UploadCreateResp(BaseModel):
    id: uuid.UUID

    file_name: str
    file_type: str
    file_size: int
    storage_key: str
    storage_url: str

    model_config = {
        "from_attributes": True,
    }

# =============================


# ===== Upload Get ======
class UploadGetResp(BaseModel):
    id: uuid.UUID

    file_name: str
    file_type: str
    file_size: int
    storage_key: str
    storage_url: str

    model_config = {
        "from_attributes": True,
    }

# =============================

# ===== Process Upload ======
class ProcessUploadResp(BaseModel):
    id: uuid.UUID
    file_name: str
    file_type: str
    embeddings_count: int

    model_config = {
        "from_attributes": True,
    }

# =============================

# ===== Check Able to Access File ======
class CheckAbleToAccessFileResp(BaseModel):
    able_to_access: bool
    error_message: Optional[str] = None

    model_config = {
        "from_attributes": True,
    }

# =============================