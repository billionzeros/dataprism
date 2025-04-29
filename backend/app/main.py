import logging
from fastapi import FastAPI
from app.utils.logging_config import setup_logging, APP_LOGGER_NAME
from app.api import api

setup_logging() # setup logging configuration

logger = logging.getLogger(APP_LOGGER_NAME) # Get the logger instance

# Initialize FastAPI app
app = FastAPI(
    title="Shooting Star",
)

app.include_router(api.api_router, prefix="/api/v1", tags=["api"])