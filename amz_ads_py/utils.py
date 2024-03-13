#python 3.11.15
## These are useful functions used in other parts of this module.
import os
import re
import pickle
from datetime import datetime, timedelta
from typing import Optional, Union


def verify_and_create_directory(directory_path:Union[str, os.PathLike])->None:
    """
    Verify if the given directory path exists, and create it if it doesn't.
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Directory '{directory_path}' created successfully.")
    elif not os.path.isdir(directory_path):
        raise ValueError(f"The given path '{directory_path}' is not a directory.")
    else:
        pass


def is_valid_month_string(month_str: str) -> bool:
    """Verifies if it is a valid month string in the format YYYY-mm 
    and the month is not greater than current month.
    """
    # Check if the string is in the format "YYYY-MM"
    if re.match(r"^\d{4}-\d{2}$", month_str):
        # Check if the month is valid
        month = int(month_str[-2:])
        year = int(month_str[:4])
        
        # Check if the month is the current month or a month in the future
        current_month = datetime.now().month
        current_year= datetime.now().year
        
        if month >= current_month and year >= current_year:
            #error
            raise ValueError("Invalid Month: current month or future date")        
        
        if month < 1 or month > 12:
            raise ValueError("Invalid month string format")
        return True  
    else:
        # Raise an error for invalid input
        raise ValueError("Invalid month string format")


def get_first_and_last_days_of_month(month: str) -> tuple:
    """Returns first and last day of any month."""
    year = int(month[:4])
    month = int(month[-2:])
    first_day = datetime(year, month, 1).strftime("%Y-%m-%d")
    
    if month == 12:
        last_day = f"{year}-12-31"
    else:    
        last_day = datetime(year, month+1, 1) - timedelta(days=1)
        last_day = last_day.strftime("%Y-%m-%d")
    return first_day, last_day


def get_start_and_end_dates(date: str, num_days: int, is_forward: bool) -> tuple:
    """Returns dates according to a date range"""
    date = datetime.strptime(date, "%Y-%m-%d")
    if is_forward:
        start_date = date
        end_date = start_date + timedelta(days=num_days - 1)
    else:
        end_date = date
        start_date = end_date - timedelta(days=num_days - 1)
    return start_date.date().strftime("%Y-%m-%d"), end_date.date().strftime("%Y-%m-%d")


def save_var(var,directory_path:Union[str, os.PathLike])->None:
    """Saves a variable in a pkl file"""   
    with open(path, 'wb') as f:
        pickle.dump(var, f, pickle.HIGHEST_PROTOCOL)
    return