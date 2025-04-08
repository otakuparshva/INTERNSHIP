import logging
import json
from datetime import datetime
from typing import Any, Dict
from pathlib import Path
import traceback
from fastapi import Request
from core.config import settings

def setup_logger(name: str) -> logging.Logger:
    """Setup a logger with proper formatting and handlers"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # File handler for all logs
        file_handler = logging.FileHandler("logs/app.log")
        file_handler.setLevel(logging.INFO)
        
        # Console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatters and add them to the handlers
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        
        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add extra fields if they exist
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "stack_trace": traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_data)

def log_request(request: Request, response: Any = None, error: Exception = None) -> None:
    """Log HTTP request details"""
    logger = setup_logger("http")
    
    log_data = {
        "method": request.method,
        "url": str(request.url),
        "client_ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }
    
    if response:
        log_data["status_code"] = getattr(response, "status_code", None)
        log_data["response_time"] = getattr(response, "response_time", None)
    
    if error:
        log_data["error"] = {
            "type": type(error).__name__,
            "message": str(error),
            "stack_trace": traceback.format_exc()
        }
        logger.error("Request failed", extra=log_data)
    else:
        logger.info("Request completed", extra=log_data)

def log_error(error: Exception, context: Dict[str, Any] = None) -> None:
    """Log error with context"""
    logger = setup_logger("error")
    
    error_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "stack_trace": traceback.format_exc(),
    }
    
    if context:
        error_data["context"] = context
    
    logger.error("Error occurred", extra=error_data)

def log_security_event(event_type: str, details: Dict[str, Any]) -> None:
    """Log security-related events"""
    logger = setup_logger("security")
    
    event_data = {
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        **details
    }
    
    logger.warning("Security event", extra=event_data)

def log_performance_metric(metric_name: str, value: float, tags: Dict[str, str] = None) -> None:
    """Log performance metrics"""
    logger = setup_logger("performance")
    
    metric_data = {
        "metric": metric_name,
        "value": value,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    if tags:
        metric_data["tags"] = tags
    
    logger.info("Performance metric", extra=metric_data) 