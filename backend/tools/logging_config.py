"""
Configuration logging professionnelle pour DatavizFT
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import structlog
from pythonjsonlogger import jsonlogger


def configure_logging(
    app_name: str = "dataviz-ft",
    log_level: str = "INFO",
    environment: str = "development"
) -> None:
    """Configure structured logging pour l'application"""
    
    # Configuration structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if environment == "production" 
            else structlog.dev.ConsoleRenderer(colors=True)
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configuration logging standard
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Logger pour les métriques
    if environment == "production":
        setup_file_logging(app_name, log_level)


def setup_file_logging(app_name: str, log_level: str) -> None:
    """Configure le logging vers fichier pour la production"""
    
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Handler pour les logs généraux
    file_handler = logging.FileHandler(
        log_dir / f"{app_name}.log",
        encoding="utf-8"
    )
    
    # Handler pour les erreurs
    error_handler = logging.FileHandler(
        log_dir / f"{app_name}-errors.log",
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    
    # Format JSON pour la production
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s"
    )
    
    file_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)
    
    # Ajout aux loggers
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)


def get_logger(name: str) -> Any:
    """Récupère un logger structuré"""
    return structlog.get_logger(name)


# Context managers pour le logging métier
class LogExecutionTime:
    """Context manager pour logger le temps d'exécution"""
    
    def __init__(self, logger: Any, operation: str):
        self.logger = logger
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info("Operation started", operation=self.operation)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        if exc_type:
            self.logger.error(
                "Operation failed", 
                operation=self.operation,
                duration_seconds=duration,
                error=str(exc_val)
            )
        else:
            self.logger.info(
                "Operation completed", 
                operation=self.operation,
                duration_seconds=duration
            )