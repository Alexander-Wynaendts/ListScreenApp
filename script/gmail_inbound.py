import re

def gmail_inbound(email_info):
    company_info = {}

    # Extract the sender's email address
    sender = email_info.get('sender', '')
    match = re.match(r'.*<(.+?)>', sender)
    if match:
        sender_email = match.group(1)
    else:
        sender_email = sender

    # Extract the domain from the email address
    if '@' in sender_email:

        company_info["Email"] = sender_email

        local_part = sender_email.split('@')[0]  # The part before the '@'
        domain = sender_email.split('@')[1].lower()

        # Extract first and last name
        if '.' in local_part:
            first_name, last_name = local_part.split('.', 1)
            company_info["First Name"] = first_name.capitalize()
            company_info["Last Name"] = last_name.capitalize()
        else:
            company_info["First Name"] = ""
            company_info["Last Name"] = local_part.capitalize()

        # List of common email domains to exclude
        common_domains = [
            'gmail.com', 'outlook.com', 'hotmail.com', 'yahoo.com', 'icloud.com',
            'aol.com', 'protonmail.com', 'live.com', 'msn.com', 'comcast.net',
            'me.com', 'mail.com', 'gmx.com'
        ]
        if domain in common_domains:
            domain = ''
    else:
        domain = ''

    # Construct the Website URL and Company Name if domain is not a common email provider
    if domain:
        company_info["Website URL"] = domain
        # Get the company name by keeping everything before the last dot ('.')
        company_name = '.'.join(domain.split('.')[:-1]).capitalize()
        company_info["Name"] = company_name
    else:
        company_info["Website URL"] = ''
        company_info["Name"] = ''

    subject = email_info.get('subject', '').strip()
    html_body = email_info.get('html_body', '').strip()

    the_string = f"""
<!DOCTYPE html>
<html>
<body>
    <p>{subject}</p>
    <br>
    <p>{html_body}</p>
</body>
</html>
"""

    company_info["Email Content"] = the_string

    return company_info
