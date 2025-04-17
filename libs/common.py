import time, os

def clear_old_logs(log_dir, retention_days=30, logger=None):
    """
    Deletes log files older than the specified retention period.

    :param log_dir: Directory where log files are stored.
    :param retention_days: Number of days to retain log files.
    :param logger: Logger instance for logging the cleanup process.
    """
    if not os.path.exists(log_dir):
        log_or_print(
            f"Log directory '{log_dir}' does not exist. Skipping cleanup.", logger
        )
        return

    current_time = time.time()
    retention_seconds = retention_days * 24 * 60 * 60

    for filename in os.listdir(log_dir):
        file_path = os.path.join(log_dir, filename)
        if os.path.isfile(file_path):
            file_age = current_time - os.path.getmtime(file_path)
            if file_age > retention_seconds:
                try:
                    os.remove(file_path)
                    log_or_print(
                        f"Deleted old log file: {file_path}", logger
                    )
                except Exception as e:
                    log_or_print(
                        f"Failed to delete log file '{file_path}': {e}", logger, is_error=True
                    )

def log_or_print(message, logger=None, is_error=False):
    if logger:
        if is_error:
            logger.error(message)
        else:
            logger.info(message)
    else:
        print(message)