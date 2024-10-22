import requests
from requests.auth import HTTPBasicAuth
import os

api_key = os.getenv("AFFINITY_API_KEY")

list_id = 271745

def get_organization_by_domain(website_url):
    # Search for the organization by domain
    url = f"https://api.affinity.co/organizations?term={website_url}"
    response = requests.get(url, auth=HTTPBasicAuth('', api_key))
    organizations = response.json().get('organizations', [])
    for organization in organizations:
        if organization.get('domain') == website_url:
            return organization.get('id')
    return None

def create_organization(name, website_url):
    url = "https://api.affinity.co/organizations"
    data = {'name': name, 'domain': website_url}
    response = requests.post(url, auth=HTTPBasicAuth('', api_key), json=data)

    organization = response.json()
    organization_id = organization.get('id')
    return organization_id

def check_list_entry_exists(organization_id):
    url = f"https://api.affinity.co/lists/{list_id}/list-entries"
    response = requests.get(url, auth=HTTPBasicAuth('', api_key))
    list_entries = response.json()
    for entry in list_entries:
        if entry.get('entity_id') == organization_id:
            return True
    return False

def create_list_entry(organization_id):
    url = f"https://api.affinity.co/lists/{list_id}/list-entries"
    data = {'entity_id': organization_id}
    requests.post(url, auth=HTTPBasicAuth('', api_key), json=data)
    return

def add_company_to_affinity(name, website_url):

    prefixes = ['https://', 'http://', 'https://www.', 'http://www.', 'www.']
    for prefix in prefixes:
        if website_url.startswith(prefix):
            website_url = website_url[len(prefix):]
            break

    # First, check if the organization exists
    organization_id = get_organization_by_domain(website_url)
    if organization_id:
        if check_list_entry_exists(organization_id):
            return
        else:
            create_list_entry(organization_id)
            return
    else:
        organization_id = create_organization(name, website_url)
        create_list_entry(organization_id)
        return
