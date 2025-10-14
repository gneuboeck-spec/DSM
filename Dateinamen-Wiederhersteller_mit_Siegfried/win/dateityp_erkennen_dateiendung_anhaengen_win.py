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

# --- ANPASSUNG FÜR WINDOWS ---
# Bitte ersetzen Sie den folgenden Pfad durch den tatsächlichen Pfad zu Ihrem Ordner.
# Path.home() findet automatisch den Benutzerordner (z.B. C:\Users\IhrName).
# Sie können auch einen festen Pfad wie Path("C:/Pfad/Zum/Ordner") verwenden.
try:
    base_path = Path.home() / "Desktop" / "Hammerl_original"
except Exception:
    # Fallback, falls der Desktop-Pfad nicht ermittelt werden kann
    base_path = Path("C:/Users/digit/Desktop/Hammerl_original") # Bitte anpassen

siegfried_to_ext_map = {
    "Microsoft Word for Macintosh Document": ".doc",
    "AppleWorks Word Processing": ".cwk",
    "ClarisWorks Word Processor": ".cwk",
    "MIME Email": ".eml",
    "Plain Text File": ".txt"
}

# Setzen Sie diesen Wert auf False, um Dateien tatsächlich umzubenennen.
# Bei True wird nur eine Simulation durchgeführt.
DRY_RUN = True

# ==============================================================================
# --- Skript-Logik (ab hier nichts mehr ändern) ---
# ==============================================================================

def log(message):
    """Gibt eine Nachricht auf der Konsole aus."""
    print(message)

def run_siegfried_on_file(filepath):
    """Führt Siegfried für eine einzelne Datei aus und gibt das JSON-Ergebnis zurück."""
    try:
        # HINWEIS FÜR WINDOWS:
        # Stellt sicher, dass der Befehl 'sf' (oder 'sf.exe') im System-PATH
        # gefunden wird, damit Python ihn ausführen kann.
        command = ["sf", "-json", str(filepath)]
        process = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
        return json.loads(process.stdout)
    except FileNotFoundError:
        log("❌ KRITISCHER FEHLER: Siegfried-Befehl 'sf.exe' nicht im System-PATH gefunden.")
        log("   Bitte stellen Sie sicher, dass Siegfried installiert und zum PATH hinzugefügt wurde.")
        sys.exit(1)
    except subprocess.CalledProcessError:
        # Dieser Fehler kann auftreten, wenn Siegfried einen Fehlercode zurückgibt.
        return None
    except json.JSONDecodeError:
        log(f"⚠️  Warnung: Konnte die JSON-Ausgabe von Siegfried für {filepath.name} nicht parsen.")
        return None
    except Exception as e:
        log(f"❌ Unerwarteter Fehler bei der Analyse von {filepath.name}: {e}")
        return None

def main():
    """Hauptfunktion des Skripts."""
    if DRY_RUN:
        log("🚨 SIMULATIONSMODUS AKTIV. Es werden keine Dateien umbenannt.")
        log("   Setzen Sie 'DRY_RUN = False' im Skript, um die Umbenennung durchzuführen.\n")

    if not base_path.is_dir():
        log(f"❌ FEHLER: Der angegebene Ordner '{base_path}' existiert nicht.")
        log("   Bitte passen Sie die Variable 'base_path' im Skript an.")
        sys.exit(1)

    log(f"Analysiere Verzeichnis: {base_path}")
    
    files_to_check = []
    
    # Eine Liste bekannter, "sicherer" Dateiendungen.
    # Dateien ohne eine dieser Endungen werden von Siegfried geprüft.
    known_safe_extensions = {
        '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', '.txt',
        '.jpg', '.jpeg', '.png', '.gif', '.tiff', '.mp3', '.wav', '.mp4', '.mov',
        '.eml', '.cwk', '.zip', '.rtf', '.pages', '.key', '.numbers'
    }

    for root, _, files in os.walk(base_path):
        for filename in files:
            # Ignoriere versteckte Dateien (beginnen mit einem Punkt)
            if filename.startswith('.'):
                continue
            
            # Prüfe, ob die Dateiendung nicht in der Liste der bekannten Endungen ist.
            _ , extension = os.path.splitext(filename)
            
            if extension.lower() not in known_safe_extensions:
                files_to_check.append(Path(root) / filename)

    if not files_to_check:
        log("\n✅ Keine Dateien mit unbekannter/fehlender Endung gefunden. Nichts zu tun.")
        return

    log(f"\n{len(files_to_check)} Datei(en) mit unbekannter/fehlender Endung gefunden. Starte Siegfried-Analyse...")
    print("-" * 40)

    renamed_count = 0
    unidentified_count = 0

    for filepath in files_to_check:
        result = run_siegfried_on_file(filepath)
        
        if result and result.get("files"):
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
                            # Umbenennung durchführen
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
             log(f"❓ Nicht erkannt (oder Fehler bei Siegfried): '{filepath.name}'")
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