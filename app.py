from flask import Flask, request, render_template, send_file
import os
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']

    if not file:
        return "No file uploaded", 400

    # Sauvegarder le fichier CSV temporairement
    filepath = os.path.join('uploads', file.filename)
    file.save(filepath)

    # Lancer le script main.py avec le fichier CSV en entrée
    subprocess.run(["python3", "script/main.py", filepath])

    # Après l'exécution de main.py, retourner le fichier CSV généré en sortie
    output_filepath = 'output/output.csv'  # Met à jour en fonction de l'endroit où le CSV est généré
    return send_file(output_filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
