import logging

from app.core.config import settings

from app.utils.logging_config import setup_logging, APP_LOGGER_NAME

setup_logging() # setup logging configuration

logger = logging.getLogger(APP_LOGGER_NAME) # Get the logger instance

def main():
    """
    Main entry point for the application.
    """
    logger.info("Starting application in %s environment", settings.environment)

    logger.info("Application started successfully")

if __name__ == "__main__":
    main()