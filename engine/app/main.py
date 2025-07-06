import logging
import dspy
from contextlib import asynccontextmanager
from fastapi import FastAPI
import mlflow
from mlflow.dspy import autolog as mlflow_autolog_dspy
from app.utils.logging_config import setup_logging, APP_LOGGER_NAME
from app.api import api
from app.settings.config import settings
from app.cloud.cf.r2_client import R2Client
from fastapi.middleware.cors import CORSMiddleware
from app.pipeline import GenerativeModel
from app.mcp import MCPManager
from app.workers import ThreadPoolWorkerQueue
from app.kg.graph_manager import KnowledgeGraph

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
    try:
        app.state.graph_db = KnowledgeGraph()
        r2_client = R2Client()
        mcp_manager = MCPManager()
        thread_pool_worker = ThreadPoolWorkerQueue(num_workers=settings.thread_pool_worker_count)

        app.state.r2_client = r2_client
        app.state.mcp_manager = mcp_manager
        app.state.thread_pool_worker = thread_pool_worker

        # Set up MLflow for tracking DSPy Runs
        mlflow.set_tracking_uri("http://localhost:3080")  
        mlflow.set_experiment("DSPy")  

        mlflow_autolog_dspy() # Enable Auto Logging

        lm = dspy.LM(model=GenerativeModel.GEMINI_2_0_FLASH, api_key=settings.gemini_api_key, cache=True)
        # dspy.configure(lm=lm, track_usage=True,)
        dspy.configure(lm=lm)

    except Exception as e:
        logger.critical(f"Fatal Error during API Startup: {e}")

    yield

    logger.info("Application shutdown initiated.")

    if hasattr(app.state, "graph_db"):
        try:
            app.state.graph_db.close()
        except Exception as e:
            logger.error(f"Error closing Neo4j connection: {e}")

    if hasattr(app.state, "r2_client"):
        try:
            app.state.r2_client.close()
        except Exception as e:
            logger.error(f"Error closing R2 client connection: {e}")

    if hasattr(app.state, "mcp_manager"):
        try:
            app.state.mcp_manager.close()
        except Exception as e:
            logger.error(f"Error closing MCP manager connection: {e}")

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