import uuid
from pydantic import BaseModel
from typing import Any, Dict

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

# ===== Chat Get ======
class ChatGetResp(BaseModel):
    chat_id: uuid.UUID

    model_config = {
        "from_attributes": True,
    }

# =============================

# ===== Test Chat Interface ======
class TestChatReq(BaseModel):
    user_query: str

    model_config = {
        "from_attributes": True,
    }

class TestChatResp(BaseModel):
    chat_id: uuid.UUID
    user_query: str
    final_answer: str
    thought_process: Dict[str, Any]

    model_config = {
        "from_attributes": True,
    }

# =============================