"""
Logging structuré centralisé - DatavizFT Backend v2
===================================================

Basé sur l'ancien backend/tools/logging_config.py, adapté pour l'architecture hexagonale.
- Logging structuré (structlog)
- Rotation des fichiers
- Format JSON pour les erreurs
- Méthode success(), context manager LogExecutionTime
- Prêt pour correlation_id
"""

import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog
from pythonjsonlogger.json import JsonFormatter

def configure_logging(
    app_name: str = "dataviz-ft",
    log_level: str = "INFO",
    environment: str = "development",
    log_dir: str = "logs"
) -> None:
    """Configure structured logging pour l'application"""

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
            (
                structlog.processors.JSONRenderer()
                if environment == "production"
                else structlog.dev.ConsoleRenderer(colors=True)
            ),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    setup_file_logging(app_name, log_level, log_dir)


def setup_file_logging(app_name: str, log_level: str, log_dir: str = "logs") -> None:
    """Configure le logging vers fichier avec rotation"""
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    file_handler = logging.handlers.RotatingFileHandler(
        log_path / f"{app_name}.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))

    error_handler = logging.handlers.RotatingFileHandler(
        log_path / f"{app_name}-errors.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)

    class CleanFormatter(logging.Formatter):
        """Formatter qui supprime les codes de couleurs ANSI"""
        def format(self, record):
            import re
            ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
            if hasattr(record, "msg"):
                record.msg = ansi_escape.sub("", str(record.msg))
            formatted = super().format(record)
            return ansi_escape.sub("", formatted)

    simple_formatter = CleanFormatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    json_formatter = JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s"
    )

    file_handler.setFormatter(simple_formatter)
    error_handler.setFormatter(json_formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)


class ExtendedLogger:
    """Logger étendu avec méthode success()"""
    def __init__(self, logger: Any):
        self._logger = logger
    def __getattr__(self, name: str) -> Any:
        return getattr(self._logger, name)
    def success(self, message: str, **kwargs) -> None:
        self._logger.info(f"✅ {message}", **kwargs)


def get_logger(name: str) -> ExtendedLogger:
    """Récupère un logger structuré étendu"""
    base_logger = structlog.get_logger(name)
    return ExtendedLogger(base_logger)


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
                error=str(exc_val),
            )
        else:
            self.logger.info(
                "Operation completed",
                operation=self.operation,
                duration_seconds=duration,
            )
