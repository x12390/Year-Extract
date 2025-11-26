# Extraction of Years

For searching for years in large CSV files with many columns and an ID at the beginning of each row. The search is divided into two parts: a rule-based search that interprets known date formats and timestamps and returns the year in the format YYYY if found. If the rule-based search returns no result, the entry is passed to a local AI. The AI-assisted search fills in missing year values if it identifies any.

## Local AI
LM Studio with mistralai/mistral-nemo-instruct-2407