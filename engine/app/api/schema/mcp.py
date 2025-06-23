
import uuid
from pydantic import BaseModel, Field
from app.mcp.postgres._schema import PostgresEndpoint

# ===== Run MCP ======
class RunMCPReq(BaseModel):
    postgres_endpoint: PostgresEndpoint

    model_config = {
        "from_attributes": True,
    }

class RunMCPResp(BaseModel):
    session_id: uuid.UUID

    runner_endpoint: str = Field(..., description="The endpoint of the Postgres MCP runner service.",)

    model_config = {
        "from_attributes": True,
    }

# =============================