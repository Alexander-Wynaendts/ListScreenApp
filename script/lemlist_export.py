import requests
from requests.auth import HTTPBasicAuth
import os

# Define your API key
api_key = os.getenv("LEMLIST_API_KEY")

def lemlist_export(company_info, campaign):
    # Determine the campaign name based on input
    if campaign == "Inbound":
        campaign_name = "Inbound Automation"
        linkedin_params_value = 'false'
    elif campaign == "Outbound":
        campaign_name = "Outbound Automation"
        linkedin_params_value = 'true'
    elif campaign == "Rejected":
        campaign_name = "Inbound Rejected"
        linkedin_params_value = 'false'

    # URL to get the list of campaigns
    campaigns_url = "https://api.lemlist.com/api/campaigns"
    response = requests.get(campaigns_url, auth=HTTPBasicAuth('', api_key))
    campaign_lists = response.json()
    campaign_id = None

    # Find the campaign ID based on the campaign name
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
        email_params_value = 'true' if email is None or "@" not in email else 'false'

        # Construct the API endpoint URL for each lead
        url = f"https://api.lemlist.com/api/campaigns/{campaign_id}/leads"
        params = {'findEmail': email_params_value, 'verifyEmail': email_params_value, 'linkedinEnrichment': linkedin_params_value}
        payload = {
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "companyName": company_name,
            "companyDomain": company_domain
        }
        requests.post(url, auth=HTTPBasicAuth('', api_key), params=params, json=payload)

    return
