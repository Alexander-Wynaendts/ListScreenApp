from flask import Flask, request, jsonify, Response, stream_with_context, send_file, render_template
import pandas as pd
import io
from script.main import main  # Import your main function

app = Flask(__name__)

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

    df = pd.read_csv(file)

    # Run the main function on the DataFrame (this is your processing logic)
    logs, startup_data = main(df)  # Assuming main() returns logs and processed dataframe

    if startup_data is None:
        return jsonify({
            'logs': logs,
            'success': False
        })

    logs = 'CSV successfully processed.'

    # Convert the DataFrame to a CSV in-memory
    output = io.StringIO()
    startup_data.to_csv(output, index=False)
    output.seek(0)  # Go back to the beginning of the StringIO object

    return jsonify({
        'logs': logs,
        'csv_content': output.getvalue(),  # Pass the CSV content in the response
        'success': True
    })

if __name__ == '__main__':
    app.run(debug=True)
