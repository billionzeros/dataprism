import io
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from app.utils import APP_LOGGER_NAME 
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.cloud import R2Client
from app.services import csv as csv_service
logger = logging.getLogger(APP_LOGGER_NAME)

# Router for CSV Upload
router = APIRouter()

# CSV Upload Endpoint
@router.post(
    "/csv",
    status_code=status.HTTP_202_ACCEPTED,
    tags = ["upload"]
)
async def upload_csv(
    *,
    workspace_id: str,
    csv_file: UploadFile = File(..., description="CSV file to upload"),
    db: AsyncSession = Depends(deps.get_db),
    r2_client: R2Client = Depends(deps.get_r2_client),
):
    """
    Accepts CSV, and uploads using R2Client.
    """
    if not csv_file.filename or not csv_file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only CSV files are allowed.",
        )
    
    parquet_buffer: io.BytesIO | None = None
    file_name = csv_file.filename[:-4] + ".parquet"
    r2_object_key = f"workspaces/{workspace_id}/{file_name}"

    try:
        logger.info(f"Processing CSV file: {csv_file.filename}")

        parquet_buffer = await csv_service.convert_csv_to_parquet_stream(csv_file.file)
        logger.info(f"CSV file converted to Parquet format: {file_name}")

        r2_upload_url = r2_client.upload_fileobj(
            file_obj=parquet_buffer,
            object_key=r2_object_key,
            content_type="application/vnd.apache.parquet",
        )

        if not r2_upload_url:
            logger.error("Failed to upload file to R2.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file to R2.",
            )
        
        logger.info(f"File uploaded to R2: {r2_upload_url}")

    except ValueError as ve:
        logger.error(f"Error During Processing CSV file: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error During Processing CSV file: {ve}",
        )
    finally:
        await csv_file.close()

        if parquet_buffer:
            parquet_buffer.close()
