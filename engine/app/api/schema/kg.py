import uuid
from pydantic import BaseModel

# ===== Encode CSV ======
class EncodeCSVResp(BaseModel):
    id: uuid.UUID

    model_config = {
        "from_attributes": True,
    }

# =============================