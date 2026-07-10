import logging
import json
import sys
from datetime import datetime, timezone
from app.config import settings

class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        # Prevent printing sensitive keys in raw log messages
        sensitive_keywords = [
            "password", "password_hash", "hashed_password", 
            "access_token", "JWT_SECRET", "GEMINI_API_KEY", "Authorization", 
            "api_key", "secret_key"
        ]
        msg = record.getMessage()
        for kw in sensitive_keywords:
            if kw.lower() in msg.lower():
                # Replace message with a scrubbed indicator
                record.msg = f"[SCRUBBED] Log message contained potentially sensitive keyword reference: '{kw}'"
                # Clear args since we altered the msg structure
                record.args = ()
                break
        return True

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logging():
    """Initializes logging configurations for development and production environments."""
    root_logger = logging.getLogger()
    
    # Clean up any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Set log level based on ENV
    log_level = logging.INFO if settings.ENV == "production" else logging.DEBUG
    root_logger.setLevel(log_level)

    # Console stream handler
    console_handler = logging.StreamHandler(sys.stdout)

    # Set appropriate formatter
    if settings.ENV == "production":
        console_handler.setFormatter(JSONFormatter())
    else:
        # Development clean string formatter
        console_handler.setFormatter(logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(module)s.%(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))

    console_handler.addFilter(SensitiveDataFilter())
    root_logger.addHandler(console_handler)
    
    # Silence third-party logs (e.g. uvicorn, HTTPX)
    logging.getLogger("uvicorn.access").handlers = [console_handler]
    logging.getLogger("httpx").setLevel(logging.WARNING)
