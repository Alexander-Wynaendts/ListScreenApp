from flask import Flask, render_template, request, jsonify
import subprocess
import pandas as pd
import io
from script.main import main

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file:
        return "No file uploaded", 400

    # Read the file into a DataFrame
    df = pd.read_csv(file)

    # Call the main processing function
    startup_data = main(df)

    # Check if the processing returned data
    if startup_data is None:
        return "Error processing file", 40

    # Send the file back as a downloadable CSV
    return "Affinity Updated"

# Webhook route
@app.route('/affinity-webhook', methods=['POST'])
def affinity_webhook():
    if request.method == 'POST':
        data = request.json
        print("Received webhook:", data)

        # Check if the event type is 'list_entry.created'
        if data.get('type') == 'list_entry.created':
            # Extract relevant information from the event
            entity = data.get('body', {}).get('entity', {})
            name = entity.get('name', '')
            website_url = entity.get('domain', '')  # Adjust as per data source if website URL is different

            # Store it in a DataFrame
            df = pd.DataFrame([{'Name': name, 'Website URL': website_url}])

            print(df)

        # Send the file back as a downloadable CSV
        return "Affinity Updated"

if __name__ == '__main__':
    app.run(debug=True)
