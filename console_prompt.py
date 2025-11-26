import threading
import time
from typing import Optional

def ask_yes_no(question: str) -> bool:
    """
    Ask the user a yes/no question and return True for yes, False for no.
    """
    while True:
        answer = input(f"{question} (y/n): ").strip().lower()

        if answer in ("y", "yes"):
            return True
        elif answer in ("n", "no"):
            return False
        else:
            print("Please enter 'y' or 'n'.")



if __name__=="__main__":
    print("Type 'n' to abort or wait...")
