import qiskit
from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit import transpile
import mido
import random
import pygame
from music21 import converter, midi, stream, metadata, environment
import subprocess  # Ajouté pour appeler LilyPond

def simulate_circuit(qc):
    simulator = Aer.get_backend("qasm_simulator")
    compiled_circuit = transpile(qc, simulator)
    job = simulator.run(compiled_circuit, shots=1)
    result = job.result()
    counts = result.get_counts()
    if counts:
        return list(counts.keys())[0]
    else:
        return qc.num_qubits

def quantum_walk_circuit(num_qubits, steps):
    qc = QuantumCircuit(num_qubits, num_qubits)
    qc.h(range(num_qubits))  # Superposition initiale
    for _ in range(steps):
        for qubit in range(num_qubits):
            qc.rx(random.uniform(0, 2 * 3.14159), qubit)  # Rotation X aléatoire
            qc.ry(random.uniform(0, 2 * 3.14159), qubit)  # Rotation Y aléatoire
        qc.barrier()
    qc.measure_all()
    return qc

def binary_to_midi_note(binary_state):
    reversed_state = binary_state[::-1]  # Inverser la chaîne binaire
    decimal = int(reversed_state.replace(" ", ""), 2)  # Convertir en décimal
    scale = [60, 62, 64, 65, 67, 69, 71, 72]  # 8 notes spécifiques (C4 à C5)
    return scale[decimal % len(scale)]  # Réduire à la gamme de 8 notes

# Initialisation MIDI
midi_file = mido.MidiFile()
track = mido.MidiTrack()
midi_file.tracks.append(track)

tempo = mido.bpm2tempo(120)
track.append(mido.MetaMessage('set_tempo', tempo=tempo))

ticks_per_beat = midi_file.ticks_per_beat
note_duration_ticks = int(ticks_per_beat / 4)  # Une note par quart de temps

num_qubits = 4
steps = 10
duration = 30  # Durée totale en secondes
notes_per_second = 4
total_notes = int(duration * notes_per_second)

# Génération des notes
current_time = 0  # Temps courant en ticks
for _ in range(total_notes):
    circuit = quantum_walk_circuit(num_qubits, steps)
    state = simulate_circuit(circuit)
    note = binary_to_midi_note(state)

    print(f"État binaire mesuré : {state}, Note MIDI : {note}")  # Debugging

    # Ajouter la note MIDI
    track.append(mido.Message('note_on', note=note, velocity=64, time=current_time))
    track.append(mido.Message('note_off', note=note, velocity=64, time=note_duration_ticks))
    current_time = note_duration_ticks  # Temps entre les notes

# Sauvegarde du fichier MIDI
midi_file.save('quantum_music_fixed.mid')
print("Partition corrigée : quantum_music_fixed.mid")

# Définir le chemin vers LilyPond
lilypond_path = "D:/A5_Esilv/QuantumProject/QuantumSong/LilyPond/usr/bin/lilypond.exe"  # Remplacer par le chemin correct

# Mettre à jour le chemin de LilyPond dans les paramètres music21
us = environment.UserSettings()
us['lilypondPath'] = lilypond_path

# Génération de la partition musicale
def generate_sheet_music(midi_filename, output_filename="quantum_sheet_music"):
    # Utilisation du converter de music21 pour lire directement le fichier MIDI
    try:
        score = converter.parse(midi_filename)
    except Exception as e:
        print(f"Erreur lors de la conversion du MIDI : {e}")
        return
    
    # Sauvegarder la partition en fichier LilyPond
    try:
        score.write('lily', fp=f"{output_filename}.ly")  # Générer le fichier LilyPond
        print(f"Fichier LilyPond généré : {output_filename}.ly")
        
        # Appeler LilyPond pour générer le PDF une seule fois
        subprocess.run([lilypond_path, f"{output_filename}.ly"], check=True)
        print(f"Partition générée : {output_filename}.pdf")
    except Exception as e:
        print(f"Erreur lors de l'exportation en PDF : {e}")

# Génération de la partition musicale
try:
    generate_sheet_music('quantum_music_fixed.mid', output_filename="quantum_music_sheet")
except Exception as e:
    print(f"Erreur lors de la génération de la partition : {e}")

# Lecture avec pygame
pygame.mixer.init()
try:
    pygame.mixer.music.load('quantum_music_fixed.mid')
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
except pygame.error as e:
    print(f"Erreur lors de la lecture du fichier MIDI: {e}")
