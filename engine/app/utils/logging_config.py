import logging
import logging.config
import sys
import json
from typing import Dict, Any

from app.settings.config import settings

APP_LOGGER_NAME = "prism"

class JsonFormatter(logging.Formatter):
    """
    Axiom works best with structured JSON logs, so we create a custom formatter
    """
    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "pathname": record.pathname,
            "lineno": record.lineno,
            "funcName": record.funcName,
        }
        # Add exception info if present
        if record.exc_info:
            log_record['exc_info'] = self.formatException(record.exc_info)
        if record.stack_info:
            log_record['stack_info'] = self.formatStack(record.stack_info)

        extra_keys = set(record.__dict__.keys()) - set(log_record.keys()) - {'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename', 'levelname', 'levelno', 'message', 'module', 'msecs', 'msg', 'name', 'pathname', 'process', 'processName', 'relativeCreated', 'stack_info', 'thread', 'threadName'}
        for key in extra_keys:
                log_record[key] = record.__dict__[key]


        return json.dumps(log_record)

LOG_LEVEL = settings.log_level.upper()

axiom_configured = all([
    settings.axiom_token,
    settings.axiom_org_id,
    settings.axiom_dataset,
])

LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "()": JsonFormatter,
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": LOG_LEVEL,
            "formatter": "simple",
            "stream": sys.stdout,
        },
    },
    "loggers": {
        "uvcorn.error": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
    },
    "root": {
        "level": LOG_LEVEL,
        "handlers": ["console"],
    }
}

if settings.enable_axiom and axiom_configured:
    try:
        LOGGING_CONFIG["handlers"]["axiom"] = {
            "class": "axiom_logging.AxiomHandler",
            "level": LOG_LEVEL,
            "formatter": "json",
            "org_id": settings.axiom_org_id,
            "dataset": settings.axiom_dataset,
            "token": settings.axiom_token,
        }
        
        LOGGING_CONFIG['root']['handlers'].append('axiom')
        LOGGING_CONFIG['loggers']['uvicorn.error']['handlers'].append('axiom')
    except ImportError:
        print("Warning: Axiom library not installed. Skipping Axiom logging setup.")
        raise
    except Exception as e:
        print(f"Error setting up Axiom logging: {e}")
        raise

def setup_logging():
    """
    Configures logging using settings from app.core.config.

    Sets up console logging and Axiom logging if configured.
    """

    try:
        logging.config.dictConfig(LOGGING_CONFIG)
        logger = logging.getLogger(APP_LOGGER_NAME)

        logger.info("Logging configured successfully. Level: %s", LOG_LEVEL)
    except Exception as e:
        print(f"Error applying logging dictConfig: {e}. Falling back to basic config.")
        raise