
import logging
import boto3
import boto3.s3
import boto3.s3.transfer
from botocore.config import Config
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from typing import Optional, BinaryIO

from app.core.config import settings
from app.utils import APP_LOGGER_NAME, SingletonMeta

logger = logging.getLogger(APP_LOGGER_NAME)

# Custom exceptions for R2Client
class R2ClientError(Exception):
    """Base exception for R2Client errors."""
    pass

class R2ConfigError(R2ClientError):
    """Error related to R2 client configuration."""
    pass

class R2UploadError(R2ClientError):
    """Error during R2 upload operation."""
    pass

# R2Client is a singleton class that manages the connection to Cloudflare R2 storage.
class R2Client(metaclass=SingletonMeta):
    """
    Client for Internet With Cloudflare R2 storage.
    """

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self._bucket_name = settings.r2_bucket_name
        self._endpoint_url = str(settings.r2_endpoint_url)
        self._access_key_id = settings.r2_access_key_id
        self._secret_access_key = settings.r2_secret_access_key

        self._transfer_config = boto3.s3.transfer.TransferConfig(
            multipart_threshold=1024 * 25,
            max_concurrency=10,
            multipart_chunksize=1024 * 25,
            use_threads=True,
        )

        # Initialize the Boto3 client
        self._client = self._create_client()

        self._initialized = True # Mark as initialized

    def _create_client(self):
        """
        Initialize the Boto3 client for R2.
        """

        if not all([self._endpoint_url, self._access_key_id, self._secret_access_key, self._bucket_name]):
            logger.error("R2 configuration is incomplete. Please check your settings.")

            raise R2ConfigError("R2 configuration is incomplete. Please check your settings.")
        
        try:
            client = boto3.client(
                's3',
                endpoint_url=self._endpoint_url,
                aws_access_key_id=self._access_key_id,
                aws_secret_access_key=self._secret_access_key,
                region_name='auto',
                config=Config(
                    connect_timeout=60,
                    read_timeout=120,
                    s3={'addressing_style': 'path'},
                    retries={'mode': 'standard'}
                )
            )

            return client
        except (NoCredentialsError, PartialCredentialsError) as e:
            logger.error("Credentials error: %s", e)
            raise R2ConfigError("Invalid R2 credentials") from e
        except Exception as e:
            logger.error("Error creating R2 client: %s", e)
            
            raise R2ConfigError("Error creating R2 client") from e
        

    def close(self):
        """
        Close the R2 client connection.
        """
        if self._client:
            self._client.close()
            logger.info("R2 client connection closed.")
        else:
            logger.warning("R2 client is not initialized, nothing to close.")
    
    def upload_fileobj(self, file_obj: BinaryIO, object_key: str, content_type: Optional[str] = None):
        """
        Uploads a file-like object (stream) to R2 using multipart if necessary.
        """
        
        if not self._client:
            logger.error("R2 Client not initialized, cannot upload file.")

            raise R2ConfigError("R2 Client not initialized, cannot upload file.")
        
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type

            file_obj.seek(0)  # Ensure the file pointer is at the beginning

            self._client.upload_fileobj(
                file_obj,
                self._bucket_name,
                object_key,
                ExtraArgs=extra_args,
                Config=self._transfer_config
            )
            logger.info("File uploaded successfully to R2: %s", object_key)

            object_url = f"{self._endpoint_url}/{self._bucket_name}/{object_key}"

            return object_url        
        except ClientError as e:
            logger.error("Client error during upload: %s", e)
            raise R2UploadError("Client error during upload") from e

        except Exception as e:
            logger.error("Error setting extra arguments for upload: %s", e)
            raise R2UploadError("Error setting extra arguments for upload") from e