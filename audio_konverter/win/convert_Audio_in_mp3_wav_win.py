# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import subprocess
import sys
import re
from datetime import datetime

# === KONFIGURATION (Für Windows 11 anpassen) ===

# 1. Geben Sie hier den Pfad zum Ordner ein, der Ihre Audiodateien enthält.
#    Verwenden Sie normale Slashes (/), Python wandelt sie korrekt um.
input_folder = "C:/Users/digit/Desktop/Audiodateien_konvertieren"

# 2. Pfad für die Log-Datei (wird automatisch im input_folder erstellt)
log_file_path = os.path.join(input_folder, "audio_conversion_log.txt")

# 3. Namen der FFmpeg-Programme. Wenn FFmpeg im PATH ist, reicht dies.
#    Andernfalls den vollen Pfad angeben, z.B. "C:/ffmpeg/bin/ffmpeg.exe"
ffmpeg_path = "ffmpeg.exe"
ffprobe_path = "ffprobe.exe"

# 4. Liste aller zu verarbeitenden Quelldateien (unverändert)
source_audio_extensions = {".aiff", ".flac", ".ogg", ".wav", ".m4a", ".wma", ".aac", ".mp3"}
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
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(timestamp + message + "\n")
    except Exception as e:
        print(f"KRITISCHER FEHLER: Konnte nicht in Log-Datei schreiben: {e}")
    print(timestamp + message)


def get_duration(input_path):
    """Gibt die Dauer der Audiodatei in Sekunden zurück."""
    try:
        result = subprocess.run(
            [ffprobe_path, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_path],
            capture_output=True, text=True, check=True
        )
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
        log(f"[FEHLER] Dauer für '{os.path.basename(input_path)}' konnte nicht ermittelt werden.")
        return None

def convert_with_progress(input_path, output_path, codec_options=None):
    """Konvertiert eine Audiodatei mit FFmpeg und zeigt eine Fortschrittsanzeige an."""
    duration = get_duration(input_path)
    if duration is None:
        return False

    log(f"Starte Konvertierung: {os.path.basename(input_path)} → {os.path.basename(output_path)}")

    command = [ffmpeg_path, "-y", "-i", input_path]
    if codec_options:
        command.extend(codec_options)
    command.extend([output_path, "-progress", "pipe:1", "-nostats", "-loglevel", "error"])

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    
    while True:
        line = process.stdout.readline()
        if not line:
            break
        match = re.search(r'out_time_ms=(\d+)', line)
        if match:
            current_time_ms = int(match.group(1))
            progress = min(current_time_ms / (duration * 1_000_000), 1.0) if duration > 0 else 1.0
            bar = "#" * int(progress * 40)
            sys.stdout.write(f"\r[{bar:<40}] {progress*100:.1f}%")
            sys.stdout.flush()

    process.wait()
    sys.stdout.write('\r' + ' ' * 80 + '\r')
    sys.stdout.flush()

    if process.returncode == 0:
        log(f"[OK] Erfolgreich konvertiert: {os.path.basename(output_path)}")
        return True
    else:
        stderr_output = process.stderr.read()
        log(f"[FEHLER] Konvertierung fehlgeschlagen für: {os.path.basename(input_path)}")
        if stderr_output:
            log(f"         FFmpeg-Fehler: {stderr_output.strip()}")
        return False

# --- HAUPTPROGRAMM ---
log("Starte Audio-Konvertierungsskript.")

if not os.path.isdir(input_folder):
    log(f"FEHLER: Der Eingabe-Ordner wurde nicht gefunden: {input_folder}")
    sys.exit(1)

source_files = []
for root, _, files in os.walk(input_folder):
    for filename in files:
        if filename.startswith('.') or filename.startswith('~'):
            continue
        parts = filename.lower().split('.')
        if len(parts) >= 3 and f".{parts[-2]}" in source_audio_extensions and f".{parts[-1]}" in {".mp3", ".wav"}:
            continue

        ext = os.path.splitext(filename)[1].lower()
        if ext in source_audio_extensions:
            source_files.append(os.path.join(root, filename))

if not source_files:
    log("Keine zu konvertierenden Quelldateien gefunden. Skript wird beendet.")
    sys.exit()

log(f"{len(source_files)} Quelldateien gefunden. Beginne Verarbeitung...")

for input_path in source_files:
    root, filename = os.path.split(input_path)
    name, ext = os.path.splitext(filename)
    ext = ext.lower()
    
    log(f"--- Verarbeite '{filename}' ---")
    
    mp3_target_path = os.path.join(root, f"{filename}.mp3")
    wav_target_path = os.path.join(root, f"{filename}.wav")
    
    if ext not in {".mp3", ".wav"}:
        log("-> Fremdformat erkannt. Erstelle MP3 und WAV.")
        convert_with_progress(input_path, mp3_target_path, codec_options=["-c:a", "libmp3lame", "-q:a", "2"])
        convert_with_progress(input_path, wav_target_path, codec_options=["-c:a", "pcm_s16le"])
    elif ext == ".mp3":
        log("-> MP3-Original erkannt. Erstelle nur WAV.")
        convert_with_progress(input_path, wav_target_path, codec_options=["-c:a", "pcm_s16le"])
    elif ext == ".wav":
        log("-> WAV-Original erkannt. Erstelle nur MP3.")
        convert_with_progress(input_path, mp3_target_path, codec_options=["-c:a", "libmp3lame", "-q:a", "2"])

log("Alle Audio-Konvertierungen abgeschlossen.")
