import os
import config
from datetime import datetime
from csv_file_operations import concat_csv_files_in_new_csv, merge_csv_on_id, verify_and_update_year



def main():
    print("Generate shipping files.")
    timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs(config.SHIPPING_DIR, exist_ok=True)

    # BASEFILE: concat splitted files form output folder => compiled.csv
    csv_base_file = os.path.join("tmp", "compiled_output_files.csv")
    concat_csv_files_in_new_csv(config.OUTPUT_DIR, csv_base_file)

    # ADDITIONAL FILE: get csv with combined value columns
    csv_add_file = os.path.join("tmp", "selected_combined_meta_cols.csv")

    # merge basefile with addtional file (pk is id column) => SHIPPING FILE WITHOUT CLEANUP
    merged_file = os.path.join(config.SHIPPING_DIR, f"{timestamp_str}_{config.SHIPPING_FILENAME}_raw.csv")
    df_merged = merge_csv_on_id(csv_base_file, csv_add_file, "combined", merged_file)
    print(f"SHIPPING FILE 1: {merged_file} (raw results), {len(df_merged)}) rows")

    # verify and cleanup shipping file
    # The AI is not 100% accurate; it recognizes some known years even though the data does not contain them.
    blacklist_years = {"1900", "2025", "2027", "2029", "2031", "2032", "2033", "2037", "2039", "2040", "2093", "2100"}
    verfied_file = os.path.join(config.SHIPPING_DIR, f"{timestamp_str}_{config.SHIPPING_FILENAME}_verified.csv")
    df_verified = verify_and_update_year(merged_file, verfied_file, blacklist_years=blacklist_years)
    print(f"SHIPPING FILE 2: {verfied_file} (verified, recommended), {len(df_verified)}) rows")

if __name__=="__main__":
  main()