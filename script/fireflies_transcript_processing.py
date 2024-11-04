import requests
import openai
import os
import re

fireflies_api_key = os.getenv("FIREFLIES_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

def gpt_fireflies_html_formatting(output):
    # Defining the prompt with a clearer emphasis on outputting HTML only
    prompt = f"""
You are a venture capitalist investing in early-stage B2B companies. Given the following meeting data, including meeting notes and transcript, provide a response strictly formatted in the HTML structure below. It is important that you act in a critical way, each question should be answered as analytical as possible: The template is below, if the text is in-between curly brackets then it is a description of what is expected. Only answer using the data given, do not answer any question using your own knowledge! Be as critical as possible! Only return HTML.

Meeting transcript:
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
    <ul>
        <li>{{List each founder with their title and a one-line description. Only include founders, not other team members or advisors.}}</li>
    </ul>

    <h5>One-line Description</h5>
    <p>{{A single line describing the startup’s business focus.}}</p>

    <h5>Traction</h5>
    <p>{{Key metrics, such as ARR, projected ARR, non-recurring revenue, projected revenue, number of pilot projects (indicate if paying), and other relevant growth indicators.}}</p>

    <h5>Why Them?</h5>
    <p>{{Reasons why the founders are well-suited (or not) to address this problem.}}</p>

    <h5>Why Now?</h5>
    <p>{{Explain why the timing is ideal for this product. Mention any market changes that make it viable now.}}</p>

    <h5>Too Hyped?</h5>
    <p>{{Is the sector or product overhyped? Is the proposed funding or valuation realistic?}}</p>

    <h5>Too Greedy?</h5>
    <p>{{Assessment of the founders' ambitions and growth plans. Are they realistic or overly aggressive?}}</p>

    <h4>In-Depth Analysis</h4>
    <ul>
        <li><strong>ICP:</strong> {{Ideal Customer Profile, including company size, geography, contract size, and any other relevant details.}}</li>
        <li><strong>Addressed Problem:</strong> {{Description of the problem, its importance, and scale.}}</li>
        <li><strong>Team:</strong> {{Summarize relevant experience and roles for each team member, one paragraph each.}}</li>
        <li><strong>Market:</strong> {{Market size, target capture, and specific market sector.}}</li>
        <li><strong>Sales:</strong> {{Details of the current sales pipeline if available.}}</li>
        <li><strong>Product:</strong> {{Brief description of the product and its core functionality.}}</li>
        <li><strong>Competition:</strong> {{Competitors, their comparisons, and differentiation factors. If a main competitor is mentioned, briefly describe similarities and differences.}}</li>
        <li><strong>Problems:</strong> {{Any IP issues, cap table concerns, or other flagged problems.}}</li>
        <li><strong>Current Funding Situation:</strong> {{Previous funding details, including valuation, funding type, investors, and funding timeline if mentioned.}}</li>
        <li><strong>Raising Funding:</strong> {{Details on current fundraising efforts, including target amount, funding type, valuation, timeline, lead/follow search, and any commitments.}}</li>
    </ul>

    <h5>Q&A</h5>
    <p>{{A summary of questions and answers from the meeting (exclude small talk).}}</p>
</body>
</html>
"""

    # Sending the prompt to the GPT API for strict HTML output
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    # Strip and directly return HTML response
    fireflies_html = response['choices'][0]['message']['content'].strip()
    fireflies_html = re.sub(r'^"+|"+$', '', fireflies_html).strip()

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
