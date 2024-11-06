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
    <h3>Meeting Summary</h3>

    <h4>Summary</h4>
    <p><strong>Summary:</strong> {{Provide a brief summary of the meeting, focusing on key points discussed and general impressions.}}</p>

    <h4>Founders</h4>
    <ul>
        <li>{{List each founder with their title and a brief description of their relevant experience. Focus on founders only, excluding other team members or advisors.}}</li>
    </ul>

    <h4>One-line Description</h4>
    <p>{{Provide a concise line describing the startup’s business focus.}}</p>

    <h4>Traction</h4>
    <p>{{Highlight key traction metrics, such as ARR, projected ARR, non-recurring revenue, projected revenue, number of pilot projects (indicate if paying), and other relevant growth indicators.}}</p>

    <h4>Why Them?</h4>
    <p>{{Analyze why the founders are well-suited (or not) to address this problem based on their background and experience.}}</p>

    <h4>Why Now?</h4>
    <p>{{Discuss why the timing is advantageous for this product. Mention any market shifts that make this solution timely or urgent.}}</p>

    <h4>Too Hyped?</h4>
    <p>{{Assess whether the sector or product might be overhyped. Evaluate if the proposed funding or valuation aligns with current market trends.}}</p>

    <h4>Too Greedy?</h4>
    <p>{{Consider the founders' ambitions and growth plans, noting if they are realistic or overly aggressive.}}</p>

    <h4>In-Depth Analysis</h4>

    <h4>ICP</h4>
    <p>{{Define the Ideal Customer Profile, covering aspects such as company size, geography, expected contract size, and other relevant details.}}</p>

    <h4>Addressed Problem</h4>
    <p>{{Explain the problem the startup aims to solve, its significance, and the scale of its impact.}}</p>

    <h4>Team</h4>
    <p>{{Summarize relevant experience and roles for each team member, providing a paragraph for each, based on their background and contribution to the project.}}</p>

    <h4>Market</h4>
    <p>{{Describe the market size, target market segment, and the projected capture rate.}}</p>

    <h4>Sales</h4>
    <p>{{Provide details on the current sales pipeline, including key leads and expected timeline if available.}}</p>

    <h4>Product</h4>
    <p>{{Describe the product, its core functionality, and any unique features that make it stand out.}}</p>

    <h4>Competition</h4>
    <p>{{Identify key competitors, their similarities, and how this startup differentiates itself from them.}}</p>

    <h4>Problems?</h4>
    <p>{{Note any potential issues such as IP challenges, cap table concerns, or other flagged risks.}}</p>

    <h4>Current Funding Situation</h4>
    <p>{{Describe previous funding rounds, including amounts, valuation, funding type, main investors, and funding timeline if provided.}}</p>

    <h4>Raising Funding</h4>
    <p>{{Outline details on current fundraising efforts, including target amount, funding type, valuation, timeline, lead or follow requirements, and any commitments or goals.}}</p>

    <h3>Q&A</h3>
    <p>{{Summarize key questions and answers from the meeting, excluding small talk.}}</p>
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
