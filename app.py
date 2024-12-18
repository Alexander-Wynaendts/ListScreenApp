from flask import Flask, render_template, redirect, url_for, session, request
import yaml
from datetime import timedelta

from script.gmail_inbound import gmail_inbound
from script.gmail_comments import gmail_comments
from script.affinity_company_data import affinity_company_data
from script.website_scraping import website_scraping
from script.website_analysis import website_analysis
from script.add_company_to_affinity import add_company_to_affinity
from script.add_people_to_affinity import add_people_to_affinity
from script.update_affinity_field import update_affinity_field
from script.formulaire_note import formulaire_note
from script.add_note_to_affinity import add_note_to_affinity
from script.add_global_to_affinity import add_global_to_affinity
from script.fireflies_transcript_processing import fireflies_transcript_processing
from script.lemlist_export import lemlist_export

app = Flask(__name__)
app.secret_key = "Assemblage_secret"  # Use a secure, random key in production
app.permanent_session_lifetime = timedelta(minutes=5)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        with open('data/password.txt', 'r') as file:
            original_password = file.read().strip()
        entered_password = request.form.get('password')

        if entered_password == original_password:
            session.permanent = True  # Make the session permanent for the timeout to apply
            session['authenticated'] = True
            return redirect(url_for('prompt_manager'))
        else:
            return render_template('index.html', error="Incorrect password. Please try again.")

    # If session is authenticated, go directly to prompt manager
    if session.get('authenticated'):
        return redirect(url_for('prompt_manager'))

    return render_template('index.html')

@app.route('/prompt_manager')
def prompt_manager():
    if not session.get('authenticated'):
        return redirect(url_for('index'))
    return render_template('prompt_manager.html')

@app.route('/prompt/<prompt_type>', methods=['GET', 'POST'])
def prompt_update(prompt_type):
    if not session.get('authenticated'):
        return redirect(url_for('index'))  # Corrected to use 'index' as the endpoint name

    # Load prompt templates from YAML each time this route is accessed
    with open('data/prompt_templates.yaml', 'r') as file:
        prompt_templates = yaml.safe_load(file)

    if request.method == 'POST':
        new_template = request.form.get("template")
        if new_template:
            prompt_templates[prompt_type] = new_template
            # Update the YAML file to save changes persistently
            with open('data/prompt_templates.yaml', 'w') as file:
                yaml.dump(prompt_templates, file)
        return redirect(url_for('prompt_manager'))

    template = prompt_templates.get(prompt_type, "Template not found.")
    return render_template('prompt_edit.html', prompt_type=prompt_type, template=template)

@app.route('/affinity-webhook', methods=['POST'])
def affinity_webhook():
    if request.method == 'POST':
        data = request.json

        with open('data/prompt_templates.yaml', 'r') as file:
            prompt_templates = yaml.safe_load(file)

        # Check for organization.created event
        if data.get('type') == 'list_entry.created':
            body = data.get('body', {})
            name = body.get("entity", {}).get('name', '')
            website_url = body.get("entity", {}).get('domain', '')

            if website_url:
                website_data = website_scraping(website_url, prompt_templates)
                company_screened = website_analysis(website_data, prompt_templates)
                company_screened["Website URL"] = website_url
                company_screened['Status'] = "To screen"

                update_affinity_field(company_screened)

                print(f"New company in 'Deal Flow': {website_url}")

        # Check for field_value.updated event and the status field
        if data.get('type') == 'field_value.updated':
            body = data.get('body', {})
            field_name = body.get('field', {}).get('name', '')
            if field_name == 'Status':
                if body.get('value', {}).get('text', '') is None or body.get('value', {}).get('text', '') == "New":
                    entry_data = affinity_company_data(body)
                    website_url = entry_data.get("Website URL")

                    if website_url:
                        website_data = website_scraping(website_url, prompt_templates)
                        company_screened = website_analysis(website_data, prompt_templates)
                        company_screened["Website URL"] = website_url
                        company_screened['Status'] = "To screen"

                        update_affinity_field(company_screened)

                        print(f'Status "New" update: {website_url}')

                if body.get('value', {}).get('text', '') == 'To be contacted':

                    company_info = affinity_company_data(body)
                    website_url = company_info.get("Website URL", "")

                    if website_url != "":
                        if not company_info.get('Contacts', []):
                            status_update = {"Website URL": website_url, "Status": "To screen"}
                            update_affinity_field(status_update)

                        if company_info.get("Inbound Boolean", "") == "Yes":
                            lemlist_export(company_info, "Inbound")
                        else:
                            lemlist_export(company_info, "Outbound")

                        website_url = company_info.get("Website URL", "")
                        print(f'Status "To be contacted": {website_url}')

                if body.get('value', {}).get('text', '') == 'Rejected':

                    company_info = affinity_company_data(body)
                    website_url = company_info.get("Website URL", "")

                    if website_url != "":
                        if company_info.get("Inbound Boolean", "") == "Yes":
                            lemlist_export(company_info, "Rejected")

                            website_url = company_info.get("Website URL", "")
                            print(f'Status "Rejected": {website_url}')

        return "Affinity webhook received and processed", 200

@app.route('/gmail-webhook', methods=['POST'])
def gmail_webhook():
    if request.method == 'POST':
        data = request.json

        email_info = gmail_inbound(data)

        first_name = email_info.get("First Name")
        last_name = email_info.get("Last Name")
        email = email_info.get("Email")

        name = email_info.get("Name")
        website_url = email_info.get("Website URL")
        email_content = email_info.get("Email Content")

        if website_url != "":
            if add_company_to_affinity(name, website_url):
                add_note_to_affinity(website_url, email_content)
                source = "Gmail Inbound"
                inbound_boolean = "Yes"
                add_global_to_affinity(website_url, source, inbound_boolean)

                add_people_to_affinity(first_name, last_name, email, website_url)

            print(f"New company out of email: {website_url}")
        return "Success", 200

@app.route('/gmail-webhook-comments', methods=['POST'])
def gmail_webhook_comments():
    if request.method == 'POST':
        data = request.json

        website_url, last_comment = gmail_comments(data)
        add_note_to_affinity(website_url, last_comment)

        print(f"New comment on email")
        return "Success", 200

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
        source = "Form Inbound"
        inbound_boolean = "Yes"
        add_global_to_affinity(website_url, source, inbound_boolean)

        print(f"New form submission: {website_url}")

    return "Form webhook received and processed", 200

@app.route('/fireflies-webhook', methods=['POST'])
def fireflies_webhook():
    if request.method == 'POST':
        data = request.json

        with open('data/prompt_templates.yaml', 'r') as file:
            prompt_templates = yaml.safe_load(file)

        if data.get("eventType", "") == "Transcription completed":
            transcript_id = data.get("meetingId", "")
            fireflies_note, website_url = fireflies_transcript_processing(transcript_id, prompt_templates)

            add_note_to_affinity(website_url, fireflies_note)

        print(f"New transcript from Fireflies: {website_url}")

    return "Fireflies webhook received and processed", 200

@app.route('/lemlist-webhook-run', methods=['POST'])
def lemlist_webhook_contacted():
    if request.method == 'POST':
        data = request.json

        website_url = data.get("companyDomain", "")
        company_status = "Contacted"

        company_udpate = {"Website URL": website_url, "Status": company_status}
        update_affinity_field(company_udpate)

        print(f"Lemlist email flow running: {website_url}")

    return "Lemlist webhook received and processed", 200

@app.route('/lemlist-webhook-lost', methods=['POST'])
def lemlist_webhook_lost():
    if request.method == 'POST':
        data = request.json

        website_url = data.get("companyDomain", "")
        company_status = "No answer"

        company_udpate = {"Website URL": website_url, "Status": company_status}
        update_affinity_field(company_udpate)

        print(f"Lemlist email flow done: {website_url}")

    return "Lemlist webhook received and processed", 200

if __name__ == '__main__':
    app.run(debug=True)
