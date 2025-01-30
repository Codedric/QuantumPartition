import qiskit
from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit import transpile
import mido
import random
from music21 import converter, environment
import subprocess
import os
import fitz


# Fonction pour simuler le circuit quantique
def simulate_circuit(qc):
    simulator = Aer.get_backend("qasm_simulator")
    compiled_circuit = transpile(qc, simulator)
    job = simulator.run(compiled_circuit, shots=1)
    result = job.result()
    counts = result.get_counts()
    if counts:
        return list(counts.keys())[0]
    else:
        return '0' * qc.num_qubits

# Fonction pour créer le circuit de marche quantique
def quantum_walk_circuit(num_qubits, steps):
    qc = QuantumCircuit(num_qubits, num_qubits)
    qc.h(range(num_qubits))
    for _ in range(steps):
        for qubit in range(num_qubits):
            qc.rx(random.uniform(0, 2 * 3.14159), qubit)
            qc.ry(random.uniform(0, 2 * 3.14159), qubit)
        qc.barrier()
    qc.measure_all()
    return qc

# Fonction pour convertir l'état binaire en note MIDI
def binary_to_midi_note(binary_state):
    reversed_state = binary_state[::-1]
    decimal = int(reversed_state.replace(" ", ""), 2)
    scale = [60, 62, 64, 65, 67, 69, 71, 72]
    return scale[decimal % len(scale)]

# Fonction pour générer un accord basé sur l'état binaire
def generate_chords(state, base_note):
    modifiers = [4, 7]
    chords = []
    if state[0]=='1':
        duration = 2*note_duration_ticks
    else :
        duration = note_duration_ticks
    chords.append(duration)
    chords.append(base_note)
    if state[1]=='0':
        modifiers[0]=3
    for i, bit in enumerate(state):
        if i > 1:
            if bit == '1':
                chords.append(base_note + modifiers[i-2])
    return chords

# Initialisation MIDI
midi_file = mido.MidiFile()
track = mido.MidiTrack()
midi_file.tracks.append(track)

# Définir le tempo et les ticks par battement
tempo = mido.bpm2tempo(120)
track.append(mido.MetaMessage('set_tempo', tempo=tempo))
ticks_per_beat = midi_file.ticks_per_beat
note_duration_ticks = int(ticks_per_beat / 3)

# Paramètres
num_qubits = 4
steps = 10
duration = 15
notes_per_second = 3
total_notes = int(duration * notes_per_second)

# Génération des notes
current_time = 0  # Temps courant en ticks
for _ in range(total_notes):
    circuit = quantum_walk_circuit(num_qubits, steps)
    state = simulate_circuit(circuit)
    base_note = binary_to_midi_note(state)
    
    # Création d'un deuxième circuit pour les accords
    chord_circuit = quantum_walk_circuit(num_qubits, steps)
    chord_state = simulate_circuit(chord_circuit)
    chords = generate_chords(chord_state, base_note)
    duration=chords[0]
    chords.pop(0)
    
    print(f"État binaire mesuré : {state}, Accord : {chords}")  # Debugging
    
    # Ajouter les accords MIDI
    for note in chords:
        track.append(mido.Message('note_on', note=note, velocity=64, time=current_time))
    for note in chords:
        track.append(mido.Message('note_off', note=note, velocity=64, time=duration))
    current_time = 0

# Sauvegarde du fichier MIDI
midi_path = 'static/quantum_music_harmonic.mid'
midi_file.save(midi_path)
print(f"Partition harmonieuse sauvegardée : {midi_path}")

# Conversion du MIDI en MP3 avec MuseScore
def convert_midi_to_mp3_with_musescore(midi_path, mp3_path):
    if os.path.exists(midi_path):
        try:
            subprocess.run(["MuseScore4", midi_path, "--export-to", mp3_path], check=True)
            print(f"Fichier MP3 généré : {mp3_path}")
        except Exception as e:
            print(f"Erreur lors de la conversion MIDI en MP3 avec MuseScore : {e}")
    else:
        print("Le fichier MIDI est introuvable.")

mp3_path = 'static/quantum_music_harmonic.mp3'
convert_midi_to_mp3_with_musescore(midi_path, mp3_path)

# Génération de la partition musicale avec LilyPond
def generate_sheet_music(midi_filename, output_filename="static/quantum_music_harmonic_sheet"):
    try:
        score = converter.parse(midi_filename)
    except Exception as e:
        print(f"Erreur lors de la conversion du MIDI : {e}")
        return

    try:
        score.write('lily', fp=f"{output_filename}.ly")  # Générer le fichier LilyPond
        print(f"Fichier LilyPond généré : {output_filename}.ly")
        
        # Appeler LilyPond pour générer le PDF
        subprocess.run(["lilypond", f"{output_filename}.ly"], check=True)
        print(f"Partition générée : {output_filename}.pdf")
    except Exception as e:
        print(f"Erreur lors de l'exportation en PDF : {e}")

generate_sheet_music(midi_path, output_filename="static/quantum_music_harmonic_sheet")

def convert_pdf_to_image(pdf_path, image_folder, image_name="quantum_music_harmonic_sheet"):
    try:
        # Ouvre le document PDF
        doc = fitz.open(pdf_path)
        
        # Créez le dossier de destination s'il n'existe pas
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)

        # Parcourt chaque page du PDF
        for i in range(len(doc)):
            page = doc.load_page(i)
            pix = page.get_pixmap(dpi=300)

            # Définir le chemin pour sauvegarder l'image
            image_path = os.path.join(image_folder, f"{image_name}_{i + 1}.png")
            pix.save(image_path)
            print(f"Image sauvegardée : {image_path}")

    except Exception as e:
        print(f"Erreur lors de la conversion du PDF en image : {e}")

# Exemple d'appel de la fonction
pdf_path = 'quantum_music_harmonic_sheet.pdf'
image_folder = 'static/picture'

# Appel à la fonction pour convertir le PDF en images
convert_pdf_to_image(pdf_path, image_folder)
