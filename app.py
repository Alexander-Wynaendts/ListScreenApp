from flask import Flask, request

from script.affinity_company_data import affinity_company_data
from script.website_scraping import website_scraping
from script.lemlist_export import lemlist_export
from script.gmail_inbound import gmail_inbound
from script.company_import_affinity import company_import_affinity

app = Flask(__name__)

@app.route('/affinity-webhook', methods=['POST'])
def affinity_webhook():
    if request.method == 'POST':
        data = request.json

        # Check for organization.created event
        if data.get('type') == 'organization.created':
            body = data.get('body', {})
            website_url = body.get('domain', '')  # Adjust if there's another field for website URL

            website_data = website_scraping(website_url)
            #company_screened = website_analysis(website_data)
            #company_import_affinity(company_screened)
            #company_screened['Status'] = "To Screen"
            print(f"New company: {website_data}")

        # Check for field_value.updated event and the status field
        if data.get('type') == 'field_value.updated':
            body = data.get('body', {})
            field_name = body.get('field', {}).get('name', '')
            if field_name == 'Status':
                if body.get('value', {}).get('text', '') is None or body.get('value', {}).get('text', '') == "New":
                    entry_data = affinity_company_data(body)
                    webiste_url = entry_data.get("Website URL")

                    website_data = website_scraping(webiste_url)
                    #company_screened = website_analysis(website_data)
                    #company_import_affinity(company_screened)
                    #company_screened['Status'] = "To Screen"
                    print(f'Status New: {website_data}')

                if body.get('value', {}).get('text', '') == 'To be contacted':
                    entry_data = affinity_company_data(body)
                    company_info = entry_data
                    #lemlist_export(company_info)
                    print(f'Status To be contacted: {company_info}')

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

        webiste_url = email_info.get("Website URL")

        website_data = website_scraping(webiste_url)
        #company_screened = website_analysis(website_data)
        #company_import_affinity(company_screened)
        #company_screened['Status'] = "To Screen"

        print(f"New company out of email: {website_data}")

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
                selected_option_ids = value
                options = field.get('options', [])
                selected_options = [opt['text'] for opt in options if opt['id'] in selected_option_ids]
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

        website_url = formulair_info.get("Website URL")

        website_data = website_scraping(website_url)
        #company_screened = website_analysis(website_data)
        #company_import_affinity(company_screened)
        #company_screened['Status'] = "To Screen"
        print(f"New form submission: {website_data}")

    return "Formulair webhook received and processed", 200

@app.route('/fireflies-webhook', methods=['POST'])
def fireflies_webhook():
    if request.method == 'POST':
        data = request.json

        #transcript_data =
        #fireflies_import_affinity()

        print(f"New transcript from Fireflies: {data}")

    return "Fireflies webhook received and processed", 200

if __name__ == '__main__':
    app.run(debug=True)
