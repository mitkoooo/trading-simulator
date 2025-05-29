import logging

LOG_FILE = "trading.log"
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s | %(levelname)-5s | %(message)s"
LOG_NAME = "york_exchange"


def setup_logger(name: str = LOG_NAME) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:  # avoid duplicate handlers
        logger.setLevel(LOG_LEVEL)
        handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        handler.setLevel(LOG_LEVEL)
        formatter = logging.Formatter(LOG_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = True
    return logger
