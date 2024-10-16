import pandas as pd
import time

from .data_formatting import data_formatting
from .website_screening import website_screen_process
from .website_analysis import website_analysis_process

import warnings
warnings.filterwarnings("ignore")

def main(startup_data):

    # Record the start time
    start_time = time.time()

    # Appeler la fonction de data_formatting pour traiter les données
    startup_data = data_formatting(startup_data)

    print(f"The process will analyse: {len(startup_data)} companies")

    # Check if the processed data is a DataFrame
    if not isinstance(startup_data, pd.DataFrame):
        return None  # Return None in case of an error

    # Perform website screening
    startup_data = website_screen_process(startup_data)

    # Perform website Analysis
    startup_data = website_analysis_process(startup_data)
    startup_data['Status'] = "To Screen"

    print(f"All companies where screen and analysed successfully")

    # Record the end time and calculate the elapsed time
    end_time = time.time()
    elapsed_time = end_time - start_time

    # Print the total time taken by the process
    print(f"Total process time: {elapsed_time:.2f} seconds")

    # Return the final processed DataFrame
    return startup_data
