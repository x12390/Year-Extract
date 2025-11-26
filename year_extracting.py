import pandas as pd
import re
import os
import asyncio
import logging
import aiohttp
import config

from prompt_lmstudio import set_prompt_text
from get_latest_year import extract_latest_year

logger = logging.getLogger(__name__)

def is_valid_year(year):
    try:
        y = int(year)
        return 1900 <= y <= 2100
    except (TypeError, ValueError):
        return False

# ASYNCHRON VERSION
async def extracting_year_and_write_csv(session, df):
    # RULE BASED SEARCH
    df['year'] = df['combined'].apply(extract_latest_year).astype("string")

    df_remaining = df[df['year'] == ""].copy().astype("string")
    df_done = df[df['year'] != ""].copy().astype("string")
    df_done["origin"] = "RULE"

    logger.info(f"Processing {len(df)} by rules: {len(df_done)} done, {len(df_remaining)} remaining.")

    # AI SEARCH - PROCESS IF RULE BASED SEARCH DID NOT FIND A YEAR
    if config.ENABLE_AI_PROCESS:
        years = []
        total = len(df_remaining)
        logger.info(f"Processing remaing {len(df_remaining)} with AI.")

        for idx, text in enumerate(df_remaining['combined'], start=1):
            year = await set_prompt_text(session, text)

            years.append(year)

            # Fortschritt ausgeben mit flush
            if idx % 10 == 0 or idx == total:
                logger.info(f"Processed by AI: {idx}/{total} rows ({idx / total * 100:.1f}%)")

        df_remaining['year'] = years

        df_remaining["year"] = (
            df_remaining["year"]
            .astype(str)  # falls None oder andere Typen
            .str.extract(r"(\d{4})")[0]  # extrahiert 4-stellige Zahl oder NaN
            .fillna(config.NOT_FOUND_RETURN_VALUE)  # ersetzt alle NaN durch leeren String
        )

        df_remaining["year"] = df_remaining["year"].apply(lambda y: y if is_valid_year(y) else "0")
        df_remaining["year"] = df_remaining["year"].astype("string")
        df_remaining["origin"] = "AI"



    #concat all df results for csv output
    df_merged = pd.concat([df_done, df_remaining], ignore_index=True).drop_duplicates()
    return df_merged

if __name__=="__main__":
    print(is_valid_year("0007"))



