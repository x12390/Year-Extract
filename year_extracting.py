import pandas as pd
import re
import os



# Function to extract the latest year from text
def extract_latest_year(text):

    if pd.isna(text):
        print("Ist kein Text.")
        return "na"

    text = str(text)


    # Regex:
    # - Jahreszahlen: 2010, 2025 (nicht direkt nach "WE ")
    # - Quartalsangaben: Q1/25 oder Q1/2025
    # Negative Lookbehind: (?<!WE\s) verhindert Treffer nach "WE "
    pattern = r"(?<!WE\s)\b(?:19|20)\d{2}\b|\bQ[1-4]/\d{2,4}\b"
    matches = re.findall(pattern, text)

    years = []
    for m in matches:
        if m.startswith("Q"):
            # Quartalsangabe -> Jahr ergänzen
            part = m.split("/")[1]
            if len(part) == 2:  # z.B. '25' -> '2025'
                year = "20" + part
            else:  # z.B. '2025'
                year = part
            years.append(year)
        else:
            years.append(m)

    if years:
        #print(years)
        max_year = max(years)
        #print(f"Choice: {max_year}")  # ['2025', '2025', '2010', '2025']
        if max_year:
            if int(max_year) < 1980:
                print(f"{max_year} => {years}")

        return max_year
    else:
        return "na"


def extracting_year_and_write_csv(df, output_dir):
    # Apply function
    df['year'] = df['combined'].apply(extract_latest_year)

    # Output CSV
    output_df = df[['id', 'year']]
    output_file = os.path.join(output_dir, "id_year_extracted.csv")
    output_df.to_csv(output_file, index=False)
    return output_file



