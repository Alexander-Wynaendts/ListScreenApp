import requests
from requests.auth import HTTPBasicAuth
import os

# Define your campaign name and API key
campaign_name = "Outreach Automation"
api_key = os.getenv("LEMLIST_API_KEY")

def lemlist_export(company_info):
    # URL to get the list of campaigns
    campaigns_url = "https://api.lemlist.com/api/campaigns"
    response = requests.get(campaigns_url, auth=HTTPBasicAuth('', api_key))
    campaign_lists = response.json()
    campaign_id = None
    for campaign_list in campaign_lists:
        if campaign_list.get("name", "") == campaign_name:
            campaign_id = campaign_list.get("_id", "")
            break

    # Extract company details
    company_name = company_info.get('Name', '')
    company_domain = company_info.get('Website URL', '')

    # Iterate over each contact in the company_info
    for contact in company_info.get('Contacts', []):
        first_name = contact.get('FirstName', '')
        last_name = contact.get('LastName', '')
        email = contact.get('Email', '')
        params_value = 'true' if email is None or "@" not in email else 'false'

        # Construct the API endpoint URL for each lead
        url = f"https://api.lemlist.com/api/campaigns/{campaign_id}/leads"
        params = {'findEmail': params_value, 'verifyEmail': params_value}
        payload = {"firstName": first_name, "lastName": last_name, "email": email, "companyName": company_name, "companyDomain": company_domain}
        requests.request("POST", url, auth=HTTPBasicAuth('', api_key), params=params, json=payload)

    return
