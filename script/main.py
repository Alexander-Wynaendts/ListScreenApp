import pandas as pd
import io
import sys
from .data_formatting import data_formatting

def main(startup_data):
    # Capture the print outputs
    log_capture_string = io.StringIO()
    sys.stdout = log_capture_string

    # Appeler la fonction de data_formatting pour traiter les données
    startup_data = data_formatting(startup_data)

    # Capture les logs et les réinitialise
    logs = log_capture_string.getvalue()
    sys.stdout = sys.__stdout__  # Restore stdout to original

    # Retourner les logs et le DataFrame traité
    return logs, startup_data
