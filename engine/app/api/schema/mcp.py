
import uuid
from pydantic import BaseModel
from app.mcp.postgres._schema import PostgresEndpoint

# ===== Run MCP ======
class RunMCPReq(BaseModel):
    postgres_endpoint: PostgresEndpoint

    model_config = {
        "from_attributes": True,
    }

class RunMCPResp(BaseModel):
    session_id: uuid.UUID

    model_config = {
        "from_attributes": True,
    }

# =============================