import requests
import openai
import os
import re

fireflies_api_key = os.getenv("FIREFLIES_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

def gpt_fireflies_html_formatting(output, prompt_templates):
    # Retrieve the Fireflies Notes prompt template from prompt_templates
    prompt_template = prompt_templates.get("Fireflies Notes", "")
    if not prompt_template:
        print("Error: 'Fireflies Notes' prompt template not found.")
        return None

    # Format the prompt with the output
    prompt = prompt_template.format(output=output)

    # Sending the prompt to the GPT API for strict HTML output
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    # Strip and directly return HTML response
    fireflies_html = response['choices'][0]['message']['content'].strip()
    fireflies_html = re.sub(r"^[\"']+|[\"']+$", '', fireflies_html).strip()

    return fireflies_html

def fireflies_transcript_processing(transcript_id, prompt_templates):
    url = 'https://api.fireflies.ai/graphql'
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {fireflies_api_key}'}
    query = '''
    query Transcript($transcriptId: String!) {
      transcript(id: $transcriptId) {
        id
        title
        dateString
        speakers {
          id
          name
        }
        sentences {
          index
          speaker_name
          text
          start_time
          end_time
        }
        duration
        summary {
          gist
          bullet_gist
        }
        meeting_attendees {
          displayName
          email
          phoneNumber
          name
          location
        }
      }
    }
    '''
    variables = {"transcriptId": transcript_id}
    response = requests.post(url, headers=headers, json={"query": query, "variables": variables})
    data = response.json()

    # Extract necessary information
    speakers = [speaker['name'] for speaker in data['data']['transcript']['speakers']]
    sentences = data['data']['transcript']['sentences']
    transcript_text = [sentence['text'] for sentence in sentences]
    summary = data['data']['transcript']['summary']['gist']
    bullet_summary = data['data']['transcript']['summary']['bullet_gist']

    # Extract attendee email
    meeting_attendees = data['data']['transcript']['meeting_attendees']
    non_entourage_email = next(
        (attendee['email'] for attendee in meeting_attendees if attendee['email'] and not attendee['email'].endswith('@entourage.io')),
        None
    )
    website_url = non_entourage_email.split('@')[1] if non_entourage_email else "No valid email found"

    # Format and prepare the HTML structure
    output = f"<strong>Speakers:</strong> {', '.join(speakers)}<br><br><strong>Transcript:</strong><br>"
    output += "<br>".join(f"- {sentence}" for sentence in transcript_text)
    output += f"<br><br><strong>Summary:</strong> {summary}<br><strong>Detailed Summary:</strong> {bullet_summary}"

    # Generate HTML using the GPT-3 model with the Fireflies Notes prompt
    fireflies_html = gpt_fireflies_html_formatting(output, prompt_templates)

    return fireflies_html, website_url
