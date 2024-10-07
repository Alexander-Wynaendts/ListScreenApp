from flask import Flask, request, render_template, send_file
import os
import pandas as pd
from script.main import main

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']

    if not file:
        return "No file uploaded", 400

    # Lire le fichier CSV uploadé
    startup_data = pd.read_csv(file)

    # Traiter le fichier via la fonction main()
    startup_data = main(startup_data)

    # Sauvegarder le fichier CSV de sortie
    output_csv_path = "output.csv"
    startup_data.to_csv(output_csv_path, index=False)

    # Envoyer le fichier CSV généré à l'utilisateur
    return send_file(output_csv_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
