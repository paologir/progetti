#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
from typing import Optional
from pathlib import Path
import json
from datetime import datetime


class StructuredLogger:
    def __init__(self, name: str, log_file: Optional[Path] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Console handler con formato leggibile
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler con formato JSON per analisi
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(JsonFormatter())
            self.logger.addHandler(file_handler)
        
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str, **kwargs):
        self.logger.debug(message, extra={"custom_fields": kwargs})
    
    def info(self, message: str, **kwargs):
        self.logger.info(message, extra={"custom_fields": kwargs})
    
    def warning(self, message: str, **kwargs):
        self.logger.warning(message, extra={"custom_fields": kwargs})
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        if exception:
            kwargs["exception_type"] = type(exception).__name__
            kwargs["exception_message"] = str(exception)
        self.logger.error(message, extra={"custom_fields": kwargs})
    
    def critical(self, message: str, **kwargs):
        self.logger.critical(message, extra={"custom_fields": kwargs})


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if hasattr(record, "custom_fields"):
            log_obj.update(record.custom_fields)
        
        return json.dumps(log_obj, ensure_ascii=False)