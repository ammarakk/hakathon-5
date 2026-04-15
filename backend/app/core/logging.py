"""
Nur Scents Customer Success Agent - Logging Configuration
"""

import logging
import sys
from pathlib import Path
from loguru import logger as loguru_logger
from app.core.config import settings


def setup_logging() -> None:
    """Setup application logging"""

    # Remove default handler
    loguru_logger.remove()

    # Console handler with formatting
    loguru_logger.add(
        sys.stdout,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        level=settings.LOG_LEVEL,
        colorize=True,
    )

    # File handler for persistent logs
    log_path = Path(settings.LOG_FILE_PATH)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    loguru_logger.add(
        settings.LOG_FILE_PATH,
        rotation=f"{settings.LOG_ROTATION} MB",
        retention=f"{settings.LOG_RETENTION} days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level=settings.LOG_LEVEL,
        compression="zip",
    )

    # Intercept standard logging
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            """Intercept standard logging records"""
            try:
                level = loguru_logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            loguru_logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )

    # Configure standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    # Set loguru as the default logger
    logger = logging.getLogger("uvicorn")
    logger.handlers = [InterceptHandler()]
    logger.setLevel(settings.LOG_LEVEL)

    loguru_logger.info("🌸 Logging configured successfully")
