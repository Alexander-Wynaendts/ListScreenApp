import re

def gmail_comments(data):
    # Retrieve the original sender's email from the forwarded message in the body
    # This assumes the original sender is the one farthest back in the plainBody text
    plain_body = data.get('plainBody', '')
    original_sender_match = re.search(r'From: .*? <(.*?)>', plain_body)
    if original_sender_match:
        original_email = original_sender_match.group(1)
        # Extract the domain from the original sender's email
        company_email_domain = original_email.split('@')[-1]
    else:
        original_email = None
        company_email_domain = None

    # Retrieve the first email content (latest comment) in the thread
    # Assuming it's the first line of plainBody text
    last_comment_match = re.search(r'^.*$', plain_body, re.MULTILINE)
    last_comment = last_comment_match.group(0) if last_comment_match else None

    return company_email_domain, last_comment
