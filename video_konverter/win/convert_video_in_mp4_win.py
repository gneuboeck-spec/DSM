# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import subprocess
import sys
from datetime import datetime

# --- KONFIGURATION (Für Windows 11 anpassen) ---

# 1. Geben Sie hier den Pfad zum Ordner ein, der Ihre Videos enthält.
#    Verwenden Sie normale Slashes (/), Python wandelt sie korrekt um.
input_folder = "C:/Users/digit/Desktop/Videodateien_konvertieren"

# 2. Pfad für die Log-Datei (wird automatisch im input_folder erstellt)
log_file_path = os.path.join(input_folder, "video_konvertierung.log")

# 3. Liste der zu verarbeitenden Quellformate.
#    .mp4 wird hier absichtlich ausgelassen.
source_video_extensions = {".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm", ".mpg", ".mpeg", ".m4v", ".vob", ".m2ts"}
# --- ENDE DER KONFIGURATION ---


# Ersetze "IhrBenutzername" im Pfad, falls es noch der Platzhalter ist
if "IhrBenutzername" in input_folder:
    print("="*60)
    print("BITTE BEARBEITEN SIE DAS SKRIPT!")
    print("Ersetzen Sie 'IhrBenutzername' in der Variable 'input_folder' mit Ihrem tatsächlichen Windows-Benutzernamen.")
    print("="*60)
    sys.exit(1)


def log(message):
    """Schreibt eine Nachricht mit Zeitstempel in die Log-Datei und auf die Konsole."""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
    try:
        # Erstelle den Ordner für die Log-Datei, falls er nicht existiert
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(timestamp + message + "\n")
    except Exception as e:
        print(f"KRITISCHER FEHLER: Konnte nicht in Log-Datei schreiben: {e}")
    print(timestamp + message)


def convert_to_mp4(input_path, output_path):
    """
    Konvertiert eine Videodatei nach MP4 mit FFmpeg.
    Überschreibt die Zieldatei dank des '-y' Parameters automatisch.
    Gibt True bei Erfolg, False bei Fehler zurück.
    """
    log(f"Starte Konvertierung: {os.path.basename(input_path)} → {os.path.basename(output_path)}")
    
    command = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_path
    ]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        log(f"[OK] Erfolgreich konvertiert: {os.path.basename(output_path)}")
        return True
    except FileNotFoundError:
        log("[KRITISCHER FEHLER] ffmpeg wurde nicht gefunden. Ist es installiert und im System-PATH?")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        log(f"[FEHLER] Konvertierung fehlgeschlagen für: {os.path.basename(input_path)}")
        log(f"         FFmpeg-Fehler: {e.stderr.strip()}")
        return False


# --- HAUPTPROGRAMM ---
log("Starte Video-Konvertierungsskript (Modus: Überschreiben).")

if not os.path.isdir(input_folder):
    log(f"FEHLER: Der Eingabe-Ordner wurde nicht gefunden: {input_folder}")
    sys.exit(1)

# Schritt 1: Finde alle relevanten Quelldateien
source_files = []
for root, _, files in os.walk(input_folder):
    for filename in files:
        if filename.startswith('.') or filename.startswith('~'):
            continue

        ext = os.path.splitext(filename)[1].lower()
        if ext in source_video_extensions:
            source_files.append(os.path.join(root, filename))

if not source_files:
    log("Keine zu konvertierenden Videodateien gefunden. Skript wird beendet.")
    sys.exit()

log(f"{len(source_files)} Quelldateien gefunden. Beginne Verarbeitung...")

# Schritt 2: Verarbeite jede Quelldatei
converted_count = 0
for input_path in source_files:
    root, filename = os.path.split(input_path)
    
    mp4_target_path = os.path.join(root, f"{filename}.mp4")
    
    log(f"--- Verarbeite '{filename}' ---")
    
    if convert_to_mp4(input_path, mp4_target_path):
        converted_count += 1

log(f"Videokonvertierung abgeschlossen. {converted_count} von {len(source_files)} Dateien erfolgreich konvertiert.")
