# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import subprocess
import json
import sys
import mimetypes
from pathlib import Path
import shutil # Hinzugefügt für shutil.which

# ==============================================================================
# 🔧 KONFIGURATION
# ==============================================================================

base_path = Path("/Users/gregorneuboeck/Desktop/Hammerl_original")

# Pfad zu ffprobe
ffprobe_path_config = "/usr/local/bin/ffprobe"

# Manuelles Mapping für PRONOM IDs
pronom_to_ext_map = {
    # Alte Mac-Formate
    "fmt/846": ".cwk",       # ClarisWorks Word Processor
    "x-fmt/65": ".doc",      # Microsoft Word for Macintosh Document
    "fmt/1439": ".pages",    # Apple iWork Pages
    
    # Musik-Software
    "fmt/397": ".mus",       # Enigma Binary File (Finale)
    
    # Video & Audio
    "fmt/569": ".mkv",       # Matroska
    "fmt/279": ".flac",      # FLAC (Free Lossless Audio Codec)
    "fmt/1038": ".r3d",      # Redcode RAW (R3D) Media File
    "fmt/134": ".ts",        # MPEG-2 Transport Stream (aus einem anderen Fall)
    "fmt/585": ".ts",        # MPEG-2 Transport Stream (dein aktueller Fall)
    "fmt/203": ".ogg",      # Ogg Vorbis (erzwingt .ogg statt .oga)
    "fmt/946": ".opus",      # Ogg Opus

    # Dokumente & Sonstiges
    "fmt/280": ".tex",       # LaTeX (Master document)
    "fmt/838": ".dbx",       # Outlook Express Message Database
    "x-fmt/191": ".sam",     # AMI Professional Document
    "x-fmt/18": ".csv",      # Comma-Separated Values (CSV)
}

# Manuelles Mapping für Formatnamen (Fallback)
format_name_to_ext_map = {
    "AppleWorks Word Processing": ".cwk",
}

DRY_RUN = True

# ==============================================================================
# --- Skript-Logik (ab hier nichts mehr ändern) ---
# ==============================================================================

ffprobe_is_available = False

mimetypes.add_type('message/rfc822', '.eml', strict=False)
mimetypes.init()

def log(message):
    print(message)

def run_command_with_json_output(command):
    try:
        process = subprocess.run(command, capture_output=True, text=True)
        if process.returncode != 0:
            return None
        if process.stdout:
            return json.loads(process.stdout)
        return None
    except FileNotFoundError:
        return "not_found"
    except json.JSONDecodeError:
        return None
    except Exception as e:
        log(f"❌ Unerwarteter Fehler bei der Ausführung von '{command[0]}': {e}")
        return None

def has_video_stream(filepath):
    """Prüft mit ffprobe, ob eine Datei eine Videospur enthält."""
    if not ffprobe_is_available:
        return None 

    command = [
        ffprobe_path_config, "-v", "error", "-show_entries", "stream=codec_type",
        "-select_streams", "v", "-of", "json", str(filepath)
    ]
    result = run_command_with_json_output(command)
    
    if result and result.get("streams"):
        return True
    return False

def determine_extension(filepath, match):
    """Ermittelt die Dateiendung mit einer intelligenten Kaskade."""
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
    global ffprobe_is_available

    if DRY_RUN:
        log("🚨 SIMULATIONSMODUS AKTIV. Es werden keine Dateien umbenannt.")
        log("   Setzen Sie 'DRY_RUN = False' im Skript, um scharf zu schalten.\n")

    if ffprobe_path_config and shutil.which(ffprobe_path_config):
        ffprobe_is_available = True
    else:
        log(f"⚠️  Warnung: ffprobe nicht unter '{ffprobe_path_config}' gefunden. Tiefenanalyse für MP4 ist deaktiviert.")

    if not base_path.is_dir():
        log(f"❌ FEHLER: Der angegebene Ordner '{base_path}' existiert nicht.")
        sys.exit(1)

    log(f"Analysiere Verzeichnis: {base_path}")
    
    files_to_check = []
    for root, _, files in os.walk(base_path):
        for filename in files:
            if not filename.startswith('.') and "." not in filename:
                files_to_check.append(Path(root) / filename)

    if not files_to_check:
        log("\n✅ Keine Dateien ohne Dateiendung gefunden. Nichts zu tun.")
        return

    log(f"{len(files_to_check)} Datei(en) ohne Endung gefunden. Starte Analyse...")
    print("-" * 40)

    renamed_count = 0
    unidentified_count = 0

    for filepath in files_to_check:
        siegfried_result = run_command_with_json_output(["sf", "-json", str(filepath)])
        
        if siegfried_result:
            matches = siegfried_result.get("files", [{}])[0].get("matches", [])
            if matches:
                match = matches[0]
                format_name = match.get("format")
                
                new_ext, source = determine_extension(filepath, match)

                if new_ext:
                    new_path = filepath.with_suffix(new_ext)
                    
                    prefix = "[SIMULATION]" if DRY_RUN else "✅ Umbenannt"
                    log(f"{prefix}: '{filepath.name}' -> '{new_path.name}' [via {source}]")
                    
                    if not DRY_RUN:
                        try:
                            if new_path.exists() and not filepath.samefile(new_path):
                                log(f"    ⚠️  ZIELDATEI EXISTIERT BEREITS: '{new_path.name}'. Überspringe.")
                                continue
                            filepath.rename(new_path)
                        except OSError as e:
                            log(f"    ❌ FEHLER beim Umbenennen: {e}")
                            continue
                    
                    renamed_count += 1
                else:
                    log(f"❓ Nicht zugeordnet: '{filepath.name}' (Erkannt als: {format_name})")
                    unidentified_count += 1
            else:
                log(f"❓ Nicht erkannt: '{filepath.name}'")
                unidentified_count += 1
        else:
             log(f"❓ Nicht erkannt (Siegfried-Fehler): '{filepath.name}'")
             unidentified_count += 1

    print("-" * 40)
    status = "simuliert umbenannt" if DRY_RUN else "tatsächlich umbenannt"
    log(f"Analyse abgeschlossen.")
    log(f"Dateien {status}: {renamed_count}")
    log(f"Dateien nicht zugeordnet: {unidentified_count}")

    if DRY_RUN and unidentified_count > 0:
        log("\nEs gibt nicht zugeordnete Dateien. Erwägen Sie, deren PRONOM-ID zur 'pronom_to_ext_map' hinzuzufügen.")

    if DRY_RUN and renamed_count > 0:
        log("\n⚠️  Wenn das Ergebnis korrekt aussieht, setzen Sie DRY_RUN = False")
        log("    im Skript und führen Sie es erneut aus.")

if __name__ == "__main__":
    main()