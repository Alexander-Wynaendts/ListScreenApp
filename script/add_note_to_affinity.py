import requests
from requests.auth import HTTPBasicAuth
import os

api_key = os.getenv("AFFINITY_API_KEY")

def add_note_to_affinity(website_url, note_content):
    # Fetch the organization by its website URL
    url = f"https://api.affinity.co/organizations?term={website_url}"
    response = requests.get(url, auth=HTTPBasicAuth('', api_key))
    organizations = response.json().get("organizations", [])
    organization_id = None
    for organization in organizations:
        if organization.get("domain", "") == website_url:
            organization_id = organization.get("id", "")
            break

    # Fetch existing notes for the organization
    url = "https://api.affinity.co/notes"
    response = requests.get(url, auth=HTTPBasicAuth('', api_key))
    notes = response.json().get("notes", [])
    note_exists = False
    note_id = None

    # Check if any note exists for this organization
    for note in notes:
        if organization_id in note.get("organization_ids", []):
            note_exists = True
            note_id = note.get("id", "")
            break

    if note_exists and note_id:
        print("Update")
        # Update the existing note
        update_url = f"https://api.affinity.co/notes/{note_id}"
        data = {'content': note_content}
        response = requests.put(update_url, auth=HTTPBasicAuth('', api_key), json=data)
        print(response)
    else:
        print("CREATING")
        # Create a new note if no existing note is found
        create_url = "https://api.affinity.co/notes"
        data = {'content': note_content, 'type': 2, 'organization_ids': [organization_id]}
        response = requests.post(create_url, auth=HTTPBasicAuth('', api_key), json=data)
        print(response)

    return
