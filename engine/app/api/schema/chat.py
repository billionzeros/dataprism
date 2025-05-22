import uuid
from pydantic import BaseModel

# ===== Chat Create ======
class CreateChatReq(BaseModel):
    model_config = {
        "from_attributes": True,
    }
    
class CreateChatResp(BaseModel):
    chat_id: uuid.UUID

    model_config = {
        "from_attributes": True,
    }

# =============================