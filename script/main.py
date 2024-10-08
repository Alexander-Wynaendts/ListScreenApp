import pandas as pd
from .data_formatting import data_formatting
from .website_screening import parallel_website_screening
from .website_analysis import parallel_website_analysis

def main(startup_data):
    # Appeler la fonction de data_formatting pour traiter les données
    startup_data = data_formatting(startup_data)

    # Keep only the first 5 rows for processing
    startup_data = startup_data[:2]

    # Check if the processed data is a DataFrame
    if not isinstance(startup_data, pd.DataFrame):
        return None  # Return None in case of an error

    # Perform website screening
    startup_data = parallel_website_screening(startup_data)

    # Perform website Analysis
    startup_data = parallel_website_analysis(startup_data)

    # Return the final processed DataFrame
    return startup_data
