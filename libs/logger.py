import logging, sys, os
from datetime import datetime
from logging.handlers import RotatingFileHandler


class Logger:
    def __init__(
        self,
        log_level=logging.INFO,
        max_bytes=5 * 1024 * 1024,
        backup_count=3,
        time_str=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
    ):
        """
        Initialize the logger with file and console handlers.

        :param log_level: Logging level (e.g., logging.INFO, logging.DEBUG).
        :param max_bytes: Maximum size of the log file before rotation.
        :param backup_count: Number of backup log files to keep.
        """

        log_file = os.path.join("logs", f"dl_stream_video_{time_str}.log")
        # Ensure the directory for the log file exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self.logger = logging.getLogger(log_file)
        self.logger.setLevel(log_level)
        self.logger.propagate = False  # Prevent duplicate logs

        # File handler with rotation
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
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
