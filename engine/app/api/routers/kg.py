from fastapi import APIRouter, status
from app.api.schema.kg import EncodeCSVResp
import uuid

router = APIRouter()

@router.get(
    "/encode-csv",
    response_model=EncodeCSVResp,
    status_code=status.HTTP_200_OK,
    summary="Encode CSV for Knowledge Graph",
)
async def health_check(
    *,
    upload_id: str, # upload_id of the CSV file to be encoded
) -> EncodeCSVResp:
    """
    Health check endpoint.
    """    

    return EncodeCSVResp(
        id=uuid.UUID(upload_id)
    )
