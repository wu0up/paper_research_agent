from typing import Optional
from loguru import logger
from pathlib import Path
from rich.logging import RichHandler

def configure(log_level: str = "DEBUG", log_file: Optional[Path] = 'logs/logs.log'):
    log_format = "<green>{time:HH:mm:ss}</green> - <level>{level: <8}</level> - <level>{message}</level>"
    logger.remove()

    handlers=[
        {
            "sink": RichHandler(rich_tracebacks=True, markup=True),
            "format": log_format,
            "level": log_level.upper(),
        }
    ]
    logger.configure(handlers=handlers)

    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            sink=str(log_file),
            level=log_level.upper(),
            format=log_format,
            rotation="10 MB",
        )