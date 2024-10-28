import requests
import openai
import os

fireflies_api_key = os.getenv("FIREFLIES_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

def gpt_fireflies_formatting(output):
    prompt = f"""{output}"""
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
