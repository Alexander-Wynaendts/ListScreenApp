import requests
from requests.auth import HTTPBasicAuth
import os

api_key = os.getenv("AFFINITY_API_KEY")

def add_people_to_affinity(first_name, last_name, email, website_url):
    # Clean up the website URL by removing common prefixes
    prefixes = ['https://', 'http://', 'https://www.', 'http://www.', 'www.']
    for prefix in prefixes:
        if website_url.startswith(prefix):
            website_url = website_url[len(prefix):]
            break

    # Search for the organization by domain
    url = f"https://api.affinity.co/organizations?term={website_url}"
    response = requests.get(url, auth=HTTPBasicAuth('', api_key))
    organizations = response.json().get("organizations", [])
    organization_id = None
    for organization in organizations:
        if organization.get('domain') == website_url:
            organization_id = organization.get("id")
            break

    # Check if the person already exists by email
    url = f"https://api.affinity.co/persons?term={email}"
    response = requests.get(url, auth=HTTPBasicAuth('', api_key))
    persons = response.json().get("persons", [])
    if not persons:
        url = "https://api.affinity.co/persons"
        data = {
            "first_name": first_name,
            "last_name": last_name,
            "emails": [email],
            "organization_ids": [organization_id]
        }
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url, auth=HTTPBasicAuth('', api_key), json=data, headers=headers)
    return
