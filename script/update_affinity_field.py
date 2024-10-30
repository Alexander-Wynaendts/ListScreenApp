import requests
from requests.auth import HTTPBasicAuth
import os

api_key = os.getenv("AFFINITY_API_KEY")

list_id = 219127

def update_affinity_field(company_info):

    # Clean up the website URL by removing prefixes
    website_url = company_info.get("Website URL")
    prefixes = ['https://', 'http://', 'https://www.', 'http://www.', 'www.']
    for prefix in prefixes:
        if website_url.startswith(prefix):
            website_url = website_url[len(prefix):]
            break

    # Find the organization by domain
    url = f"https://api.affinity.co/organizations?term={website_url}"
    response = requests.get(url, auth=HTTPBasicAuth('', api_key))
    organizations = response.json().get("organizations", [])
    organization_id = None
    for organization in organizations:
        if organization.get('domain') == website_url:
            organization_id = organization.get('id')
            break

    # Get the list fields
    url = f'https://api.affinity.co/lists/{list_id}'
    response = requests.get(url, auth=HTTPBasicAuth('', api_key))
    list_fields = response.json().get("fields", [])

    url = f"https://api.affinity.co/lists/{list_id}/list-entries"
    response = requests.get(url, auth=HTTPBasicAuth('', api_key))
    list_entries = response.json()
    list_entry_id = None
    for list_entry in list_entries:
        entity = list_entry.get('entity', {})
        entity_domain = entity.get('domain', '')
        if entity_domain == website_url:
            list_entry_id = list_entry.get('id')
            break

    # For each field in the list, update it with the corresponding value from company_info
    for list_field in list_fields:
        field_name = list_field.get("name")
        field_id = list_field.get("id")
        if field_name in company_info:
            new_value = company_info[field_name]
            dropdown_options = list_field.get('dropdown_options', [])
            if dropdown_options:
                dropdown_option_id = None
                for option in dropdown_options:
                    if option.get('text') == new_value:
                        new_value = option.get('id')
                        break

            # Get existing field values for the organization
            url = f"https://api.affinity.co/field-values?organization_id={organization_id}"
            response = requests.get(url, auth=HTTPBasicAuth('', api_key))
            organization_fields = response.json()
            field_value_id = None
            for field_value in organization_fields:
                try:
                    # Vérifiez d'abord le champ "field_id" et assignez "field_value_id" si c'est un match
                    if field_value.get("field_id") == field_id:
                        field_value_id = field_value.get("id")
                        break
                except Exception as e:
                    print("FIELD VALUE PROBLEM")
                    print(field_value)
                    print("Exception:", e)

            if field_value_id:
                # Update existing field value
                url = f"https://api.affinity.co/field-values/{field_value_id}"
                data = {'value': new_value}
                response = requests.put(url, auth=HTTPBasicAuth('', api_key), json=data)
            else:
                url = "https://api.affinity.co/field-values"
                data = {'field_id': field_id, 'value': new_value, 'entity_id': organization_id, 'list_entry_id': list_entry_id}
                response = requests.post(url, auth=HTTPBasicAuth('', api_key), json=data)

    return
