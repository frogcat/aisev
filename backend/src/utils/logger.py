from loguru import logger
import os
import sys

log_dir = os.path.join(os.path.dirname(__file__), '../../logs')
os.makedirs(log_dir, exist_ok=True)

logger.remove()  # Clear existing sink

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()

# Console output
logger.add(sys.stdout, colorize=True, level=LOG_LEVEL,
           backtrace=True, diagnose=True)

# File output
logger.add(
    os.path.join(log_dir, "backend_{time:YYYY-MM-DD}.log"),
    rotation="00:00",
    retention="10 days",
    encoding="utf-8",
    enqueue=True,
    backtrace=True,
    diagnose=True,
    level=LOG_LEVEL
)
