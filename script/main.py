import pandas as pd
import asyncio

from .data_formatting import data_formatting
from .website_screening import website_sreen_process
from .website_analysis import website_analysis_process

import warnings
warnings.filterwarnings("ignore")

async def main(startup_data):

    # Appeler la fonction de data_formatting pour traiter les données
    startup_data = data_formatting(startup_data)

    # Check if the processed data is a DataFrame
    if not isinstance(startup_data, pd.DataFrame):
        return None  # Return None in case of an error

    # Perform website screening
    startup_data = await website_sreen_process(startup_data)

    print(startup_data.head())

    # Perform website Analysis
    startup_data = website_analysis_process(startup_data)

    # Return the final processed DataFrame
    return startup_data
