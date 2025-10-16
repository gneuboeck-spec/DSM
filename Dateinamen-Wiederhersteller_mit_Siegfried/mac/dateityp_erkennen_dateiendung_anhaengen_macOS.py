# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import subprocess
import json
import sys
import mimetypes
from pathlib import Path

# ==============================================================================
# 🔧 KONFIGURATION (unverändert)
# ==============================================================================
base_path = Path("/Users/gregorneuboeck/Desktop/Hammerl_original")
pronom_to_ext_map = {
    "fmt/397": ".mus",
    "fmt/846": ".cwk",
}
format_name_to_ext_map = {
    "AppleWorks Word Processing": ".cwk",
}
DRY_RUN = True
# ==============================================================================

# (Der Rest der Konfiguration und die Hilfsfunktionen bleiben exakt gleich)
mimetypes.add_type('message/rfc822', '.eml')
mimetypes.init()

def log(message):
    print(message)

def run_siegfried_on_file(filepath):
    try:
        command = ["sf", "-json", str(filepath)]
        process = subprocess.run(command, capture_output=True, text=True)
        if process.stdout:
            return json.loads(process.stdout)
        return None
    except FileNotFoundError:
        log("❌ KRITISCHER FEHLER: Siegfried-Befehl 'sf' nicht im System-PATH gefunden. Skript wird beendet.")
        sys.exit(1)
    except json.JSONDecodeError:
        return None
    except Exception as e:
        log(f"❌ Unerwarteter Fehler bei der Analyse von {filepath.name}: {e}")
        return None

def determine_extension(match):
    pronom_id = match.get("id")
    mime_type = match.get("mime")
    format_name = match.get("format")
    
    if pronom_id in pronom_to_ext_map:
        return pronom_to_ext_map[pronom_id], "PRONOM ID"
    
    if mime_type:
        ext = mimetypes.guess_extension(mime_type)
        if ext:
            if ext == '.ksh' and mime_type == 'text/plain': ext = '.txt'
            return ext, "MIME-Typ"

    if format_name in format_name_to_ext_map:
        return format_name_to_ext_map[format_name], "Formatname"
        
    return None, None

def main():
    if DRY_RUN:
        log("🚨 SIMULATIONSMODUS AKTIV. Es werden keine Dateien umbenannt.")
        log("   Setzen Sie 'DRY_RUN = False' im Skript, um scharf zu schalten.\n")

    if not base_path.is_dir():
        log(f"❌ FEHLER: Der angegebene Ordner '{base_path}' existiert nicht.")
        sys.exit(1)

    log(f"Analysiere Verzeichnis: {base_path}")
    
    files_to_check = []
    known_safe_extensions = {
        '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', '.txt',
        '.jpg', '.jpeg', '.png', '.gif', '.tiff', '.mp3', '.wav', '.mp4', '.mov',
        '.eml', '.cwk', '.zip', '.rtf', '.pages', '.key', '.numbers', '.musicxml', '.mus'
    }

    for root, _, files in os.walk(base_path):
        for filename in files:
            if filename.startswith('.'):
                continue
            
            _ , extension = os.path.splitext(filename)
            if extension.lower() not in known_safe_extensions:
                files_to_check.append(Path(root) / filename)

    if not files_to_check:
        log("\n✅ Keine Dateien mit unbekannter/fehlender Endung gefunden. Nichts zu tun.")
        return

    log(f"{len(files_to_check)} Datei(en) zur Analyse gefunden. Starte Siegfried...")
    print("-" * 40)

    renamed_count = 0
    unidentified_count = 0

    for filepath in files_to_check:
        result = run_siegfried_on_file(filepath)
        
        if result:
            matches = result.get("files", [{}])[0].get("matches", [])
            if matches:
                match = matches[0]
                format_name = match.get("format")
                
                new_ext, source = determine_extension(match)
                
                if new_ext:
                    # ================================================
                    # --- KORRIGIERTE LOGIK ZUR NAMENSGEBUNG ---
                    # ================================================
                    # Wir nehmen den originalen Dateinamen und hängen einfach die neue Endung an.
                    # Der str(filepath) stellt sicher, dass der komplette Pfad erhalten bleibt.
                    new_path_str = str(filepath) + new_ext
                    new_path = Path(new_path_str)
                    # ================================================
                    
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
                log(f"❓ Nicht erkannt (kein Match): '{filepath.name}'")
                unidentified_count += 1
        else:
             log(f"❓ Nicht erkannt (Siegfried-Fehler): '{filepath.name}'")
             unidentified_count += 1

    # ... (Abschlussbericht bleibt unverändert) ...
    print("-" * 40)
    status = "simuliert umbenannt" if DRY_RUN else "tatsächlich umbenannt"
    log(f"Analyse abgeschlossen.")
    log(f"Dateien {status}: {renamed_count}")
    log(f"Dateien nicht automatisch zugeordnet: {unidentified_count}")

    if DRY_RUN and unidentified_count > 0:
        log("\nEs gibt nicht zugeordnete Dateien. Fügen Sie deren PRONOM-ID zur 'pronom_to_ext_map' hinzu.")

    if DRY_RUN and renamed_count > 0:
        log("\n⚠️  Wenn das Ergebnis korrekt aussieht, setzen Sie DRY_RUN = False")
        log("    im Skript und führen Sie es erneut aus.")

if __name__ == "__main__":
    main()