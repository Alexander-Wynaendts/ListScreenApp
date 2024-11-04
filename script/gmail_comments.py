import re

def gmail_comments(data):
    # Retrieve the original sender's email from the forwarded message in the body
    plain_body = data.get('plainBody', '')
    original_sender_match = re.search(r'From: .*? <(.*?)>', plain_body)
    if original_sender_match:
        original_email = original_sender_match.group(1)
        # Extract the domain from the original sender's email
        website_url = original_email.split('@')[-1]
    else:
        original_email = None
        website_url = None

    # Retrieve the first email content (last comment) in the thread up to '\r\n\r\n>'
    last_comment_match = re.search(r'^(.*?)(?=\r\n\r\n>)', plain_body, re.DOTALL)
    last_comment = last_comment_match.group(0) if last_comment_match else None

    return website_url, last_comment
