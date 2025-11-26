import pandas as pd
import os

import os
import pandas as pd

class CsvBufferWriter:
    """
    A class that continuously receives (id, value) pairs,
    buffers them in an internal DataFrame, and automatically
    writes to a CSV after a certain number of rows.
    """

    def __init__(self, csv_file, columns=("id", "value"), chunk_size=10):
        self.csv_file = csv_file
        self.columns = list(columns)
        self.chunk_size = chunk_size
        self.buffer = pd.DataFrame(columns=self.columns)

        # If the file does not exist yet → create header
        if not os.path.exists(self.csv_file):
            pd.DataFrame(columns=self.columns).to_csv(self.csv_file, index=False)

    def add(self, id_value, value):
        """Add a new row and write if necessary."""
        # Append new row
        self.buffer.loc[len(self.buffer)] = [id_value, value]

        # If enough rows are collected → write
        if len(self.buffer) >= self.chunk_size:
            self.flush()

    def flush(self):
        """Write the buffer to the CSV file and clear it."""
        if not self.buffer.empty:
            self.buffer.to_csv(self.csv_file, mode="a", index=False, header=False)
            print(f"{len(self.buffer)} rows saved → {self.csv_file}")
            self.buffer = pd.DataFrame(columns=self.columns)

    def close(self):
        """Call at the end to save the remaining rows."""
        self.flush()
        print("Buffer closed and all data saved.")
