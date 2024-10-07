import argparse

from data_formatting import data_formatting

#parser = argparse.ArgumentParser(description='Process a CSV file.')
#parser.add_argument('file_name', type=str, help='Path to the input CSV file')

#args = parser.parse_args()
#file_name = args.file_name

file_name = "BE_clean.csv"

startup_data = data_formatting(file_name)
