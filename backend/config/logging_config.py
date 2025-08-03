import logging

LOG_FILE = "trading.log"
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s | %(levelname)-5s | %(message)s"
LOG_NAME = "ghostswap"


def setup_logger(name: str = LOG_NAME, level: int = LOG_LEVEL,
                 fmt: str | None = LOG_FORMAT) -> logging.Logger:
    """Create and configure a named logger.

    Initializes a `logging.Logger` with the given name, log level,
    and optional format, adding a StreamHandler if none exists.

    Args:
        name (str):
            Name of the logger (typically `__name__`).

        level (int, optional):
            Logging level (e.g., logging.INFO). Defaults to INFO.

        fmt (str | None, optional):
            Log message format string; uses a default if None.

    Returns:
        logging.Logger: Configured logger instance.

    """
    logger = logging.getLogger(name)

    if not logger.handlers:  # avoid duplicate handlers
        logger.setLevel(level)
        handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        handler.setLevel(level)
        formatter = logging.Formatter(fmt)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = True
    return logger
