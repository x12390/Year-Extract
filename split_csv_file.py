import os
import shutil
import pandas as pd

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
        print(f"File copied unchanged to: {output_path}")
        return

    # --- Case 2: Splitting mode ---------------------------------------------
    reader = pd.read_csv(input_path, chunksize=max_rows)
    part = 1

    for chunk in reader:
        current_file = os.path.join(output_dir, f"part_{part}.csv")
        chunk.to_csv(current_file, index=False)
        size_mb = os.path.getsize(current_file) / 1024 / 1024
        print(f"File '{current_file}' written ({size_mb:.2f} MB)")
        part += 1

    print("Splitting finished.")
