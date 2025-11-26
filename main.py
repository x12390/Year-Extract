import os
import shutil
import logging
import config
import time
import pandas as pd
import glob
import re
import aiohttp
import asyncio

from datetime import datetime
from file_operation import move_file_to_directory, backup_files
from console_prompt import ask_yes_no
from select_and_combine_metadata import select_meta_cols
from logging_config import setup_logging
from year_extracting import extracting_year_and_write_csv
from split_csv_file import split_csv_by_size

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
    if config.CLEAN_OUTPUT_FOLDER_AT_STARTUP:
        backup_files(config.OUTPUT_DIR, "backup")
        logger.info("Output files moved to backup folder.")
        shutil.rmtree(config.OUTPUT_DIR)

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)


def metafile_transformation():
    # configure csv files
    if config.TEST_MODE_ACTIVATED:
        meta_data_csv = os.path.join("data", config.FILENAME_META_TST)
    else:
        meta_data_csv = os.path.join("data", config.FILENAME_META_PRD)

    logger.info(f"Using data csv: {meta_data_csv}")

    if ask_yes_no("Do you want to start a new meta file transformation? No, will use existing files."):
        shutil.rmtree("processed")
        os.makedirs("processed", exist_ok=True)

        logger.info("Starting csv file transformation...")
        shutil.rmtree("csv_parts")

        #create new csv with 2 cols: id and combination of selected columns
        tmpfile_path = select_meta_cols(meta_data_csv, create_csv=True)
        logger.info(f"Successfully transformed meta file: {tmpfile_path}")

        # splitting big csv into chunk files
        logger.info(f"splitting meta file {tmpfile_path} in multiple files: max_rows {config.CSV_SPILT_FILE_ROWS}")
        split_csv_by_size(tmpfile_path, "csv_parts", max_rows=config.CSV_SPILT_FILE_ROWS)




# force numeric sorting, because sorted uses lexicographical sorting
def natural_sort_key(filename):
    # extrahiere die Zahl nach 'part_'
    match = re.search(r'part_(\d+)\.csv$', filename)
    return int(match.group(1)) if match else 0


async def main_async():
    logger.info("Application started.")
    cleanup_and_ensure_folder()
    metafile_transformation()

    # sorted glob
    csv_files = sorted(glob.glob(os.path.join("csv_parts", "part_*.csv")), key=natural_sort_key)

    async with aiohttp.ClientSession() as session:
        for file_path in csv_files:
            filename = os.path.basename(file_path)
            if config.PROMPT_AFTER_CHUNK:
                if not ask_yes_no(f"Do you want to process the next file ({filename})?"):
                    logger.warning("Aborted by user.")
                    break


            logger.info(f"\n--- Loading file {filename} ... ---")
            df = pd.read_csv(file_path)
            chunk_rows = len(df)

            start_time = time.time()
            #### PROCESSING START ###

            df_years = await extracting_year_and_write_csv(session, df)

            #write output csv
            timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            name_part = os.path.splitext(filename)[0]
            output_file_name = f"{timestamp_str}_extracted_years_{name_part}.csv"
            output_file_path = os.path.join(config.OUTPUT_DIR, output_file_name)

            await asyncio.to_thread(df_years[['id', 'year', 'origin']].astype(str).to_csv, output_file_path, index=False)
            logger.info(f"Write new file: {output_file_path}")

            #### PROCESSING END ###
            end_time = time.time()

            elapsed = end_time - start_time
            row_per_sec = round(elapsed / chunk_rows, 2)
            logger.info(f"{file_path} processed in {elapsed:.2f} seconds. Rows per Sec: {row_per_sec} ")

            move_file_to_directory(source_path=file_path, target_dir="processed")
            logger.info(f"File moved from '{file_path}' to 'processed'")

    logger.info("All selected files are processed.")


if __name__=="__main__":
    asyncio.run(main_async())