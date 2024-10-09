from quart import Quart, render_template, request, send_file, Response
import pandas as pd
import io
import asyncio
from script.main import main

app = Quart(__name__)

@app.route('/')
async def index():
    return await render_template('index.html')

@app.route('/upload', methods=['POST'])
async def upload_file():
    try:
        # Await to properly handle the file upload in Quart
        file = (await request.files).get('file')

        if not file:
            return "No file uploaded", 400

        # Read the file into a DataFrame
        df = pd.read_csv(file)

        # Call the main processing function asynchronously
        startup_data = await main(df)

        if startup_data is None:
            return "Error processing file", 400

        # Convert the processed DataFrame to CSV in-memory using UTF-8 encoding
        output = io.BytesIO()
        startup_data.to_csv(output, index=False, encoding='utf-8')
        output.seek(0)

        # Send the file back as a downloadable CSV
        return await send_file(output, mimetype='text/csv', as_attachment=True, attachment_filename='processed_data.csv')

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return f"Error processing file: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
