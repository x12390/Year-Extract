import os
import logging
import sys

def setup_logging(log_dir="logs", log_file="app.log", level=logging.INFO):
    """
    Sets up centralized logging configuration with:
    - File logging
    - Console logging
    """

    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)

    # Get main logger
    logger = logging.getLogger()
    logger.setLevel(level)

    # Prevent adding handlers multiple times (important in notebooks or repeated calls)
    if logger.handlers:
        return logger

    # Formatter for both console and file
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # --- File Handler ---
    file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # --- Console Handler ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


if __name__ == "__main__":
    setup_logging()
    logging.warning("Logging test started.")