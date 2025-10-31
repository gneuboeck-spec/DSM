# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
# SPDX-FileCopyrightText: 2025 Google LLC (für Windows-Anpassungen)
#
# SPDX-License-Identifier: MIT

import os
import subprocess
import json
import sys
import mimetypes
from pathlib import Path
import shutil  # Wird für shutil.which benötigt, um Programme im PATH zu finden
from datetime import datetime # NEU: Für Zeitstempel im Log

# ==============================================================================
# 🔧 KONFIGURATION (für Windows 11 angepasst)
# ==============================================================================

# 1. Geben Sie den Pfad zu dem Ordner an, der analysiert werden soll.
#    (FEHLER KORRIGIERT: Backslash nach C: hinzugefügt)
base_path = r"C:\Users\digit\Desktop\AC15993802\ZPH1705-120_04-12-03-01\2_ZPH1705-120_04-12-03-01_extracted-files\Files"

# 2. Pfad zu ffprobe.exe (Teil von FFmpeg)
ffprobe_path_config = "ffprobe.exe"

# 3. NEU: Pfad für die Log-Datei
#    Alle Ausgaben werden in diese Datei geschrieben.
#    Lassen Sie den Wert leer (""), um das Logging in eine Datei zu deaktivieren.
log_file_path = r"C:\Users\digit\Desktop\AC15993802\ZPH1705-120_04-12-03-01\2_ZPH1705-120_04-12-03-01_extracted-files\protokoll.log"

# 4. Manuelles Mapping für PRONOM IDs zu Dateiendungen
pronom_to_ext_map = {
    # Alte Mac-Formate
    "fmt/846": ".cwk",       # ClarisWorks Word Processor
    "x-fmt/65": ".doc",      # Microsoft Word for Macintosh Document
    "fmt/1439": ".pages",    # Apple iWork Pages
    
    # Musik-Software
    "fmt/397": ".mus",       # Enigma Binary File (Finale)
    "x-fmt/23": ".mid",      # Musical Instrument Digital Interface (Standard-Variante)
    "x-fmt/230": ".mid",     # NEU (aus Ihrer Ausgabe): MIDI-Variante
    "fmt/575": ".musicxml",  # MusicXML (Standard-Variante)
    "fmt/896": ".musicxml",  # NEU (aus Ihrer Ausgabe): MusicXML-Variante
    
    # Video & Audio
    "fmt/569": ".mkv",       # Matroska
    "fmt/279": ".flac",      # FLAC (Free Lossless Audio Codec)
    "fmt/1038": ".r3d",      # Redcode RAW (R3D) Media File
    "fmt/134": ".ts",        # MPEG-2 Transport Stream
    "fmt/585": ".ts",        # MPEG-2 Transport Stream
    "fmt/203": ".ogg",       # Ogg Vorbis (erzwingt .ogg statt .oga)
    "fmt/946": ".opus",      # Ogg Opus
    "fmt/117": ".flv",       # Macromedia Flash Video (Standard-Variante)
    "x-fmt/382": ".flv",     # NEU (aus Ihrer Ausgabe): FLV-Variante
    "fmt/384": ".mxf",       # Material Exchange Format (Standard-Variante)
    "fmt/200": ".mxf",       # NEU (aus Ihrer Ausgabe): MXF-Variante

    # Bilder & Dokumente
    "fmt/120": ".psd",       # Adobe Photoshop Document (Standard-Variante)
    "x-fmt/92": ".psd",      # NEU (aus Ihrer Ausgabe): PSD-Variante
    "fmt/280": ".tex",       # LaTeX (Master document)
    "fmt/838": ".dbx",       # Outlook Express Message Database
    "x-fmt/191": ".sam",     # AMI Professional Document
    "x-fmt/18": ".csv",      # Comma-Separated Values (CSV)
    "fmt/291": ".odt",       # OpenDocument Text
}

# 5. Manuelles Mapping für Formatnamen (wird als Fallback verwendet)
format_name_to_ext_map = {
    "AppleWorks Word Processing": ".cwk",
}

# 6. SICHERHEITSSCHALTER:
#    True = Nur Simulation, es werden keine Änderungen vorgenommen.
#    False = Dateien werden tatsächlich umbenannt.
DRY_RUN = True

# ==============================================================================
# --- Skript-Logik (ab hier im Normalfall keine Änderungen nötig) ---
# ==============================================================================

ffprobe_path_executable = "" 
LOG_FILE_HANDLE = None # NEU: Globale Variable für die Log-Datei

mimetypes.add_type('message/rfc822', '.eml', strict=False)
mimetypes.init()

def log(message):
    """Gibt eine Nachricht auf der Konsole aus UND schreibt sie in die Log-Datei."""
    print(message)
    if LOG_FILE_HANDLE:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        LOG_FILE_HANDLE.write(f"[{timestamp}] {message}\n")

def run_command_with_json_output(command):
    """Führt einen Befehl aus und erwartet eine JSON-Ausgabe."""
    try:
        process = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        if process.returncode != 0:
            log(f"Fehler bei Ausführung von '{command[0]}': {process.stderr}")
            return None
        if process.stdout:
            return json.loads(process.stdout)
        return None
    except FileNotFoundError:
        log(f"❌ KRITISCHER FEHLER: Das Programm '{command[0]}' wurde nicht gefunden.")
        log("   Bitte stellen Sie sicher, dass es installiert und zur System-PATH-Umgebungsvariable hinzugefügt wurde.")
        return "not_found"
    except json.JSONDecodeError:
        log(f"Fehler: Konnte die Ausgabe von '{command[0]}' nicht als JSON verarbeiten.")
        return None
    except Exception as e:
        log(f"❌ Unerwarteter Fehler bei der Ausführung von '{command[0]}': {e}")
        return None

def has_video_stream(filepath):
    """Prüft mit ffprobe, ob eine Datei eine Videospur enthält."""
    if not ffprobe_path_executable:
        return None 

    command = [
        ffprobe_path_executable, "-v", "error", "-show_entries", "stream=codec_type",
        "-select_streams", "v", "-of", "json", str(filepath)
    ]
    result = run_command_with_json_output(command)
    
    if result and result.get("streams"):
        return True
    return False

def determine_extension(filepath, match):
    """Ermittelt die Dateiendung anhand einer Prioritätenliste."""
    pronom_id = match.get("id")
    mime_type = match.get("mime")
    format_name = match.get("format")
    
    if pronom_id in pronom_to_ext_map:
        return pronom_to_ext_map[pronom_id], "PRONOM ID (Manuell)"
    
    if pronom_id == 'fmt/199': 
        video_check = has_video_stream(filepath)
        if video_check is True:
            return ".mp4", "MPEG-4 (mit Video)"
        elif video_check is False:
            return ".m4a", "MPEG-4 (nur Audio)"

    if mime_type:
        ext = mimetypes.guess_extension(mime_type)
        if ext:
            if ext == '.ksh' and mime_type == 'text/plain': ext = '.txt'
            if pronom_id == 'fmt/199':
                 return '.mp4', 'MPEG-4 (Standard)'
            return ext, "MIME-Typ (Automatisch)"
            
    if format_name in format_name_to_ext_map:
        return format_name_to_ext_map[format_name], "Formatname (Manuell)"
        
    return None, None

def main():
    global ffprobe_path_executable
    global LOG_FILE_HANDLE

    # NEU: Log-Datei initialisieren, bevor irgendetwas anderes passiert
    if log_file_path:
        try:
            log_dir = Path(log_file_path).parent
            log_dir.mkdir(parents=True, exist_ok=True)
            LOG_FILE_HANDLE = open(log_file_path, 'w', encoding='utf-8')
        except IOError as e:
            # Wenn das Log nicht erstellt werden kann, auf Konsole ausgeben und beenden
            print(f"❌ KRITISCHER FEHLER: Log-Datei konnte nicht erstellt werden unter '{log_file_path}': {e}")
            sys.exit(1)

    try:
        # --- Start der eigentlichen Skript-Logik ---
        log(f"Skript gestartet am {datetime.now().strftime('%Y-%m-%d um %H:%M:%S Uhr')}")
        log("-" * 40)
        
        if DRY_RUN:
            log("🚨 SIMULATIONSMODUS AKTIV. Es werden keine Dateien umbenannt.")
            log("   Setzen Sie 'DRY_RUN = False' im Skript, um die Änderungen durchzuführen.\n")
        
        if not shutil.which("sf"):
            log("❌ KRITISCHER FEHLER: Siegfried ('sf.exe') nicht im System-PATH gefunden.")
            log("   Bitte installieren Sie Siegfried und fügen Sie es zum PATH hinzu. Das Skript wird beendet.")
            sys.exit(1)

        found_ffprobe_path = shutil.which(ffprobe_path_config)
        if found_ffprobe_path:
            ffprobe_path_executable = found_ffprobe_path
            log(f"✅ ffprobe gefunden unter: {ffprobe_path_executable}")
        else:
            log(f"⚠️  WARNUNG: '{ffprobe_path_config}' nicht gefunden. Tiefenanalyse für MP4/M4A ist deaktiviert.")

        path_obj = Path(base_path)

        if not path_obj.is_dir():
            log(f"❌ FEHLER: Der angegebene Ordner '{path_obj}' existiert nicht oder ist kein Verzeichnis.")
            sys.exit(1)

        log(f"\nAnalysiere Verzeichnis: {path_obj}")
        
        files_to_check = []
        for root, _, files in os.walk(path_obj):
            for filename in files:
                if not filename.startswith('.') and "." not in filename:
                    files_to_check.append(Path(root) / filename)

        if not files_to_check:
            log("\n✅ Keine Dateien ohne Dateiendung gefunden. Nichts zu tun.")
            return

        log(f"{len(files_to_check)} Datei(en) ohne Endung gefunden. Starte Analyse...")
        log("-" * 40)

        renamed_count = 0
        unidentified_count = 0

        for filepath in files_to_check:
            siegfried_result = run_command_with_json_output(["sf", "-json", str(filepath)])
            
            if siegfried_result == "not_found":
                sys.exit(1)
            
            if siegfried_result:
                matches = siegfried_result.get("files", [{}])[0].get("matches", [])
                if matches:
                    match = matches[0]
                    format_name = match.get("format", "Unbekannt")
                    pronom_id = match.get("id", "Keine ID")
                    
                    new_ext, source = determine_extension(filepath, match)

                    if new_ext:
                        new_path = filepath.with_suffix(new_ext)
                        prefix = "[SIMULATION]" if DRY_RUN else "✅ Umbenannt"
                        log(f"{prefix}: '{filepath.name}' -> '{new_path.name}' [via {source}]")
                        
                        if not DRY_RUN:
                            try:
                                if new_path.exists():
                                    log(f"    ⚠️  ZIELDATEI EXISTIERT BEREITS: '{new_path.name}'. Überspringe.")
                                    continue
                                filepath.rename(new_path)
                                renamed_count += 1
                            except OSError as e:
                                log(f"    ❌ FEHLER beim Umbenennen: {e}")
                                continue
                        else:
                            renamed_count += 1
                    else:
                        log(f"❓ Nicht zugeordnet: '{filepath.name}' (Erkannt als: {format_name}, PRONOM: {pronom_id})")
                        unidentified_count += 1
                else:
                    log(f"❓ Nicht erkannt (kein Siegfried-Match): '{filepath.name}'")
                    unidentified_count += 1
            else:
                log(f"❓ Nicht erkannt (Siegfried-Fehler): '{filepath.name}'")
                unidentified_count += 1

        log("-" * 40)
        status = "simuliert umbenannt" if DRY_RUN else "tatsächlich umbenannt"
        log(f"Analyse abgeschlossen.")
        log(f"Dateien {status}: {renamed_count}")
        log(f"Dateien nicht zugeordnet: {unidentified_count}")

        if unidentified_count > 0:
            log("\nTipp: Fügen Sie die PRONOM-ID von 'nicht zugeordneten' Dateien zur 'pronom_to_ext_map' hinzu.")

        if DRY_RUN and renamed_count > 0:
            log("\n⚠️  Wenn das Ergebnis korrekt aussieht, setzen Sie DRY_RUN = False")
            log("    im Skript und führen Sie es erneut aus, um die Dateien umzubenennen.")

    finally:
        # NEU: Stellt sicher, dass die Log-Datei immer geschlossen wird, auch bei einem Fehler.
        if LOG_FILE_HANDLE:
            log("-" * 40)
            log(f"Protokoll wurde gespeichert unter: {log_file_path}")
            LOG_FILE_HANDLE.close()

if __name__ == "__main__":
    main()