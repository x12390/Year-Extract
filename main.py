import os
import shutil
import logging
import config
import time
import pandas as pd
import glob
import re

from file_operation import move_file_to_directory, backup_files
from console_prompt import ask_yes_no
from select_and_combine_metadata import select_meta_cols
from logging_config import setup_logging

setup_logging(log_file="app.log")
logger = logging.getLogger(__name__)

def cleanup_and_ensure_folder():
    # ensure tmp directory exists
    os.makedirs("csv_parts", exist_ok=True)

    # ensure tmp directory exists
    os.makedirs("tmp", exist_ok=True)

    # ensure processed directory exists
    os.makedirs("processed", exist_ok=True)

    # ensure output directory exists
    backup_files("output", "backup")
    logger.info("Output files moved to backup folder.")
    shutil.rmtree("output")
    os.makedirs("output", exist_ok=True)


def metafile_transformation():
    # configure csv files
    if config.TEST_MODE_ACTIVATED:
        meta_data_csv = "data//" + config.FILENAME_META_TST
    else:
        meta_data_csv = "data//" + config.FILENAME_META_PRD

    logger.info(f"Using data csv: {meta_data_csv}")

    if ask_yes_no("Do you want to start a new meta file transformation? No, will use existing files."):
        shutil.rmtree("processed")
        os.makedirs("processed", exist_ok=True)

        logger.info("Starting csv file transformation...")
        shutil.rmtree("csv_parts")
        df = select_meta_cols(meta_data_csv, create_csv=True)
        logger.info(f"Successfully transformed file")

# force numeric sorting, because sorted uses lexicographical sorting
def natural_sort_key(filename):
    # extrahiere die Zahl nach 'part_'
    match = re.search(r'part_(\d+)\.csv$', filename)
    return int(match.group(1)) if match else 0


def main():
    logger.info("Application started.")
    cleanup_and_ensure_folder()
    metafile_transformation()

    csv_files = sorted(glob.glob(os.path.join("csv_parts", "part_*.csv")), key=natural_sort_key)
    for file_path in csv_files:
        filename = os.path.basename(file_path)
        if config.PROMPT_AFTER_CHUNK:
            if not ask_yes_no(f"Do you want to process the next file ({filename})?"):
                logger.warning("Aborted by user.")
                break


        logger.info(f"\n--- Loading file {filename} ... ---")
        df = pd.read_csv(file_path)

        start_time = time.time()
        #@TODO process df

        end_time = time.time()
        elapsed = end_time - start_time
        logger.info(f"{file_path} processed in {elapsed:.2f} seconds")
        logger.info(f"{file_path} processed in {elapsed:.2f} seconds")

        move_file_to_directory(source_path=file_path, target_dir="processed")
        logger.info(f"File moved from '{file_path}' to 'processed'")

    logger.info("All selected files are processed.")
    backup_files("output", "backup")
    logger.info("Output files moved to backup folder.")
    shutil.rmtree("output")
    os.makedirs("output", exist_ok=True)

if __name__=="__main__":
    main()