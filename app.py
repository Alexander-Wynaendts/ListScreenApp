from flask import Flask, request

from script.company_screening import company_screening
from script.outreach_export import outreach_export
from script.gmail_inbound import gmail_inbound
from script.formulair_inbound import formulair_inbound
from script.import_affinity import import_affinity

app = Flask(__name__)

@app.route('/affinity-webhook', methods=['POST'])
def affinity_webhook():
    if request.method == 'POST':
        data = request.json

        # Check for organization.created event
        if data.get('type') == 'organization.created':
            body = data.get('body', {})
            name = body.get('name', '')
            website_url = body.get('domain', '')  # Adjust if there's another field for website URL

            # Store in a dictionary
            company_info = {'Name': name, 'Website URL': website_url}

            # Run the list_screening function
            company_screened  = company_screening(company_info)

        # Check for field_value.updated event and the status field
        if data.get('type') == 'field_value.updated':
            body = data.get('body', {})
            field_name = body.get('field', {}).get('name', '')
            field_value = body.get('value', {}).get('text', '')

            if field_name == 'Status' and (field_value is None or field_value == 'New'):
                company_screened = company_screening(company_info)

            if field_name == 'Status' and field_value == 'To be contacted':
                outreach_export(company_info)

        import_affinity(company_screened)

        return "Affinity webhook received and processed", 200

@app.route('/gmail-webhook', methods=['POST'])
def affinity_webhook():
    if request.method == 'POST':
        data = request.json


    return "Gmail webhook received and processed", 200

@app.route('/formulair-webhook', methods=['POST'])
def affinity_webhook():
    if request.method == 'POST':
        data = request.json
        print(data)

    return "formulair webhook received and processed", 200


if __name__ == '__main__':
    app.run(debug=True)
