import io
import asyncio
import uuid
import duckdb
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from app.utils import APP_LOGGER_NAME 
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.cloud import R2Client, R2UploadError
from app.services.upload import csv as csv_service
from app.settings.config import settings
from app.db.models.upload import UploadType, Upload as UploadModel, ProcessingStatus
from app.api.schema.upload  import UploadCreateResp, ProcessUploadResp, CheckAbleToAccessFileResp
from app.services.duck_db import DuckDBConn
from app.pipeline.modules.process_csv import ProcessCSV, CSVHeaderDescriptionContext
from app.pipeline.handler.embeddings import Embedder, EmbedContentConfig, EmbeddingSourceType, EmbeddingModel

logger = logging.getLogger(APP_LOGGER_NAME)

# Router for CSV Upload
router = APIRouter()

@router.get(
    "/validate",
    status_code=status.HTTP_200_OK,
    summary="Validate CSV upload",
    tags=["upload"],
)
async def validate_csv_upload(
    *,
    db: AsyncSession = Depends(deps.get_db),
    upload_id: str,
):
    """
    Validates the CSV upload by checking if the upload exists and is of type CSV.
    """
    try:
        upload_uuid = uuid.UUID(upload_id)

        upload = await csv_service.get_upload_by_id(db=db, upload_id=upload_uuid)
        if not upload:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Upload not found",
            )
        
        response = CheckAbleToAccessFileResp(
            able_to_access=False,
            error_message=None,
        )
        
        try:
            with DuckDBConn() as duckdb_conn:
                logger.info(f"Upload Storage Key: {upload.storage_key}")
                s3_uri = f"s3://{settings.r2_bucket_name}/{upload.storage_key}"

                describe_query = "DESCRIBE SELECT * FROM read_parquet(?);"

                conn = duckdb_conn.conn

                if conn is None:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to establish DuckDB connection.",
                    )
                
                headers_result = conn.execute(describe_query, parameters=[s3_uri]).fetchall()

                if not headers_result:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="No headers found for the CSV file.",
                    )
                response.able_to_access = True
                response.error_message = None

                return response

        except duckdb.Error as e:
            logger.error(f"DuckDB Error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process CSV file with DuckDB.",
            )
            
        except ValueError as ve:
            logger.error(f"Invalid CSV file: {ve}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid CSV file: {ve}",
            )

        except Exception as e:
            logger.error(f"Error processing CSV file: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while processing the CSV file.",
            )
        
        return response
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error validating CSV upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while validating the CSV upload.",
        )

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
    "/process",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Process CSV file",
    tags=["upload"],
)
async def process_csv(
    *,
    upload_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    r2_client: R2Client = Depends(deps.get_r2_client),
):
    """
    Processes a CSV file, using DuckDB retrive the headers of the CSV 
    after which send the headers of the CSV for further understanding the context
    of the headers after which upload them to the Database.
    """
    logger.info(f"Processing CSV file with ID: {upload_id}")

    try:
        upload = await csv_service.get_upload_by_id(db=db, upload_id=upload_id)

        if not upload:
            logger.warning(f"Upload with ID {upload_id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Upload not found with ID {upload_id}.",
            )
        
        if upload.processing_status == ProcessingStatus.PROCESSING:
            logger.warning(f"Upload with ID {upload_id} is already being processed.")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Upload is already being processed.",
            )
        
        if not upload.storage_key:
            logger.warning(f"Upload with ID {upload_id} has no storage key.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Upload does not have a valid storage key.",
            )
        
        headers: List[str] = []
        num_sample_rows = 3
        headers_context: List[CSVHeaderDescriptionContext] = []

        try:
            with DuckDBConn() as duckdb_conn:
                s3_uri = f"s3://{settings.r2_bucket_name}/{upload.storage_key}"

                # DuckDB query to describe the CSV file
                describe_query = "DESCRIBE SELECT * FROM read_parquet(?);"

                conn = duckdb_conn.conn

                if conn is None:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to establish DuckDB connection.",
                    )

                headers_result = conn.execute(describe_query, parameters=[s3_uri]).fetchall()

                if not headers_result:
                    logger.error(f"No headers found for upload {upload_id}.")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="No headers found for the CSV file.",
                    )

                for row in headers_result:
                    context = CSVHeaderDescriptionContext(
                        header_name=row[0],
                        sample_data=[],
                    )
                    headers_context.append(context)
                    headers.append(row[0])

                logger.info(f"Successfully extracted headers for upload {upload_id}: {headers}")

                if headers:
                    sample_query = f"SELECT {', '.join(headers)} FROM read_parquet(?) LIMIT ?;"
                    sample_result = conn.execute(sample_query, parameters=[s3_uri, num_sample_rows]).fetchall()

                    if sample_result:
                        for row in sample_result:
                            for i, sample_data in enumerate(row):
                                context = headers_context[i]
                                if context is not None:
                                    context.sample_data.append(sample_data)
                    else:
                        logger.warning(f"No sample data found for upload {upload_id}.")

        except duckdb.Error as e:
            logger.error(f"DuckDB Processing Error: {e}")

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process CSV file with DuckDB.",
            )
        
        except HTTPException:
            raise

        # Process headers context
        module = ProcessCSV()
        
        output = await module.aforward(
            headers_count = len(headers),
            headers_info = headers_context,
        )

        em = Embedder(config=EmbedContentConfig(
            task_type="SEMANTIC_SIMILARITY",
        ))

        ems = em.generate_embeddings(content=[header.model_dump_json() for header in output.headers_info])
        if not ems:
            logger.error("Failed to generate embeddings.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate embeddings.",
            )    
        
        await em.store_embeddings(
            db=db,
            ems=[
                EmbeddingModel(
                    source_type=EmbeddingSourceType.CSV_COLUMN,
                    source_identifier=str(upload.id),
                    column_or_chunk_name=header.header_name,
                    original_text=header.model_dump_json(),
                    embedding=embedding.values,
                )
                for embedding, header in zip(ems, output.headers_info)
            ],
        )

        response = ProcessUploadResp(
            id= upload.id,
            embeddings_count= len(ems),
            file_name= upload.file_name,
            file_type= upload.file_type,
        )

        return response
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error processing CSV file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the CSV file.",
        )


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
