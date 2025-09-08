"""
Logging system for Clienti CRM
Provides centralized logging with configuration from config.toml
"""
import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

from .config import get_config

class CRMLogger:
    """Centralized logger for the CRM system"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = None
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration based on config.toml"""
        log_config = self.config.logging
        
        # Create logs directory if it doesn't exist
        log_file_path = Path(log_config.file)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger('clienti_crm')
        self.logger.setLevel(getattr(logging, log_config.level.upper()))
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_config.file,
            maxBytes=log_config.max_file_size_mb * 1024 * 1024,
            backupCount=log_config.backup_count,
            encoding='utf-8'
        )
        
        # Console handler for development
        console_handler = logging.StreamHandler()
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        
        # Only add console handler in debug mode or if explicitly requested
        if self.config.server.debug or log_config.level.upper() == 'DEBUG':
            self.logger.addHandler(console_handler)
    
    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance"""
        return self.logger
    
    def log_operation(self, operation: str, details: str, level: str = 'INFO'):
        """Log a business operation with structured format"""
        message = f"OPERATION: {operation} - {details}"
        getattr(self.logger, level.lower())(message)
    
    def log_timer_start(self, cliente: str, descrizione: str = ""):
        """Log timer start event"""
        if self.config.logging.timer_enabled:
            self.log_operation('TIMER_START', f"Cliente: {cliente}, Descrizione: {descrizione}")
    
    def log_timer_stop(self, cliente: str, durata: str, compenso: float):
        """Log timer stop event"""
        if self.config.logging.timer_enabled:
            self.log_operation('TIMER_STOP', f"Cliente: {cliente}, Durata: {durata}, Compenso: €{compenso}")
    
    def log_backup_created(self, backup_path: str, size_mb: float):
        """Log backup creation"""
        self.log_operation('BACKUP_CREATED', f"Path: {backup_path}, Size: {size_mb:.2f}MB")
    
    def log_backup_restored(self, backup_path: str):
        """Log backup restoration"""
        self.log_operation('BACKUP_RESTORED', f"From: {backup_path}", 'WARNING')
    
    def log_export_operation(self, export_type: str, destination: str, items_count: int):
        """Log export operations"""
        self.log_operation('EXPORT', f"Type: {export_type}, Destination: {destination}, Items: {items_count}")
    
    def log_import_operation(self, import_type: str, source: str, items_count: int):
        """Log import operations"""
        self.log_operation('IMPORT', f"Type: {import_type}, Source: {source}, Items: {items_count}")
    
    def log_client_operation(self, operation: str, cliente_nome: str, details: str = ""):
        """Log client-related operations"""
        self.log_operation(f'CLIENT_{operation}', f"Cliente: {cliente_nome}, {details}")
    
    def log_todo_operation(self, operation: str, todo_id: int, titolo: str):
        """Log todo operations"""
        self.log_operation(f'TODO_{operation}', f"ID: {todo_id}, Titolo: {titolo}")
    
    def log_web_access(self, endpoint: str, method: str, ip: str = ""):
        """Log web interface access"""
        if self.config.logging.web_enabled:
            self.logger.info(f"WEB_ACCESS: {method} {endpoint} from {ip}")
    
    def log_database_operation(self, operation: str, table: str, details: str = ""):
        """Log database operations"""
        self.log_operation(f'DB_{operation}', f"Table: {table}, {details}")
    
    def log_config_change(self, setting: str, old_value: str, new_value: str):
        """Log configuration changes"""
        self.log_operation('CONFIG_CHANGE', f"Setting: {setting}, Old: {old_value}, New: {new_value}", 'WARNING')
    
    def log_error(self, operation: str, error: Exception, details: str = ""):
        """Log errors with context"""
        self.logger.error(f"ERROR in {operation}: {str(error)} - {details}", exc_info=True)
    
    def log_audit(self, user: str, action: str, resource: str, details: str = ""):
        """Log security/audit events"""
        if self.config.security.audit_enabled:
            self.log_operation('AUDIT', f"User: {user}, Action: {action}, Resource: {resource}, {details}", 'WARNING')

# Global logger instance
_crm_logger = None

def get_logger() -> CRMLogger:
    """Get global CRM logger instance"""
    global _crm_logger
    if _crm_logger is None:
        _crm_logger = CRMLogger()
    return _crm_logger

def log_operation(operation: str, details: str, level: str = 'INFO'):
    """Convenience function for logging operations"""
    get_logger().log_operation(operation, details, level)

def log_error(operation: str, error: Exception, details: str = ""):
    """Convenience function for logging errors"""
    get_logger().log_error(operation, error, details)

class LogContext:
    """Context manager for operation logging"""
    
    def __init__(self, operation: str, details: str = ""):
        self.operation = operation
        self.details = details
        self.start_time = None
        self.logger = get_logger()
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.log_operation(f'{self.operation}_START', self.details)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = datetime.now() - self.start_time
        if exc_type is None:
            self.logger.log_operation(
                f'{self.operation}_COMPLETE', 
                f"{self.details}, Duration: {duration.total_seconds():.2f}s"
            )
        else:
            self.logger.log_error(
                self.operation,
                exc_val,
                f"{self.details}, Duration: {duration.total_seconds():.2f}s"
            )