from fastapi import APIRouter, status
from pydantic import BaseModel


class HealthStatus(BaseModel):
    """
    Health status model.
    """
    status: str
    message: str

router = APIRouter()

@router.get(
    "/",
    response_model=HealthStatus,
    status_code=status.HTTP_200_OK,
    summary="Check the health of the API",
)
async def health_check() -> HealthStatus:
    """
    Health check endpoint.
    """
    return HealthStatus(status="ok", message="API is healthy")
