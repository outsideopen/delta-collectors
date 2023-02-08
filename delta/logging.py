import logging
import os
from enum import Enum

import colorlog


class LogLevel(Enum):
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0


def getLogger(module):
    color_format = colorlog.ColoredFormatter(
        "{log_color}{levelname:7} {purple}{asctime} {threadName} {blue}{name}:{lineno}{reset} {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "blue",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        style="{",
    )

    logger = logging.getLogger(module)
    level = os.getenv("DELTA_LOG_LEVEL", default="INFO")
    logger.setLevel(level.upper())

    if not logger.hasHandlers():
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(color_format)
        logger.addHandler(stream_handler)

        file_name = "delta.log"
        if file_name:
            file_handler = logging.FileHandler(file_name)
            file_handler.setFormatter(color_format)
            logger.addHandler(file_handler)
    return logger
