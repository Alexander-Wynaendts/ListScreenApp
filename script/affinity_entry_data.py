import requests
from requests.auth import HTTPBasicAuth
import os

api_key = os.getenv("AFFINITY_API_KEY")

def affinity_entry_data(body):
    # Extract list_id and list_entry_id from the body
    list_id = body.get('field', {}).get('list_id')
    list_entry_id = body.get('list_entry_id')

    # Construct the API URL to get the list entry
    url_entry = f'https://api.affinity.co/lists/{list_id}/list-entries/{list_entry_id}'
    response_entry = requests.get(url_entry, auth=HTTPBasicAuth('', api_key))

    # Use the field-values endpoint with the list_entry_id
    url_field_values = f'https://api.affinity.co/field-values?list_entry_id={list_entry_id}'
    response_field_values = requests.get(url_field_values, auth=HTTPBasicAuth('', api_key))

    field_values = response_field_values.json()
    print("Field Values Data:")
    print(field_values)

    # Prepare the company_info dictionary
    company_info = {}
    #organization_name = entity.get('name')
    #website_url = entity.get('domain') or entity.get('url')
    #company_info['Name'] = organization_name
    #company_info['Website URL'] = website_url

    return company_info
