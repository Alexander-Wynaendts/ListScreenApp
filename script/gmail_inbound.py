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
        domain = sender_email.split('@')[1].lower()
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
        company_info["Website URL"] = f"https://{domain}"
        # Get the company name from the domain (capitalize first letter and take everything until the '.')
        company_name = domain.split('.')[0].capitalize()
        company_info["Name"] = company_name
    else:
        company_info["Website URL"] = ''
        company_info["Name"] = ''

    # Create a single string variable with Subject and Content, removing '\r\n'
    subject = email_info.get('subject', '').strip()
    plain_body = email_info.get('plain_body', '').strip()

    # Remove line breaks and carriage returns from the content
    content = plain_body.replace('\r', '').replace('\n', '')

    # Combine Subject and Content into one string
    the_string = f"{subject}\n\n{content}"
    company_info["Email Content"] = the_string

    return company_info
