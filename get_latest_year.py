import re
from datetime import datetime
from typing import Optional


def extract_latest_year(text: str) -> Optional[str]:
    """
    Extracts the latest (most recent) year from a string based on reliable date formats.

    Only considers:
    - ISO dates: YYYY-MM-DD, YYYY/MM/DD
    - European format: DD.MM.YYYY
    - Timestamp formats: YYYYMMDD, DDMMYYYY, MMDDYYYY
    - Full datetime stamps: YYYY-MM-DD HH:MM:SS, YYYYMMDD_HHMMSS
    - Quarterly formats: Q1/25, Q2-2025, Q3 2024, 2024Q4

    Single year numbers (e.g., "2023") are ignored as they're unreliable.

    Args:
        text: Input string to search for dates

    Returns:
        The most recent year found as string, or None if no valid dates found
    """

    if not text:
        return ""

    found_years = []

    # Pattern 1: ISO format YYYY-MM-DD or YYYY/MM/DD
    iso_pattern = r'(?<!\d)(\d{4})[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])(?!\d)'
    for match in re.finditer(iso_pattern, text):
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))

        # Validate date
        try:
            datetime(year, month, day)
            if 1900 <= year <= 2100:
                found_years.append(year)
        except ValueError:
            continue

    # Pattern 2: European format DD.MM.YYYY
    european_pattern = r'(?<!\d)(0[1-9]|[12]\d|3[01])\.(0[1-9]|1[0-2])\.(19\d{2}|20\d{2})(?!\d)'
    for match in re.finditer(european_pattern, text):
        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3))

        try:
            datetime(year, month, day)
            found_years.append(year)
        except ValueError:
            continue

    # Pattern 3: YYYYMMDD format (e.g., 20231215)
    yyyymmdd_pattern = r'(?<!\d)(19\d{2}|20\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])(?!\d)'
    for match in re.finditer(yyyymmdd_pattern, text):
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))

        try:
            datetime(year, month, day)
            found_years.append(year)
        except ValueError:
            continue

    # Pattern 4: DDMMYYYY format (e.g., 15122023)
    ddmmyyyy_pattern = r'(?<!\d)(0[1-9]|[12]\d|3[01])(0[1-9]|1[0-2])(19\d{2}|20\d{2})(?!\d)'
    for match in re.finditer(ddmmyyyy_pattern, text):
        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3))

        try:
            datetime(year, month, day)
            found_years.append(year)
        except ValueError:
            continue

    # Pattern 5: MMDDYYYY format (e.g., 12152023)
    mmddyyyy_pattern = r'(?<!\d)(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])(19\d{2}|20\d{2})(?!\d)'
    for match in re.finditer(mmddyyyy_pattern, text):
        month = int(match.group(1))
        day = int(match.group(2))
        year = int(match.group(3))

        try:
            datetime(year, month, day)
            found_years.append(year)
        except ValueError:
            continue

    # Pattern 6: Datetime stamps like YYYY-MM-DD HH:MM:SS or YYYYMMDD_HHMMSS
    datetime_pattern = r'(?<!\d)(\d{4})[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])[\s_T](\d{2}):?(\d{2}):?(\d{2})(?!\d)'
    for match in re.finditer(datetime_pattern, text):
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))

        try:
            datetime(year, month, day)
            if 1900 <= year <= 2100:
                found_years.append(year)
        except ValueError:
            continue

    # Pattern 7: Quarterly formats
    # Q1/25, Q2-2025, Q3 2024, Q4/2023, etc.
    quarterly_pattern_short = r'[Qq]([1-4])[-/\s](\d{2})(?!\d)'
    for match in re.finditer(quarterly_pattern_short, text):
        quarter = int(match.group(1))
        year_short = int(match.group(2))

        # Convert 2-digit year to 4-digit (assume 20xx for 00-99)
        if year_short <= 99:
            year = 2000 + year_short
        else:
            continue

        if 1 <= quarter <= 4 and 1900 <= year <= 2100:
            found_years.append(year)

    # Q1-2025, Q2 2024, Q3/2023, etc. (4-digit year)
    quarterly_pattern_long = r'[Qq]([1-4])[-/\s](19\d{2}|20\d{2})(?!\d)'
    for match in re.finditer(quarterly_pattern_long, text):
        quarter = int(match.group(1))
        year = int(match.group(2))

        if 1 <= quarter <= 4 and 1900 <= year <= 2100:
            found_years.append(year)

    # 2024Q1, 2025Q4, etc. (year first)
    quarterly_pattern_reverse = r'(?<!\d)(19\d{2}|20\d{2})[Qq]([1-4])(?!\d)'
    for match in re.finditer(quarterly_pattern_reverse, text):
        year = int(match.group(1))
        quarter = int(match.group(2))

        if 1 <= quarter <= 4 and 1900 <= year <= 2100:
            found_years.append(year)

    # Return the most recent year found as string
    return str(max(found_years)) if found_years else ""


# Test cases
if __name__ == "__main__":
    test_cases = [
        ("report_20231215_final.pdf", "2023"),
        ("data_2022-01-01_and_2023-12-31.csv", "2023"),
        ("backup_15122023.zip", "2023"),
        ("file_12152023_important.txt", "2023"),
        ("invoice_01.12.2025.pdf", "2025"),
        ("contract_31.01.2024_signed.docx", "2024"),
        ("meeting_15.03.2022_and_20.08.2023.txt", "2023"),
        ("just 2023 here", ""),
        ("2020 2021 2022", ""),  # Only standalone years, unreliable
        ("doc_2021-06-15_updated_2023-08-20.pdf", "2023"),
        ("20200115_20220630_archive.tar", "2022"),
        ("meeting_2023-11-26 14:30:00.log", "2023"),
        ("Q1/25_report.pdf", "2025"),
        ("sales_Q4-2024.xlsx", "2024"),
        ("Q2 2023_summary.docx", "2023"),
        ("2024Q3_earnings.pdf", "2024"),
        ("Q1/22_Q4/24_comparison.xlsx", "2024"),
        ("quarterly_q2-25.txt", "2025"),
        ("1602_7.4.1_Baubeschreibung-intern_20110511.pdf 7746 WE 1602 7. Gebäude-, Grundstückszustand 7.4. Baubeschreibung 7.4.1 Baubeschreibung intern Baubeschreibung intern", "2011"),
        ("1602_7.4.1_Baubeschreibung-intern_0511.pdf 7746 WE 1602 7. Gebäude-, Grundstückszustand 7.4. Baubeschreibung 7.4.1 Baubeschreibung intern Baubeschreibung intern", ""),
        ("", ""),
    ]

    print("Testing extract_latest_year():\n")
    for text, expected in test_cases:
        result = extract_latest_year(text)
        status = "OK" if result == expected else "ERROR"
        print(f"{status} Input: '{text}'")
        print(f"  Expected: {expected}, Got: {result}\n")