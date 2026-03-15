import logging
from logging.handlers import RotatingFileHandler
import os

class DebugLogger:
    _logger = None  # None cuando desactivado → if-check es free

    @classmethod
    def init(cls, enabled: bool, log_path: str):
        if not enabled:
            return
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        handler = RotatingFileHandler(
            log_path, maxBytes=1_000_000, backupCount=2, encoding="utf-8"
        )
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s",
                              datefmt="%Y-%m-%d %H:%M:%S")
        )
        logger = logging.getLogger("unlighted")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        cls._logger = logger

    @classmethod
    def log(cls, msg, *args):
        """Llama con %s-style para lazy formatting: log("val: %s", x)"""
        if cls._logger:
            cls._logger.debug(msg, *args)
