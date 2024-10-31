import requests
import openai
import os

fireflies_api_key = os.getenv("FIREFLIES_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

def gpt_fireflies_html_formatting(output):
    # Defining the HTML template structure with the required content
    prompt = f"""
You are a venture capitalist investing in early-stage B2B companies. Given the following meeting data, including meeting notes and transcript, format the data into the HTML structure below. Be concise and avoid adding any extra styles or spaces.

Meeting Data:
{output}

HTML TEMPLATE:

<!DOCTYPE html>
<html>
<head>
    <title>Meeting Summary</title>
</head>
<body>
    <h4>Meeting Summary</h4>
    <p><strong>Summary:</strong> {{Summary of the meeting}}</p>

    <h5>Founders</h5>
    <p>{{List each founder with their title and a one-line description.}}</p>

    <h5>One-line Description</h5>
    <p>{{A single line describing the startup's business focus.}}</p>

    <h5>Traction</h5>
    <p>{{Key metrics, such as ARR, pilot projects, and any additional growth indicators.}}</p>

    <h5>Why Them?</h5>
    <p>{{Reasoning for the founders' suitability for this role.}}</p>

    <h5>Why Now?</h5>
    <p>{{Why the timing is ideal for this product.}}</p>

    <h5>Too Hyped?</h5>
    <p>{{Assessment of the market's current hype status.}}</p>

    <h5>Too Greedy?</h5>
    <p>{{Evaluation of growth plans and ambition.}}</p>

    <h4>In-Depth Analysis</h4>
    <ul>
        <li><strong>ICP:</strong> {{Ideal Customer Profile}}</li>
        <li><strong>Addressed Problem:</strong> {{Problem description and scale}}</li>
        <li><strong>Team:</strong> {{Team's relevant experience}}</li>
        <li><strong>Market:</strong> {{Market size and company's target capture}}</li>
        <li><strong>Sales:</strong> {{Sales pipeline details}}</li>
        <li><strong>Product:</strong> {{Product description}}</li>
        <li><strong>Competition:</strong> {{Competitors and comparison}}</li>
        <li><strong>Problems:</strong> {{Any IP, cap table, or other issues}}</li>
        <li><strong>Current Funding Situation:</strong> {{Details of previous funding}}</li>
        <li><strong>Raising Funding:</strong> {{Current fundraising efforts}}</li>
    </ul>
</body>
</html>
"""

    # Sending the prompt to the GPT API for analysis and formatting
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    fireflies_html = response['choices'][0]['message']['content'].strip()
    return fireflies_html

def fireflies_transcript_processing(transcript_id):
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

    fireflies_html = gpt_fireflies_html_formatting(output)

    return fireflies_html, website_url
