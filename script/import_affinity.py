import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

load_dotenv()
# API key and base URL
api_key = os.getenv("AFFINITY_API_KEY")  # Load API key from environment variable
base_url = "https://api.affinity.co"
list_id = 271745

# Field ID mapping
field_mapping = {
    'Status': 4768744,
    'GPT Description': 4769046
}

dropdown_fields = [4768744]
dropdown_value_to_id = {
    'New': 16696433,
    'To Screen': 16671075,
    'Rejected': 16696436
}

# Function to search for an organization by domain
def search_organization(domain):
    url = f"{base_url}/organizations?term={domain}"
    response = requests.get(url, auth=HTTPBasicAuth('', api_key))
    organizations = response.json().get('organizations', [])

    # Return the ID of the first organization matching the domain
    for org in organizations:
        if org['domain'] == domain:
            return org['id']
    return None

# Function to create a new organization
def create_organization(company_name, domain):
    url = f"{base_url}/organizations"
    payload = {
        "name": company_name,
        "domain": domain
    }
    response = requests.post(url, json=payload, auth=HTTPBasicAuth('', api_key), headers={"Content-Type": "application/json"})
    org_id = response.json().get('id')
    return org_id

# Function to check if an organization is already in the list
def is_organization_in_list(list_entries, organization_id):
    for entry in list_entries:
        if entry['entity_id'] == organization_id:
            return True
    return False

# Function to create a new list entry
def create_list_entry(entity_id):
    # Create a new list entry
    url = f"{base_url}/lists/{list_id}/list-entries"
    payload = {"entity_id": entity_id}
    response = requests.post(url, json=payload, auth=HTTPBasicAuth('', api_key), headers={"Content-Type": "application/json"})
    return response.json().get('id')

def get_list_entry_id(list_entries, organization_id):
    for entry in list_entries:
        if entry['entity_id'] == organization_id:
            return entry['id']
    new_entry_id = create_list_entry(organization_id)
    if new_entry_id:
        return new_entry_id

def get_field_value_id(entity_id, list_entry_id, field_id):
    url = f"{base_url}/field-values?organization_id={entity_id}"
    response = requests.get(url, auth=HTTPBasicAuth('', api_key))
    field_values = response.json()

    # Look for the specific field value
    for field_value in field_values:
        if field_value.get('field_id') == field_id and field_value.get('list_entry_id') == list_entry_id:
            field_value_id = field_value['id']
            return field_value_id
    return None

# Function to create a new field value if it doesn't exist
def create_field_value(entity_id, field_id, value, list_entry_id=None):
    url = f"{base_url}/field-values"
    payload = {
        "entity_id": entity_id,
        "field_id": field_id,
        "value": value,
        "list_entry_id": list_entry_id
    }
    response = requests.post(url, json=payload, auth=HTTPBasicAuth('', api_key), headers={"Content-Type": "application/json"})

# Function to update field value
def update_field_value(field_value_id, value, is_dropdown):
    url = f"{base_url}/field-values/{field_value_id}"
    if is_dropdown:
        payload = {"value": {"id": str(value)}}
    else:
        payload = {"value": str(value)}
    response = requests.put(url, json=payload, auth=HTTPBasicAuth('', api_key), headers={"Content-Type": "application/json"})
    print(response.json())

# Function to process startup_data
def import_affinity(startup_data):
    # Fetch the list entries once before processing
    url = f"{base_url}/lists/{list_id}/list-entries"
    response = requests.get(url, auth=HTTPBasicAuth('', api_key))
    list_entries = response.json()

    for index, row in startup_data.iterrows():
        # Get the company name and domain
        company_name = row.get('Name')
        domain = row.get('Website URL').replace("https://", "").replace("http://", "").replace("www.", "").replace("/", "")

        # Check if the organization exists by domain
        organization_id = search_organization(domain)

        # If organization doesn't exist, create it
        if not organization_id:
            organization_id = create_organization(company_name, domain)

        # Retrieve or create list entry ID
        list_entry_id = get_list_entry_id(list_entries, organization_id)

        # Update all fields for the organization
        for column, field_id in field_mapping.items():
            if column in row and pd.notna(row[column]):

                # Get the field value ID if it exists
                field_value_id = get_field_value_id(organization_id, list_entry_id, field_id)

                # Check if the field requires an ID (like a dropdown) or a free-text value
                value = row[column]
                if field_id in dropdown_fields:  # Handle dropdown fields that require IDs
                    dropdown_id = dropdown_value_to_id.get(value, None)
                    if field_value_id:
                        update_field_value(field_value_id, dropdown_id, is_dropdown=True)
                    else:
                        create_field_value(organization_id, field_id, dropdown_id, list_entry_id)
                else:
                    # For free-text or other fields, just update or create the field value
                    if field_value_id:
                        update_field_value(field_value_id, value, is_dropdown=False)
                    else:
                        create_field_value(organization_id, field_id, value, list_entry_id)

    return f"Processing of {startup_data.shape[0]} entries completed."
