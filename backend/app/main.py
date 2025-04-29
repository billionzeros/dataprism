import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.utils.logging_config import setup_logging, APP_LOGGER_NAME
from app.api import api
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware

# setup logging configuration
setup_logging() 

# Get the logger instance
logger = logging.getLogger(APP_LOGGER_NAME) 


# Lifespan event handler, called on startup and shutdown of the application
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for the FastAPI application.
    """
    logger.info("Application startup initiated.")
    yield

    logger.info("Application shutdown initiated.")

# Initialize FastAPI app
app = FastAPI(
    title=settings.project_name,
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
# Allow all origins, credentials, methods, and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.api_router, prefix="/api/v1", tags=["api"])