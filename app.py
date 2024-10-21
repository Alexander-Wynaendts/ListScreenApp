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
        # Process webhook data from Affinity
        data = request.json
        print("Received webhook:", data)

        # Trigger the Python script
        try:
            # Call the main.py script
            result = subprocess.run(['python3', '/mnt/data/main.py'], capture_output=True, text=True)
            return jsonify({"status": "Script executed", "output": result.stdout}), 200
        except Exception as e:
            return jsonify({"status": "Error", "message": str(e)}), 500

    return jsonify({"status": "Invalid request"}), 400

if __name__ == '__main__':
    app.run(debug=True)
