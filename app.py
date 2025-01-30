from flask import Flask, render_template, send_file, Response
import os
import subprocess
import sys

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start')
def start():
    try:
        # Utiliser sys.executable pour s'assurer que nous utilisons le bon interpréteur Python
        result = subprocess.run([sys.executable, 'partition.py'], capture_output=True, text=True, check=True)
        print(result.stdout)  # Pour le débogage
        print(result.stderr)  # Pour le débogage

        # Vérifiez si les fichiers ont bien été générés
        mp3_path = 'static/quantum_music_harmonic.mp3'
        image_path = 'static/picture/quantum_music_harmonic_sheet_1.png'
        if os.path.exists(mp3_path) and os.path.exists(image_path):
            return "Le programme a été lancé avec succès. La musique et la partition sont en cours de génération."
        else:
            return "Erreur : Fichiers générés manquants.", 500
    except subprocess.CalledProcessError as e:
        # Capturer la sortie d'erreur pour le débogage
        return f"Erreur lors de l'exécution du script: {e.stderr}"

@app.route('/music')
def music():
    # Chemin du fichier MP3
    mp3_path = 'static/quantum_music_harmonic.mp3'
    if os.path.exists(mp3_path):
        return send_file(mp3_path, as_attachment=False, mimetype='audio/mpeg')
    else:
        return "Fichier MP3 introuvable.", 404

@app.route('/sheet')
def sheet():
    # Chemin du fichier PDF
    pdf_path = 'quantum_music_harmonic_sheet.pdf'
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=False, mimetype='application/pdf')
    else:
        return "Fichier PDF introuvable.", 404

@app.route('/image')
def image():
    # Chemin du fichier image généré depuis le PDF
    image_folder = 'static/picture'
    image_path = os.path.join(image_folder, 'quantum_music_harmonic_sheet_1.png')
    if os.path.exists(image_path):
        return send_file(image_path, as_attachment=False, mimetype='image/png')
    else:
        return "Image non trouvée.", 404

if __name__ == '__main__':
    app.run(debug=True)
