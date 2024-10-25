from flask import Flask, request

from script.gmail_inbound import gmail_inbound
from script.affinity_company_data import affinity_company_data
from script.website_scraping import website_scraping
from script.website_analysis import website_analysis
from script.add_company_to_affinity import add_company_to_affinity
from script.add_people_to_affinity import add_people_to_affinity
from script.update_affinity_field import update_affinity_field
from script.formulaire_note import formulaire_note
from script.add_note_to_affinity import add_note_to_affinity
from script.add_tag_to_affinity import add_tag_to_affinity
from script.lemlist_export import lemlist_export

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
            website_url = body.get('domain', '')

            website_data = website_scraping(website_url)
            company_screened = website_analysis(website_data)
            company_screened["Website URL"] = website_url
            company_screened['Status'] = "To Screen"

            update_affinity_field(company_screened)

            print(f"New company: {website_url}")

        # Check for field_value.updated event and the status field
        if data.get('type') == 'field_value.updated':
            body = data.get('body', {})
            field_name = body.get('field', {}).get('name', '')
            if field_name == 'Status':
                if body.get('value', {}).get('text', '') is None or body.get('value', {}).get('text', '') == "New":
                    entry_data = affinity_company_data(body)
                    website_url = entry_data.get("Website URL")
                    print(website_url)

                    website_data = website_scraping(website_url)
                    company_screened = website_analysis(website_data)
                    company_screened["Website URL"] = website_url
                    company_screened['Status'] = "To Screen"

                    update_affinity_field(company_screened)

                    print(f'Status "New" update: {website_url}')

                if body.get('value', {}).get('text', '') == 'To be contacted':
                    entry_data = affinity_company_data(body)
                    company_info = entry_data
                    lemlist_export(company_info)

                    website_url = company_info.get("Website URL", "")
                    status_update = {"Website URL": website_url, "Status": "In Email Flow"}
                    update_affinity_field(status_update)

                    website_url = company_info.get("Website URL", "")
                    print(f'Status "To be contacted": {website_url}')

        return "Affinity webhook received and processed", 200

@app.route('/gmail-webhook', methods=['POST'])
def gmail_webhook():
    try:
        if request.method == 'POST':
            data = request.json

            sender = data.get('from', '')
            subject = data.get('subject', '')
            plain_body = data.get('plainBody', '')
            html_body = data.get('htmlBody', '')

            email_info = {'sender': sender, 'subject': subject, 'plain_body': plain_body, 'html_body': html_body}
            email_info = gmail_inbound(email_info)

            first_name = email_info.get("First Name")
            last_name = email_info.get("Last Name")
            email = email_info.get("Email")

            name = email_info.get("Name")
            website_url = email_info.get("Website URL")
            email_content = email_info.get("Email Content")

            if website_url != "":
                add_company_to_affinity(name, website_url)
                add_note_to_affinity(website_url, email_content)
                add_tag_to_affinity(website_url, "Gmail Inbound")

                add_people_to_affinity(first_name, last_name, email, website_url)

                print(f"New company out of email: {website_url}")
            return "Success", 200
        else:
            return "Method not allowed", 405
    except Exception as e:
        app.logger.error(f"Error processing the webhook: {str(e)}")
        return "Internal Server Error", 500

@app.route('/formulair-webhook', methods=['POST'])
def formulair_webhook():
    if request.method == 'POST':
        data = request.json

        # Access the 'fields' array from the data
        fields = data.get('data', {}).get('fields', [])

        # Initialize a dictionary to store extracted information
        formulair_info = {'first_names': [], 'last_names': [], 'emails': []}

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

        name = formulair_info.get("Name")
        website_url = formulair_info.get("Website URL")
        first_names = formulair_info.get("first_names", [])
        last_names = formulair_info.get("last_names", [])
        emails = formulair_info.get("emails", [])

        # Add company to Affinity using name and website_url
        add_company_to_affinity(name, website_url)

        # Iterate over the first_names, last_names, and emails lists
        for first_name, last_name, email in zip(first_names, last_names, emails):
            add_people_to_affinity(first_name, last_name, email, website_url)

        note_content = formulaire_note(formulair_info)
        add_note_to_affinity(website_url, note_content)
        add_tag_to_affinity(website_url, "Form Inbound")

        print(f"New form submission: {website_url}")

    return "Form webhook received and processed", 200

@app.route('/fireflies-webhook', methods=['POST'])
def fireflies_webhook():
    if request.method == 'POST':
        data = request.json

        #transcript_data =
        #fireflies_import_affinity()

        print(f"New transcript from Fireflies: {data}")

    return "Fireflies webhook received and processed", 200

@app.route('/lemlist-webhook', methods=['POST'])
def lemlist_webhook():
    if request.method == 'POST':
        data = request.json

        website_url = data.get("companyDomain", "")
        company_status = "Contacted"

        company_udpate = {"Website URL": website_url, "Status": company_status}
        update_affinity_field(company_udpate)

        print(f"Lemlist email flow running: {website_url}")

    return "Lemlist webhook received and processed", 200

if __name__ == '__main__':
    app.run(debug=True)
