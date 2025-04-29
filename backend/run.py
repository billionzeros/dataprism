import uvicorn

from app.core.config import settings

if __name__ == "__main__":

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
        # workers=4,
        # log_level="info",
    )
