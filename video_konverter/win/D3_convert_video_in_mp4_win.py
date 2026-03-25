# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import shutil

# ==============================================================================
# 🔧 KONFIGURATION
# ==============================================================================

# --- 1. System-Pfade und Listen (manuell anpassen, falls nötig) ---

# Name des FFmpeg-Programms. Wenn FFmpeg im System-PATH ist, reicht dies.
# Andernfalls den vollen Pfad angeben, z.B. "C:/ffmpeg/bin/ffmpeg.exe"
FFMPEG_PATH = "ffmpeg.exe"

# Liste der zu verarbeitenden Quellformate.
# .mp4 wird hier absichtlich ausgelassen.
SOURCE_VIDEO_EXTENSIONS = {".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm", ".mpg", ".mpeg", ".m4v", ".vob", ".m2ts", ".mts",
    ".mxf", ".ogm", ".ts"}

# --- 2. Funktion zur dynamischen Erstellung und Validierung der Projekt-Pfade ---
def setup_and_validate_paths(ac_number, disk_archive_id):
    """
    Erstellt und validiert die Projekt-Pfade für das Video-Konvertierungsskript.

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
        "log_file_path": transfer_folder / f"3_{disk_archive_id}_for-transfer_video-conversion.log"
    }

    if not paths["input_folder"].is_dir():
        print(f"\033[91mFehler: Der Eingabe-Ordner wurde nicht gefunden:\n{paths['input_folder']}\033[0m")
        return None
        
    if not paths["log_file_path"].parent.is_dir():
        print(f"\033[91mFehler: Der Ordner für die Log-Datei existiert nicht:\n{paths['log_file_path'].parent}\033[0m")
        return None

    # Überprüfen, ob ffmpeg gefunden werden kann
    if not shutil.which(FFMPEG_PATH):
        print(f"\033[91mFehler: '{FFMPEG_PATH}' wurde nicht gefunden.\033[0m")
        print("\033[93mStellen Sie sicher, dass FFmpeg installiert und zum System-PATH hinzugefügt wurde, oder geben Sie den vollen Pfad in der Konfiguration an.\033[0m")
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

def convert_to_mp4(input_path, output_path):
    """
    Konvertiert eine Videodatei nach MP4 mit FFmpeg.
    Gibt True bei Erfolg, False bei Fehler zurück.
    """
    log(f"Starte Konvertierung: {os.path.basename(input_path)} → {os.path.basename(output_path)}")
    
    command = [
        FFMPEG_PATH,
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
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
        log(f"[OK] Erfolgreich konvertiert: {os.path.basename(output_path)}")
        return True
    except subprocess.CalledProcessError as e:
        log(f"[FEHLER] Konvertierung fehlgeschlagen für: {os.path.basename(input_path)}")
        log(f"         FFmpeg-Fehler: {e.stderr.strip()}")
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

        log("Starte Video-Konvertierungsskript (Modus: Überschreiben).")

        # Finde alle relevanten Quelldateien
        source_files = []
        for root, _, files in os.walk(input_folder):
            for filename in files:
                if filename.startswith('.') or filename.startswith('~'):
                    continue

                # Logik zur Erkennung von bereits konvertierten Dateien
                name_part, ext_part = os.path.splitext(filename)
                current_ext = ext_part.lower()

                # Wenn die aktuelle Endung .mp4 ist UND der Dateiname davor auf eine unserer Quell-Endungen endet,
                # ist es bereits ein Derivat und wird übersprungen.
                is_derivative = False
                if current_ext == ".mp4":
                    for source_ext in SOURCE_VIDEO_EXTENSIONS:
                        if name_part.lower().endswith(source_ext):
                            is_derivative = True
                            break
                
                if is_derivative:
                    continue

                if current_ext in SOURCE_VIDEO_EXTENSIONS:
                    source_files.append(os.path.join(root, filename))

        if not source_files:
            log("Keine zu konvertierenden Videodateien gefunden. Skript wird beendet.")
        else:
            log(f"{len(source_files)} Quelldateien gefunden. Beginne Verarbeitung...")
            
            converted_count = 0
            for input_path in source_files:
                root, filename = os.path.split(input_path)
                
                mp4_target_path = os.path.join(root, f"{filename}.mp4")
                
                log(f"--- Verarbeite '{filename}' ---")
                
                if convert_to_mp4(input_path, mp4_target_path):
                    converted_count += 1

            log(f"Videokonvertierung abgeschlossen. {converted_count} von {len(source_files)} Dateien erfolgreich konvertiert.")

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