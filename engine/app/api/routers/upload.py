import io
import asyncio
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from app.utils import APP_LOGGER_NAME 
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.cloud import R2Client, R2UploadError
from app.services import csv as csv_service
from app.db.models.upload import UploadType, Upload as UploadModel
from app.api.schema.upload  import UploadCreateResp

logger = logging.getLogger(APP_LOGGER_NAME)

# Router for CSV Upload
router = APIRouter()

@router.get(
    "/all",
    status_code=status.HTTP_200_OK,
    summary="Get all uploads",
    tags=["upload"],
)
async def get_all_uploads(
    *,
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieves all uploads with pagination.
    """

    try:
        uploads = await csv_service.get_uploads(db=db, skip=skip, limit=limit)
        if not uploads:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No uploads found",
            )
        
        response = [
            UploadCreateResp(
                id=upload.id,
                file_name=upload.file_name,
                file_size=upload.file_size,
                file_type=upload.file_type,
                storage_key=upload.storage_key,
                storage_url=upload.storage_url,
            )
            for upload in uploads
        ]

        return response
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error retrieving uploads: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the uploads.",
        )

@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Get upload by ID",
    tags=["upload"],
)
async def get_upload(
    *,
    db: AsyncSession = Depends(deps.get_db),
    upload_id: uuid.UUID,
):
    """
    Retrieves an upload by its ID.
    """
    try:
        upload = await csv_service.get_upload_by_id(db=db, upload_id=upload_id)
        if not upload:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Upload not found",
            )
        
        response = UploadCreateResp(
            id=upload.id,
            file_name=upload.file_name,
            file_size=upload.file_size,
            file_type=upload.file_type,
            storage_key=upload.storage_key,
            storage_url=upload.storage_url,
        )

        return response
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error retrieving upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the upload.",
        )

# CSV Upload Endpoint
@router.post(
    "/csv",
    status_code=status.HTTP_202_ACCEPTED,
    tags = ["upload"]
)
async def upload_csv(
    *,
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
    r2_object_key = f"uploads/parquet/{uuid.uuid4()}/{file_name}"

    try:
        logger.info(f"Processing CSV file: {csv_file.filename}")

        parquet_buffer = await csv_service.convert_csv_to_parquet_stream(csv_file.file)
        logger.info(f"CSV file converted to Parquet format: {file_name}")

        try:
            r2_upload_url = await asyncio.to_thread(
                r2_client.upload_fileobj,
                file_obj=parquet_buffer,
                object_key=r2_object_key,
                content_type="application/vnd.apache.parquet",
            )
        except R2UploadError as e:
            logger.error(f"R2 Upload Error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file to R2.",
            )
        

        if not r2_upload_url:
            logger.error("Failed to upload file to R2.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file to R2.",
            )
        
        upload_info = await csv_service.create_upload(
            db=db,
            upload_info=UploadModel(
                file_name=file_name,
                file_type=UploadType.PARQUET,
                file_size=parquet_buffer.getbuffer().nbytes,
                storage_key=r2_object_key,
                storage_url=r2_upload_url,
            ),
        )

        response = UploadCreateResp(
            id = upload_info.id,
            file_name= upload_info.file_name,
            file_size= upload_info.file_size,
            file_type= upload_info.file_type,
            storage_key= upload_info.storage_key,
            storage_url= upload_info.storage_url,
        )

        return response
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
