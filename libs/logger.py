import logging
import sys
from logging.handlers import RotatingFileHandler


class Logger:
    def __init__(
        self,
        log_file="dl_stream_video.log",
        log_level=logging.INFO,
        max_bytes=5 * 1024 * 1024,
        backup_count=3,
    ):
        """
        Initialize the logger with file and console handlers.

        :param log_file: Path to the log file.
        :param log_level: Logging level (e.g., logging.INFO, logging.DEBUG).
        :param max_bytes: Maximum size of the log file before rotation.
        :param backup_count: Number of backup log files to keep.
        """
        self.logger = logging.getLogger(log_file)
        self.logger.setLevel(log_level)
        self.logger.propagate = False  # Prevent duplicate logs

        # File handler with rotation
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        self.logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
        self.logger.addHandler(console_handler)

    def get_logger(self):
        """
        Returns the logger instance.
        """
        return self.logger
