# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import subprocess
import json
import sys
from pathlib import Path

# ==============================================================================
# 🔧 KONFIGURATION
# ==============================================================================

base_path = Path("/Users/gregorneuboeck/Desktop/Hammerl_original")

siegfried_to_ext_map = {
    "Microsoft Word for Macintosh Document": ".doc",
    "AppleWorks Word Processing": ".cwk",
    "ClarisWorks Word Processor": ".cwk",
    "MIME Email": ".eml",
    "Plain Text File": ".txt"
}

DRY_RUN = True

# ==============================================================================
# --- Skript-Logik (ab hier nichts mehr ändern) ---
# ==============================================================================

def log(message):
    print(message)

def run_siegfried_on_file(filepath):
    try:
        command = ["sf", "-json", str(filepath)]
        process = subprocess.run(command, capture_output=True, text=True, check=True)
        return json.loads(process.stdout)
    except FileNotFoundError:
        log("❌ KRITISCHER FEHLER: Siegfried-Befehl 'sf' nicht im System-PATH gefunden. Skript wird beendet.")
        sys.exit(1)
    except subprocess.CalledProcessError:
        return None
    except json.JSONDecodeError:
        log(f"⚠️  Warnung: Konnte die JSON-Ausgabe von Siegfried für {filepath.name} nicht parsen.")
        return None
    except Exception as e:
        log(f"❌ Unerwarteter Fehler bei der Analyse von {filepath.name}: {e}")
        return None

def main():
    if DRY_RUN:
        log("🚨 SIMULATIONSMODUS AKTIV. Es werden keine Dateien umbenannt.")
        log("   Setzen Sie 'DRY_RUN = False' im Skript, um scharf zu schalten.\n")

    if not base_path.is_dir():
        log(f"❌ FEHLER: Der angegebene Ordner '{base_path}' existiert nicht.")
        sys.exit(1)

    log(f"Analysiere Verzeichnis: {base_path}")
    
    files_to_check = []
    
    # KORREKTUR: Wir definieren, was eine "normale" Endung ist.
    # Alles, was keine dieser Endungen hat, wird geprüft.
    known_safe_extensions = {
        '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', '.txt',
        '.jpg', '.jpeg', '.png', '.gif', '.tiff', '.mp3', '.wav', '.mp4', '.mov',
        '.eml', '.cwk', '.zip', '.rtf', '.pages', '.key', '.numbers'
    }

    for root, _, files in os.walk(base_path):
        for filename in files:
            if filename.startswith('.'):
                continue
            
            # KORREKTUR: Wir prüfen jetzt, ob die Endung der Datei NICHT in unserer Liste bekannter Endungen ist.
            _ , extension = os.path.splitext(filename)
            
            if extension.lower() not in known_safe_extensions:
                files_to_check.append(Path(root) / filename)

    if not files_to_check:
        log("\n✅ Keine Dateien mit unbekannter/fehlender Endung gefunden. Nichts zu tun.")
        return

    log(f"{len(files_to_check)} Datei(en) mit unbekannter/fehlender Endung gefunden. Starte Siegfried-Analyse...")
    print("-" * 40)

    renamed_count = 0
    unidentified_count = 0

    for filepath in files_to_check:
        result = run_siegfried_on_file(filepath)
        
        if result:
            matches = result.get("files", [{}])[0].get("matches", [])
            if matches:
                format_name = matches[0].get("format")
                if format_name in siegfried_to_ext_map:
                    new_ext = siegfried_to_ext_map[format_name]
                    new_path = filepath.with_suffix(new_ext)
                    
                    prefix = "[SIMULATION]" if DRY_RUN else "✅ Umbenannt"
                    log(f"{prefix}: '{filepath.name}' -> '{new_path.name}' (Erkannt als: {format_name})")
                    
                    if not DRY_RUN:
                        try:
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
             log(f"❓ Nicht erkannt: '{filepath.name}'")
             unidentified_count += 1

    print("-" * 40)
    status = "simuliert umbenannt" if DRY_RUN else "tatsächlich umbenannt"
    log(f"Analyse abgeschlossen.")
    log(f"Dateien {status}: {renamed_count}")
    log(f"Dateien nicht erkannt/zugeordnet: {unidentified_count}")

    if DRY_RUN and renamed_count > 0:
        log("\n⚠️  Wenn das Ergebnis korrekt aussieht, setzen Sie DRY_RUN = False")
        log("    im Skript und führen Sie es erneut aus, um die Dateien wirklich umzubenennen.")

if __name__ == "__main__":
    main()