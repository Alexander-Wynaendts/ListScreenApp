import pandas as pd
import time

from .data_formatting import data_formatting
from .duplicate_drop import duplicate_drop
from .website_screening import website_screen_process
from .website_analysis import website_analysis_process
from .import_affinity import import_affinity

import warnings
warnings.filterwarnings("ignore")

def main(startup_data):

    # Record the start time
    start_time = time.time()

    # Appeler la fonction de data_formatting pour traiter les données
    startup_data = data_formatting(startup_data)
    startup_data['Status'] = "To Screen"

    print(f"The process will analyse: {len(startup_data)} companies")

    # Check if the processed data is a DataFrame
    if not isinstance(startup_data, pd.DataFrame):
        return None  # Return None in case of an error

    # Not process companies in a later stage then To Screen
    startup_data = duplicate_drop(startup_data)

    # Perform website screening
    startup_data = website_screen_process(startup_data)

    # Perform website Analysis
    startup_data = website_analysis_process(startup_data)

    import_affinity(startup_data)

    print(f"All companies where screen and analysed and imported successfully")

    # Record the end time and calculate the elapsed time
    end_time = time.time()
    elapsed_time = end_time - start_time

    # Return the final processed DataFrame
    return f"Total process time: {elapsed_time:.2f} seconds"
