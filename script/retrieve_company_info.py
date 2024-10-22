import requests
from requests.auth import HTTPBasicAuth
import os

api_key = os.getenv("AFFINITY_API_KEY")

def retrieve_company_info(body):
    # Extract list_id and list_entry_id from the body
    list_id = body.get('field', {}).get('list_id')
    list_entry_id = body.get('list_entry_id')

    if not list_id or not list_entry_id:
        print("Missing list_id or list_entry_id")
        return None

    # Construct the API URL
    url = f'https://api.affinity.co/lists/{list_id}/list-entries/{list_entry_id}'
    response = requests.get(url, auth=HTTPBasicAuth('', api_key))

    data = response.json()
    # Extract "Name" and "Website URL" from the response
    entity = data.get('entity', {})

    company_info = {}
    organization_name = entity.get('name')
    website_url = entity.get('domain')
    company_info['Name'] = organization_name
    company_info['Website URL'] = website_url

    return company_info
