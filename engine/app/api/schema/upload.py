import uuid
from pydantic import BaseModel

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