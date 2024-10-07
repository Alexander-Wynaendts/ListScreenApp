from flask import Flask, request, jsonify, send_file, render_template
import pandas as pd
import io
import os
from script.main import main  # Import your main function

app = Flask(__name__)

# Path to store the processed file temporarily
TEMP_FILE_PATH = "temp/processed_data.csv"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file:
        return jsonify({
            'logs': 'No file uploaded',
            'success': False
        })

    try:
        # Load the CSV into a DataFrame
        df = pd.read_csv(file)

        # Run the main function on the DataFrame (this is your processing logic)
        logs, startup_data = main(df)  # Assuming main() takes a dataframe and returns a processed dataframe

        if startup_data is None:
            return jsonify({
            'logs': logs,
            'success': False
        })

        # Save the processed DataFrame to a temporary CSV file
        startup_data.to_csv(TEMP_FILE_PATH, index=False)

        logs = 'CSV successfully processed and saved.'  # You can update logs based on the process
        return jsonify({
            'logs': logs,
            'success': True
        })
    except Exception as e:
        return jsonify({
            'logs': f'Error: {str(e)}',
            'success': False
        })

@app.route('/download', methods=['GET'])
def download_file():
    # Check if the temporary file exists
    if not os.path.exists(TEMP_FILE_PATH):
        return jsonify({"error": "No processed file found"}), 400

    # Send the processed CSV file as a downloadable file
    return send_file(TEMP_FILE_PATH, mimetype="text/csv", attachment_filename="processed_data.csv", as_attachment=True)

if __name__ == '__main__':
    # Create the temporary folder if it doesn't exist
    os.makedirs('temp', exist_ok=True)
    app.run(debug=True)
