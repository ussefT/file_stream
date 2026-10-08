import logging 
import sys
from pathlib import Path
import os

BASE_DIR=Path(__file__).resolve().parent
LOG_DIR=Path(os.environ.get("STREAM_LOG_DIR",BASE_DIR/"logs"))

try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

except OSError:
    pass

LOG_FILE=LOG_DIR/"app.log"

def init_logger()-> logging.Logger:
    """
    Create a log on Path app / logs / app.log
    """
    
    logger=logging.getLogger("App")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # File
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024 ,
        backupCount=3,
        encoding="utf-8",

    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = init_logger()