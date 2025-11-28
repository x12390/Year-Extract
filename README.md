# Extraction of Years

For searching for years in large CSV files with many columns and an ID at the beginning of each row. The search is divided into two parts: a rule-based search that interprets known date formats and timestamps and returns the year in the format YYYY if found. If the rule-based search returns no result, the entry is passed to a local AI. The AI-assisted search fills in missing year values if it identifies any.

## Local AI
An already installed LM Studio with the appropriate model is required. To run the code, LM Studio must be running on the same machine and the model must already be loaded.

Recommended model: __mistralai/mistral-nemo-instruct-2407__


## Installation

1. clone repository:
   ```bash
   git clone https://github.com/x12390/Year-Extract.git
   
   cd Year-Extract
   
   pip install -r requirements.txt  

## Usage
You need a CSV file that contains a unique ID in the first column.

* Copy the CSV file into the data folder

* Run main.py

* It will extract the latest year (YYYY) from all columns in each row

* The result will be a new CSV file in the output folder

* Since the AI is not 100% accurate, you can use generate_shipping.py for cleanup (but you may need to modify it to suit your needs)