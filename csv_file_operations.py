import os
import shutil
import pandas as pd

import glob
import config

def split_csv_by_size(input_path, output_dir, max_rows=1000):
    """
    Split a CSV file into multiple smaller ones, or copy it unchanged if max_rows is None or 0.

    Args:
        input_path (str): Path to input CSV file.
        output_dir (str): Output directory for split files.
        max_rows (int or None): Maximum number of rows per chunk.
                                If None or 0 → do NOT split.
    """

    os.makedirs(output_dir, exist_ok=True)

    # --- Case 1: No splitting requested -------------------------------------
    if not max_rows:  # None, 0 or False → no splitting
        output_path = os.path.join(output_dir, f"part_1.csv")
        shutil.copy2(input_path, output_path)
        print(f"Splitter: File copied unchanged to: {output_path}")
        return

    # --- Case 2: Splitting mode ---------------------------------------------
    reader = pd.read_csv(input_path, chunksize=max_rows)
    part = 1

    for chunk in reader:
        current_file = os.path.join(output_dir, f"part_{part}.csv")
        chunk.to_csv(current_file, index=False)
        size_mb = os.path.getsize(current_file) / 1024 / 1024
        print(f"Splitter: File '{current_file}' written ({size_mb:.2f} MB)")
        part += 1

    print("Splitting finished.")



def concat_csv_files_in_new_df(input_folder_path):
    input_files = glob.glob(f"{input_folder_path}/*.csv")

    # Alle CSVs einlesen
    dfs = [pd.read_csv(file) for file in input_files]

    # Zusammenfügen
    df = pd.concat(dfs, ignore_index=True)

    # Sortieren
    df = df.sort_values("id")

    # Speichern
    df.to_csv("dla_years.csv", index=False)

    return df

def concat_csv_files_in_new_csv(input_folder_path, output_filepath):
    df = concat_csv_files_in_new_df(input_folder_path)
    df.to_csv(output_filepath, index=False)

    return output_filepath


def merge_csv_on_id(base_csv_path, additional_csv_path, column_to_add, output_csv_path):
    """
    Merge two CSVs based on 'id' and append a single column from the second CSV to the first.

    Parameters:
    - base_csv_path: Path to the main CSV file
    - additional_csv_path: Path to the CSV file with additional data
    - column_to_add: Name of the column in additional CSV to append
    - output_csv_path: Path to save the merged CSV
    """
    # Haupt-CSV einlesen
    df_base = pd.read_csv(base_csv_path)

    # Zusatz-CSV einlesen
    df_add = pd.read_csv(additional_csv_path)

    # Merge auf Basis der ID und nur die gewünschte Spalte hinzufügen
    df_merged = df_base.merge(df_add[['id', column_to_add]], on="id", how="left")

    # Ergebnis speichern
    df_merged.to_csv(output_csv_path, index=False)

    return df_merged


def verify_and_update_year(csv_path, output_path, blacklist_years=None):
    """
    Prüft die 'year'-Spalte und setzt sie ggf. auf "0", nur wenn origin == "AI":
    - 'combined' enthält "WE " + year
    - ODER 'combined' enthält "WE " + die letzten 2 Ziffern von year, 4-stellig gepaddet
    - ODER die letzten 2 Ziffern von year tauchen überhaupt nicht in combined auf
    - ODER year in blacklist_years
    """
    if blacklist_years is None:
        blacklist_years = set()  # Standard: leer

    df = pd.read_csv(csv_path)

    def check_year(row):
        if row['origin'] != "AI":
            return str(row['year'])

        year_str = str(row['year'])
        combined_str = str(row['combined'])
        last_two = year_str[-2:]
        padded_year = last_two.zfill(4)

        # Bedingungen prüfen
        if (f"WE {year_str}" in combined_str or
            f"WE {padded_year}" in combined_str or
            year_str in blacklist_years or
            last_two not in combined_str):
            return "0"
        else:
            return year_str

    df['year'] = df.apply(check_year, axis=1)

    # with or without col 'combined'
    if not config.ADD_COMBINED_ROW and 'combined' in df.columns:
        df_result = df.drop(columns=['combined'])
    else:
        df_result = df

    df_result.to_csv(output_path, index=False)
    return df_result


if __name__=="__main__":
    print("no test")
