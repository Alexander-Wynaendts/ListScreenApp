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

        print(data)

        # Check for organization.created event
        if data.get('type') == 'organization.created':
            body = data.get('body', {})
            name = body.get('name', '')
            website_url = body.get('domain', '')  # Adjust if there's another field for website URL

            # Store in a dictionary
            company_info = {'Name': name, 'Website URL': website_url}

            # Run the list_screening function
            #company_screened  = company_screening(company_info)
            print(f"New company to process: {company_info}")

        # Check for field_value.updated event and the status field
        if data.get('type') == 'field_value.updated':
            body = data.get('body', {})
            field_name = body.get('field', {}).get('name', '')
            field_value = body.get('value', {}).get('text', '')

            if field_name == 'Status' and (field_value is None or field_value == 'New'):
                #company_screened = company_screening(company_info)
                print(f"New company to process: {company_info}")

            if field_name == 'Status' and field_value == 'To be contacted':
                #outreach_export(company_info)
                print(f"New company to process: {company_info}")

        #import_affinity(company_screened)

        return "Affinity webhook received and processed", 200

@app.route('/gmail-webhook', methods=['POST'])
def gmail_webhook():
    if request.method == 'POST':
        data = request.json

        sender = data.get('from', '')
        subject = data.get('subject', '')
        plain_body = data.get('plainBody', '')
        html_body = data.get('htmlBody', '')

        email_info = {'sender': sender, 'subject': subject, 'plain_body': plain_body, 'html_body': html_body}
        email_info = gmail_inbound(email_info)

        company_info = { "Name": email_info.get("Name"), "Website URL": email_info.get("Website URL") }

        print(f"New company out of email: {company_info}")

    return "Gmail webhook received and processed", 200

@app.route('/formulair-webhook', methods=['POST'])
def formulair_webhook():
    if request.method == 'POST':
        data = request.json

        # Access the 'fields' array from the data
        fields = data.get('data', {}).get('fields', [])

        # Initialize a dictionary to store extracted information
        formulair_info = {
            'first_names': [],
            'last_names': [],
            'emails': []
        }

        # Loop through each field and extract key information
        for field in fields:
            label = field.get('label')
            value = field.get('value')
            field_type = field.get('type')

            if label in ['First name', 'Please allow us to contact you!']:
                if value:
                    formulair_info['first_names'].append(value)
            elif label == 'Last Name':
                if value:
                    formulair_info['last_names'].append(value)
            elif label == 'Email':
                if value:
                    formulair_info['emails'].append(value)
            elif label == 'What is you company name?':
                formulair_info['Name'] = value
            elif label == 'Are you a B2B SaaS company?':
                # Handle multiple-choice field
                selected_option_ids = value
                options = field.get('options', [])
                selected_options = [opt['text'] for opt in options if opt['id'] in selected_option_ids]
                # Extract the first option as a string
                formulair_info['b2b_saas'] = selected_options[0] if selected_options else None
            elif label == 'In what industry are you operating?':
                formulair_info['industry'] = value
            elif label == 'What does your startup do?':
                formulair_info['startup_description'] = value
            elif label == 'Add the Link to your Website':
                formulair_info['Website URL'] = value
            elif label == 'Where is your company based?':
                formulair_info['company_location'] = value
            elif label == 'What kind of funding round are you raising?':
                selected_option_ids = value
                options = field.get('options', [])
                selected_options = [opt['text'] for opt in options if opt['id'] in selected_option_ids]
                formulair_info['funding_round'] = selected_options[0] if selected_options else None
            elif label == 'How much are you expecting to raise?':
                formulair_info['funding_amount'] = value
            elif label == 'Roughly when do you plan on closing this round?':
                formulair_info['funding_close_date'] = value
            elif field_type == 'FILE_UPLOAD':
                files = value
                if files:
                    file_url = files[0]['url']
                    formulair_info['uploaded_file'] = file_url
                else:
                    formulair_info['uploaded_file'] = None

        company_info = { "Name": formulair_info.get("Name"), "Website URL": formulair_info.get("Website URL") }
        print(f"New form submission: {company_info}")

    return "Formulair webhook received and processed", 200

if __name__ == '__main__':
    app.run(debug=True)
