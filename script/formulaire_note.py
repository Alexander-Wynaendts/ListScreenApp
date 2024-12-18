def formulaire_note(formulair_info):
    # Initialize a list to hold HTML lines
    html_lines = []

    # Company Information
    html_lines.append("<h4>Company Information</h4>")

    # Company Name
    name = formulair_info.get('Name')
    if name:
        html_lines.append(f"<p><strong>Company Name:</strong> {name}</p>")

    # Website URL
    website_url = formulair_info.get('Website URL')
    if website_url:
        html_lines.append(f"<p><strong>Website:</strong> <a href='{website_url}'>{website_url}</a></p>")

    # Company Location
    company_location = formulair_info.get('company_location')
    if company_location:
        html_lines.append(f"<p><strong>Location:</strong> {company_location}</p>")

    # Industry
    industry = formulair_info.get('industry')
    if industry:
        html_lines.append(f"<p><strong>Industry:</strong> {industry}</p>")

    # Startup Description
    startup_description = formulair_info.get('startup_description')
    if startup_description:
        html_lines.append(f"<p><strong>Description:</strong> {startup_description}</p>")

    # B2B SaaS Company
    b2b_saas = formulair_info.get('b2b_saas')
    if b2b_saas:
        html_lines.append(f"<p><strong>B2B SaaS Company:</strong> {b2b_saas}</p>")

    # Funding Information
    funding_round = formulair_info.get('funding_round')
    funding_amount = formulair_info.get('funding_amount')
    funding_close_date = formulair_info.get('funding_close_date')
    if funding_round or funding_amount or funding_close_date:
        html_lines.append("<h4>Funding Information</h4>")
        if funding_round:
            html_lines.append(f"<p><strong>Funding Round:</strong> {funding_round}</p>")
        if funding_amount:
            html_lines.append(f"<p><strong>Funding Amount:</strong> {funding_amount}</p>")
        if funding_close_date:
            html_lines.append(f"<p><strong>Expected Close Date:</strong> {funding_close_date}</p>")

    # Uploaded File
    uploaded_file = formulair_info.get('uploaded_file')
    if uploaded_file:
        html_lines.append(f"<p><strong>Uploaded File:</strong> <a href='{uploaded_file}'>Download</a></p>")

    # Contact Persons
    first_names = formulair_info.get('first_names', [])
    last_names = formulair_info.get('last_names', [])
    emails = formulair_info.get('emails', [])
    if first_names or last_names or emails:
        html_lines.append("<h4>Contact Persons</h4>")
        # Iterate over the lists simultaneously
        for first_name, last_name, email in zip(first_names, last_names, emails):
            # Full Name
            full_name = f"{first_name} {last_name}".strip()
            if full_name:
                html_lines.append(f"<strong>Name:</strong> {full_name}<br>")
            # Email
            if email:
                html_lines.append(f"<strong>Email:</strong> {email}")

    # Combine all HTML lines into a single string
    note_content = '\n'.join(html_lines)

    # Wrap the note_content in a complete HTML structure
    full_html_content = f"""
<!DOCTYPE html>
<html>
<head><title>Formulaire Note</title></head>
<body>
    {note_content}
</body>
</html>
"""
    return full_html_content
