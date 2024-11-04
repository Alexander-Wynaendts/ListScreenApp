import re

def gmail_inbound(email_info):
    company_info = {}

    # Extract the sender's email address
    sender = email_info.get('from', '')
    match = re.match(r'.*<(.+?)>', sender)
    if match:
        sender_email = match.group(1)
    else:
        sender_email = sender

    # Extract subject, plain body, and HTML body
    subject = email_info.get('subject', '').strip()
    plain_body = email_info.get('plainBody', '').strip()
    html_body = email_info.get('htmlBody', '').strip()

    # Check if the email is a forwarded message
    if subject.startswith("Fwd:"):
        # Extract original sender and email details from forwarded content
        forwarded_match = re.search(r"From:\s*(.*?)\s*<(.+?)>", plain_body)
        if forwarded_match:
            original_sender_name = forwarded_match.group(1).strip()
            sender_email = forwarded_match.group(2).strip()

        # Extract original subject if available
        forwarded_subject_match = re.search(r"Subject:\s*(.*?)\n", plain_body)
        if forwarded_subject_match:
            original_subject = forwarded_subject_match.group(1).strip()
            subject = original_subject if original_subject else subject

        # Extract the original email body content from forwarded section
        forwarded_body_match = re.split(r"[-]+ Forwarded message [-]+\s*", plain_body)
        if len(forwarded_body_match) > 1:
            plain_body = forwarded_body_match[-1].strip()  # Use the forwarded email's body

    # Parse the email for sender details and create the company info dictionary
    if '@' in sender_email:
        company_info["Email"] = sender_email
        local_part = sender_email.split('@')[0]
        domain = sender_email.split('@')[1].lower()

        # Extract first and last name
        if '.' in local_part:
            first_name, last_name = local_part.split('.', 1)
            company_info["First Name"] = first_name.capitalize()
            company_info["Last Name"] = last_name.capitalize()
        else:
            company_info["First Name"] = ""
            company_info["Last Name"] = local_part.capitalize()

        # Exclude common domains
        common_domains = [
            'gmail.com', 'outlook.com', 'hotmail.com', 'yahoo.com', 'icloud.com',
            'aol.com', 'protonmail.com', 'live.com', 'msn.com', 'comcast.net',
            'me.com', 'mail.com', 'gmx.com'
        ]
        if domain in common_domains:
            domain = ''
    else:
        domain = ''

    # Construct Website URL and Company Name if domain is not a common email provider
    if domain:
        company_info["Website URL"] = domain
        company_name = '.'.join(domain.split('.')[:-1]).capitalize()
        company_info["Name"] = company_name
    else:
        company_info["Website URL"] = ''
        company_info["Name"] = ''

    # Create HTML content for email
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
