import pandas as pd
import io
import sys
from datetime import datetime, timedelta
from .data_formatting import data_formatting
from .website_screening import parallel_website_screening

def main(startup_data):
    # Capture the print outputs
    log_capture_string = io.StringIO()
    sys.stdout = log_capture_string

    # Appeler la fonction de data_formatting pour traiter les données
    startup_data = data_formatting(startup_data)
    startup_data = startup_data[:5]

    if not isinstance(startup_data, pd.DataFrame):
        logs = log_capture_string.getvalue()
        sys.stdout = sys.__stdout__
        return logs, None

    # Perform website screening
    startup_data = parallel_website_screening(startup_data)

    # Capture the logs and reset stdout
    logs = log_capture_string.getvalue()
    sys.stdout = sys.__stdout__  # Restore stdout to original

    # Yield the logs and final data at the end
    return logs, startup_data
