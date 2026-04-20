# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT


import os
import subprocess
import sys
import re
from datetime import datetime
from pathlib import Path

# ==============================================================================
# 🔧 KONFIGURATION
# ==============================================================================

# --- 1. System-Pfade und Listen (manuell anpassen, falls nötig) ---

# Namen der FFmpeg-Programme. Wenn FFmpeg im System-PATH ist, reicht dies.
# Andernfalls den vollen Pfad angeben, z.B. "C:/ffmpeg/bin/ffmpeg.exe"
FFMPEG_PATH = "ffmpeg.exe"
FFPROBE_PATH = "ffprobe.exe"

# Liste aller zu verarbeitenden Quelldateien
SOURCE_AUDIO_EXTENSIONS = {".aiff", ".flac", ".ogg", ".wav", ".m4a", ".wma", ".aac", ".mp3"}

# --- 2. Funktion zur dynamischen Erstellung und Validierung der Projekt-Pfade ---
def setup_and_validate_paths(ac_number, disk_archive_id):
    """
    Erstellt und validiert die Projekt-Pfade für das Audio-Konvertierungsskript.

    Args:
        ac_number (str): Die AC-Nummer.
        disk_archive_id (str): Die Datenträger-ID.

    Returns:
        dict: Ein Dictionary mit den validierten Pfaden oder None bei einem Fehler.
    """
    project_base_path = Path.home() / "Documents/data" / ac_number / disk_archive_id
    transfer_folder = project_base_path / f"3_{disk_archive_id}_for-transfer"

    paths = {
        "input_folder": transfer_folder / "files",
        "log_file_path": transfer_folder / f"3_{disk_archive_id}_for-transfer_audio-conversion.log"
    }

    if not paths["input_folder"].is_dir():
        print(f"\033[91mFehler: Der Eingabe-Ordner wurde nicht gefunden:\n{paths['input_folder']}\033[0m")
        return None
        
    if not paths["log_file_path"].parent.is_dir():
        print(f"\033[91mFehler: Der Ordner für die Log-Datei existiert nicht:\n{paths['log_file_path'].parent}\033[0m")
        return None

    # Überprüfen, ob ffmpeg und ffprobe gefunden werden können
    import shutil
    if not shutil.which(FFMPEG_PATH):
        print(f"\033[91mFehler: '{FFMPEG_PATH}' wurde nicht gefunden.\033[0m")
        print("\033[93mStellen Sie sicher, dass FFmpeg installiert und zum System-PATH hinzugefügt wurde, oder geben Sie den vollen Pfad in der Konfiguration an.\033[0m")
        return None
    if not shutil.which(FFPROBE_PATH):
        print(f"\033[91mFehler: '{FFPROBE_PATH}' wurde nicht gefunden.\033[0m")
        return None

    print("\033[92mAlle Pfade und Programme wurden erfolgreich gefunden und validiert.\033[0m")
    return paths

# ==============================================================================
# --- SKRIPT-LOGIK ---
# ==============================================================================

# Globale Variable für den Log-Pfad, wird im Hauptteil gesetzt
LOG_FILE_PATH = None

def log(message):
    """Schreibt eine Nachricht mit Zeitstempel in die Log-Datei und auf die Konsole."""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
    full_message = timestamp + message
    print(full_message)
    if LOG_FILE_PATH:
        try:
            with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
                f.write(full_message + "\n")
        except Exception as e:
            print(f"\033[91mKRITISCHER FEHLER: Konnte nicht in Log-Datei schreiben: {e}\033[0m")

def get_duration(input_path):
    """Gibt die Dauer der Audiodatei in Sekunden zurück."""
    try:
        result = subprocess.run(
            [FFPROBE_PATH, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_path],
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

    command = [FFMPEG_PATH, "-y", "-i", input_path]
    if codec_options:
        command.extend(codec_options)
    command.extend([output_path, "-progress", "pipe:1", "-nostats", "-loglevel", "error"])

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, encoding='utf-8', errors='replace')
    
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

# ==============================================================================
# --- HAUPT-AUSFÜHRUNGSBLOCK ---
# ==============================================================================
if __name__ == "__main__":
    # NEU: Liest die Werte von der Kommandozeile
    try:
        ac_number_input = sys.argv[1]
        disk_archive_id_input = sys.argv[2]
        print(f"Werte aus der Kommandozeile erhalten: AC={ac_number_input}, ID={disk_archive_id_input}")
    except IndexError:
        print("FEHLER: AC-Nummer und Datenträger-ID wurden nicht übergeben.")
        print("Dieses Skript sollte über 'start.bat' gestartet werden.")
        sys.exit(1)

    validated_paths = setup_and_validate_paths(ac_number_input, disk_archive_id_input)

    if validated_paths:
        input_folder = validated_paths["input_folder"]
        LOG_FILE_PATH = validated_paths["log_file_path"]

        # Log-Datei vor dem ersten Schreiben löschen, um altes Log zu entfernen
        if os.path.exists(LOG_FILE_PATH):
            os.remove(LOG_FILE_PATH)

        print("\nSkript wird mit folgenden Pfaden ausgeführt:")
        print(f"- Eingabe-Ordner: {input_folder}")
        print(f"- Log-Datei: {LOG_FILE_PATH}\n")

        log("Starte Audio-Konvertierungsskript.")

        source_files = []
        for root, _, files in os.walk(input_folder):
            for filename in files:
                if filename.startswith('.') or filename.startswith('~'):
                    continue
                
                # Verbesserte Logik zur Erkennung von bereits konvertierten Dateien
                parts = os.path.splitext(filename.lower())[0].split('.')
                if len(parts) >= 2:
                    original_ext = f".{parts[-1]}"
                    current_ext = os.path.splitext(filename)[1].lower()
                    if original_ext in SOURCE_AUDIO_EXTENSIONS and current_ext in {".mp3", ".wav"}:
                        continue

                ext = os.path.splitext(filename)[1].lower()
                if ext in SOURCE_AUDIO_EXTENSIONS:
                    source_files.append(os.path.join(root, filename))

        if not source_files:
            log("Keine zu konvertierenden Quelldateien gefunden. Skript wird beendet.")
        else:
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

        # --- ANFANG: HINZUGEFÜGTER CODE-BLOCK ---
        # Der Zielordner ist der übergeordnete Ordner des Eingabeordners (also der "for-transfer"-Ordner)
        destination_folder = validated_paths["input_folder"].parent
        
        # --- Zielordner optional öffnen ---
        print("")
        open_folder = input("Zielordner oeffnen? (j/n): ").lower()
        if open_folder == 'j':
            if sys.platform == "win32":
                os.startfile(destination_folder)
            elif sys.platform == "darwin":
                subprocess.run(["open", destination_folder])
            else:
                subprocess.run(["xdg-open", destination_folder])
            # Angepasst an den Stil des bestehenden Skripts
            print("\033[92mZielordner geoeffnet\033[0m")
        # --- ENDE: HINZUGEFÜGTER CODE-BLOCK ---

    else:
        print("\nSkript wird aufgrund von Konfigurationsfehlern beendet.")

    print("\nSkript beendet.")