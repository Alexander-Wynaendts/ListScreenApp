import requests
from requests.auth import HTTPBasicAuth
import os

api_key = os.getenv("AFFINITY_API_KEY")

def add_global_to_affinity(website_url, source, inbound_boolean):
    # Fetch the organization ID by domain
    url = f"https://api.affinity.co/organizations?term={website_url}"
    response = requests.get(url, auth=HTTPBasicAuth('', api_key))
    organizations = response.json().get("organizations", [])
    organization_id = None
    for organization in organizations:
        if organization.get("domain", "") == website_url:
            organization_id = organization.get("id", "")
            break

    # Fetch field IDs for "Source" and "Inbound Boolean"
    url = f"https://api.affinity.co/organizations/fields"
    response = requests.get(url, auth=HTTPBasicAuth('', api_key))
    fields = response.json()
    field_id_source = None
    field_id_inbound = None

    for field in fields:
        if field.get("name", "") == "Source":
            field_id_source = field.get("id", "")
        elif field.get("name", "") == "Inbound Boolean":
            field_id_inbound = field.get("id", "")

    # Update the "Source" field
    url = "https://api.affinity.co/field-values"
    data_source = {"field_id": field_id_source, "entity_id": organization_id, "entity_type": "organization", "value": source}
    requests.post(url, auth=HTTPBasicAuth('', api_key), json=data_source)

    # Update the "Inbound Boolean" field
    data_inbound = {"field_id": field_id_inbound, "entity_id": organization_id, "entity_type": "organization", "value": inbound_boolean}
    requests.post(url, auth=HTTPBasicAuth('', api_key), json=data_inbound)

    return
