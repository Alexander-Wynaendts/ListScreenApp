import requests
import openai
import os

fireflies_api_key = os.getenv("FIREFLIES_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

def gpt_fireflies_formatting(output):
    # Defining the prompt structure with the transcript and summary included in the content
    prompt = f"""
You are a venture capitalist investing in early-stage B2B companies. Given the following meeting data, including meeting notes and transcript, organize the data into the format below. Each question should be answered as analytically as possible, only using the provided data. Do not add any information not explicitly mentioned. Be critical in your responses and make the layout easy to copy and paste.

Meeting Data:
{output}

TEMPLATE:

Summary

Founders
{{List each founder with their title and a one-line description. Only list founders, not team members or advisors.}}

One-line description
{{Provide a one-line description of what the startup does.}}

Traction
{{Briefly mention key metrics if provided, including ARR and projected ARR, non-recurring revenue and projected revenue, the number of pilot projects (indicating if they are paid), and any relevant extra information.}}

Why them?
{{Analyze if the founders are a strong fit for the company and problem.}}

Why now?
{{Discuss why the product is viable now, including any recent changes in the world that may benefit it.}}

Too hyped?
{{Evaluate if the sector or product is overhyped, and whether the funding expectations are realistic.}}

Too greedy?
{{Assess if the founders’ growth plans are realistic and sufficiently ambitious.}}

In-depth part:

ICP
{{Describe the Ideal Customer Profile, including company size, geography, contract size, and other relevant data.}}

Addressed problem
{{Define the problem the startup addresses, and indicate its scale.}}

Team
{{List relevant experience for each team member (up to one paragraph each).}}

Market
{{Identify the market, its size, and what the company aims to capture.}}

Sales
{{Summarize their sales pipeline, if mentioned.}}

Product
{{Provide a description of the product.}}

Competition
{{Mention any competitors and briefly describe how they are similar or different from the startup.}}

Problems?
{{List any IP or cap table issues, or other specific problems if mentioned.}}

Current funding situation
{{Summarize previous funding details, including amount, valuation, funding type, and funders if available.}}

Raising funding
{{Describe their current fundraising efforts, including the amount, funding type, valuation or equity offered, timeline, and any commitments or lead/follow search.}}

Q&A
{{List any questions and answers from the call, excluding small talk.}}
"""

    # Sending the prompt to the GPT API for analysis and formatting
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    fireflies_note = response['choices'][0]['message']['content'].strip()
    return fireflies_note

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

    # Extract speakers
    speakers = [speaker['name'] for speaker in data['data']['transcript']['speakers']]

    # Extract transcript sentences
    sentences = data['data']['transcript']['sentences']
    transcript_text = [sentence['text'] for sentence in sentences]

    # Extract summary
    summary = data['data']['transcript']['summary']['gist']
    bullet_summary = data['data']['transcript']['summary']['bullet_gist']

    # Extract the first email not ending in '@entourage.io'
    meeting_attendees = data['data']['transcript']['meeting_attendees']
    non_entourage_email = next(
        (attendee['email'] for attendee in meeting_attendees if attendee['email'] and not attendee['email'].endswith('@entourage.io')),
        None
    )
    website_url = non_entourage_email.split('@')[1] if non_entourage_email else "No valid email found"

    # Format the output and store it in a string
    output = f"Speakers: {', '.join(speakers)}\n\nTranscript:\n"
    output += "\n".join(f"- {sentence}" for sentence in transcript_text)
    output += f"\n\nSummary:\n{summary}\n\nDetailed Summary:\n{bullet_summary}"

    fireflies_note = gpt_fireflies_formatting(output)

    return fireflies_note, website_url
