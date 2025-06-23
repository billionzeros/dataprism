import uvicorn

from engine.app.settings.config import settings

if __name__ == "__main__":

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
        workers=settings.workers,
        log_level=settings.log_level.lower(),
    )
