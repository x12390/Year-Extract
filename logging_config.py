import os
import logging

def setup_logging(log_dir="logs", log_file="app.log", level=logging.INFO):
    """
    Sets up centralized logging configuration.
    """
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)

    logging.basicConfig(
        level=level,  # Set the logging level
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=log_path,
        filemode='w'
    )

if __name__ == "__main__":
    setup_logging()
    logging.warning("Logging test started.")