import re

def extract_original_sender_and_comment(data):
    # Retrieve the original sender's email from the forwarded message in the body
    plain_body = data.get('plainBody', '')
    original_sender_match = re.search(r'From: .*? <(.*?)>', plain_body)
    if original_sender_match:
        original_email = original_sender_match.group(1)
        # Extract the domain from the original sender's email
        company_email_domain = original_email.split('@')[-1]
    else:
        original_email = None
        company_email_domain = None

    # Retrieve the first email content (last comment) in the thread up to '\r\n\r\n>'
    last_comment_match = re.search(r'^(.*?)(?=\r\n\r\n>)', plain_body, re.DOTALL)
    last_comment = last_comment_match.group(0) if last_comment_match else None

    return company_email_domain, last_comment
