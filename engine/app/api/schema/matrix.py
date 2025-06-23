
import uuid
from pydantic import BaseModel
from app.pipeline.modules._schema import Paragraph, BarGraph, BulletPoint, Table, LineGraph
from typing import Union, List

# ===== Ask Matrix ======
class AskMatrixReq(BaseModel):
    user_query: str

    model_config = {
        "from_attributes": True,
    }

class AskMatrixResp(BaseModel):
    chat_id: uuid.UUID
    user_query: str
    answer: List[Union[Paragraph, BulletPoint, BarGraph, LineGraph, Table]]
    reasoning: str

    model_config = {
        "from_attributes": True,
    }

# =============================