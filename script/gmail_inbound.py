import re

def gmail_inbound(email_info):
    company_info = {}

    # Extract subject, plain body, and HTML body
    subject = email_info.get('subject', '').strip()
    plain_body = email_info.get('plainBody', '').strip()
    html_body = email_info.get('htmlBody', '').strip()

    # Initialize the sender email
    sender_email = ""

    # Check if the email is a forwarded message
    if subject.startswith("Fwd:"):
        # Extract content after the forwarded message marker
        forwarded_body_match = re.split(r"[-]+ Forwarded message [-]+\s*", plain_body)
        if len(forwarded_body_match) > 1:
            # The content after the forwarded marker is assumed to be the original message
            original_body = forwarded_body_match[-1].strip()

            # Extract the original sender's email and name
            forwarded_match = re.search(r"From:\s*(.*?)\s*<(.+?)>", original_body)
            if forwarded_match:
                original_sender_name = forwarded_match.group(1).strip()
                sender_email = forwarded_match.group(2).strip()

            # Extract the original subject
            forwarded_subject_match = re.search(r"Subject:\s*(.*?)\n", original_body)
            if forwarded_subject_match:
                original_subject = forwarded_subject_match.group(1).strip()
                subject = original_subject if original_subject else subject

            # Update plain_body to contain only the forwarded email's actual content
            content_match = re.split(r"\r\n\r\n", original_body, maxsplit=1)
            if len(content_match) > 1:
                plain_body = content_match[1].strip()
    else:
        # Extract email from 'from' field if not a forwarded message
        sender = email_info.get('from', '')
        match = re.match(r".*<(.+?)>", sender)
        sender_email = match.group(1) if match else sender

    # Parse the email address for sender details and construct company info
    if '@' in sender_email:
        company_info["Email"] = sender_email
        local_part, domain = sender_email.split('@')[0], sender_email.split('@')[1].lower()

        # Extract first and last name from local part
        if '.' in local_part:
            first_name, last_name = local_part.split('.', 1)
            company_info["First Name"] = first_name.capitalize()
            company_info["Last Name"] = last_name.capitalize()
        else:
            company_info["First Name"] = local_part.capitalize()
            company_info["Last Name"] = ""

        # Exclude common domains for constructing the website URL
        common_domains = [
            'gmail.com', 'outlook.com', 'hotmail.com', 'yahoo.com', 'icloud.com',
            'aol.com', 'protonmail.com', 'live.com', 'msn.com', 'comcast.net',
            'me.com', 'mail.com', 'gmx.com'
        ]
        if domain not in common_domains:
            company_info["Website URL"] = f"https://{domain}"
            company_info["Name"] = '.'.join(domain.split('.')[:-1]).capitalize()
        else:
            company_info["Website URL"] = ''
            company_info["Name"] = ''
    else:
        company_info["Email"] = ''
        company_info["First Name"] = ''
        company_info["Last Name"] = ''
        company_info["Website URL"] = ''
        company_info["Name"] = ''

    # Construct HTML content
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
