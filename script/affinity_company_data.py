import requests
from requests.auth import HTTPBasicAuth
import os

api_key = os.getenv("AFFINITY_API_KEY")

def affinity_company_data(body):
    # Extract list_id and list_entry_id from the body
    list_id = body.get('field', {}).get('list_id')
    list_entry_id = body.get('list_entry_id')

    # Construct the API URL to get the list entry
    url = f'https://api.affinity.co/lists/{list_id}/list-entries/{list_entry_id}'
    response = requests.get(url, auth=HTTPBasicAuth('', api_key))

    list_entry_data = response.json()

    # Get entity details from the list entry
    entity_id = list_entry_data.get('entity_id')

    # Get organization data
    organization_url = f'https://api.affinity.co/organizations/{entity_id}'
    org_response = requests.get(organization_url, auth=HTTPBasicAuth('', api_key))

    organization_data = org_response.json()
    organization_name = organization_data.get('name')
    website_url = organization_data.get('domain') or organization_data.get('url')
    person_ids = organization_data.get('person_ids', [])

    # Initialize list to store contact information
    contacts = []

    # Fetch person details for each associated person
    for person_id in person_ids:
        person_url = f'https://api.affinity.co/persons/{person_id}'
        person_response = requests.get(person_url, auth=HTTPBasicAuth('', api_key))

        person_data = person_response.json()
        first_name = person_data.get('first_name')
        last_name = person_data.get('last_name')
        primary_email = person_data.get('primary_email')

        if not primary_email:
            emails = person_data.get('emails', [])
            primary_email = emails[0] if emails else None

        contact_info = {
            'FirstName': first_name,
            'LastName': last_name,
            'Email': primary_email
        }
        contacts.append(contact_info)

    # Compile the company information
    company_info = {
        'Name': organization_name,
        'Website URL': website_url,
        'Contacts': contacts
    }

    return company_info
