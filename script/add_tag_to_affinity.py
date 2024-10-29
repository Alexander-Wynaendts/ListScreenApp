import requests
from requests.auth import HTTPBasicAuth
import os

api_key = os.getenv("AFFINITY_API_KEY")

def add_tag_to_affinity(website_url, tag):

    url = f"https://api.affinity.co/organizations?term={website_url}"
    response = requests.get(url, auth=HTTPBasicAuth('', api_key))
    organizations = response.json().get("organizations", [])
    organization_id = None
    for organization in organizations:
        if organization.get("domain", "") == website_url:
            organization_id = organization.get("id", "")
            break

    url = f"https://api.affinity.co/organizations/fields"
    response = requests.get(url, auth=HTTPBasicAuth('', api_key))
    fields = response.json()
    for field in fields:
        if field.get("name", "") == "Source":
            field_id = field.get("id", "")
            break

    url = "https://api.affinity.co/field-values"
    data = {"field_id": field_id, "entity_id": organization_id, "entity_type": "organization", "value": tag}
    requests.post(url, auth=HTTPBasicAuth('', api_key), json=data)

    return
