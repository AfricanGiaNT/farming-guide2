"""
Logging utility for the Agricultural Advisor Bot.
Provides structured logging with different levels and formatting.
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

class BotLogger:
    """Custom logger for the Agricultural Advisor Bot."""
    
    def __init__(self, name: str = "AgricultureBot", log_level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create formatters
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Setup console handler
        self._setup_console_handler()
        
        # Setup file handler
        self._setup_file_handler()
    
    def _setup_console_handler(self):
        """Setup console (stdout) logging handler."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self):
        """Setup file logging handler."""
        # Create logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Create log file with timestamp
        log_file = logs_dir / f"bot_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)
    
    def info(self, message: str, user_id: Optional[str] = None):
        """Log info message."""
        if user_id:
            message = f"[User: {user_id}] {message}"
        self.logger.info(message)
    
    def debug(self, message: str, user_id: Optional[str] = None):
        """Log debug message."""
        if user_id:
            message = f"[User: {user_id}] {message}"
        self.logger.debug(message)
    
    def warning(self, message: str, user_id: Optional[str] = None):
        """Log warning message."""
        if user_id:
            message = f"[User: {user_id}] {message}"
        self.logger.warning(message)
    
    def error(self, message: str, user_id: Optional[str] = None):
        """Log error message."""
        if user_id:
            message = f"[User: {user_id}] {message}"
        self.logger.error(message)
    
    def critical(self, message: str, user_id: Optional[str] = None):
        """Log critical message."""
        if user_id:
            message = f"[User: {user_id}] {message}"
        self.logger.critical(message)
    
    def log_user_query(self, user_id: str, query: str, query_type: str = "text"):
        """Log user query with structured format."""
        self.info(f"Query received - Type: {query_type}, Content: {query}", user_id)
    
    def log_bot_response(self, user_id: str, response_type: str, success: bool):
        """Log bot response with success status."""
        status = "SUCCESS" if success else "FAILED"
        self.info(f"Response sent - Type: {response_type}, Status: {status}", user_id)
    
    def log_api_call(self, api_name: str, endpoint: str, status_code: int, user_id: Optional[str] = None):
        """Log API call with details."""
        message = f"API Call - {api_name} ({endpoint}) - Status: {status_code}"
        if status_code >= 400:
            self.error(message, user_id)
        else:
            self.info(message, user_id)
    
    def get_timestamp(self) -> str:
        """Get current timestamp in ISO format for AI integration."""
        return datetime.now().isoformat()


# Global logger instance
logger = BotLogger() 