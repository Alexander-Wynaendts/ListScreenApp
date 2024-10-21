import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("AFFINITY_API_KEY")

# Function to get field values for a specific list entry
def get_field_values(entity_id):
    url = f"https://api.affinity.co/field-values?organization_id={entity_id}"
    response = requests.get(url, auth=HTTPBasicAuth('', api_key))
    return response.json()

# Function to drop duplicates based on the "Website URL" and "Status"
def duplicate_drop(startup_data):

    # Fetch list entries from the API
    url = f"https://api.affinity.co/lists/271745/list-entries"
    response = requests.get(url, auth=HTTPBasicAuth('', api_key))
    list_entries = response.json()

    # Create a set of unique "Website URL" values from startup_data for faster lookup
    startup_domains = set(startup_data["Website URL"].str.replace("https://www.", "").str.replace("https://", "").str.replace("http://", "").str.replace("http://www.", "").str.replace("/", ""))

    # Keep track of rows to drop
    rows_to_drop = []

    # Loop through list entries and match only entries with a domain in startup_domains
    for entry in list_entries:
        domain = entry['entity'].get('domain', None)  # Get the domain if it exists
        entry_id = entry['entity_id']

        if domain and domain in startup_domains:
            field_values = get_field_values(entry_id)
            status_field = next((field for field in field_values if field.get('field_id') == 4768744), None)
            value = status_field.get('value')
            if isinstance(value, dict) and value.get('text') not in ["New", "Lead", None]:
                row_index = startup_data[startup_data["Website URL"].str.contains(domain)].index
                rows_to_drop.extend(row_index)

    # Drop rows from startup_data
    startup_data = startup_data.drop(rows_to_drop)

    return startup_data
