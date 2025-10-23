# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

# Dieses Skript wurde für die Ausführung unter Windows optimiert.
# Es enthält nun einen manuellen Workaround, um die 'tree.txt' zuverlässig
# zu generieren, falls Brunhilde dies nicht automatisch erledigt.

import os
import sys
import json
import subprocess
import re
import tempfile
import shutil
import csv
from pathlib import Path

# ==============================================================================
# 🔧 KONFIGURATION (BITTE FÜR IHR WINDOWS-SYSTEM ANPASSEN)
# ==============================================================================

# --- Pfade zu den Verzeichnissen der externen Tools ---
# Tragen Sie hier die Pfade zu den Ordnern ein, die die .exe-Dateien enthalten.
SIEGFRIED_DIR = r"C:\Program Files\Siegfried"
CLAMAV_DIR = ""  # Beispiel: r"C:\Program Files\ClamAV"

# --- Standard-Verzeichnisse ---
user_desktop = Path.home() / "Desktop"
BASE_DIR = sys.argv[1] if len(sys.argv) > 1 else user_desktop / "Test_Metadaten auslesen"
BRUNHILDE_OUTPUT_DIR = user_desktop / "Brunhilde_Reports"
OUTPUT_JSON = user_desktop / "brunhilde_summary.json"


# ==============================================================================
# --- Skript-Logik (Angepasst für robuste Ausführung unter Windows) ---
# ==============================================================================

def run_command(command, env=None, stream_output=False):
    """Führt einen Shell-Befehl aus."""
    stdout_target = sys.stdout if stream_output else subprocess.PIPE
    stderr_target = sys.stderr if stream_output else subprocess.PIPE
    try:
        result = subprocess.run(command, stdout=stdout_target, stderr=stderr_target, text=True, check=False, env=env, encoding='utf-8', errors='replace')
        return result.stdout, result.stderr, result.returncode
    except FileNotFoundError:
        print(f"Fehler: Befehl nicht gefunden: '{command[0]}'.")
        return "", f"Befehl nicht gefunden: '{command[0]}'", -1
    except Exception as e:
        print(f"Unerwarteter Fehler beim Ausführen von Befehl '{' '.join(command)}': {e}")
        return "", str(e), -1

def extract_brunhilde_info(source_path):
    """
    Führt Brunhilde aus, erstellt manuell die tree.txt und extrahiert Metadaten.
    """
    brunhilde_metadata = {}
    brunhilde_output_base_dir = Path(BRUNHILDE_OUTPUT_DIR) if BRUNHILDE_OUTPUT_DIR else Path(tempfile.mkdtemp(prefix="brunhilde_output_"))
    is_temp_dir = not BRUNHILDE_OUTPUT_DIR

    brunhilde_output_base_dir.mkdir(parents=True, exist_ok=True)

    identifier = Path(source_path).name.replace('.', '_') + "_collection_report"
    brunhilde_report_path = brunhilde_output_base_dir / identifier

    try:
        if brunhilde_report_path.exists():
            print(f"Lösche vorhandenen Brunhilde-Berichtsordner: {brunhilde_report_path}")
            shutil.rmtree(brunhilde_report_path)

        # --- Umgebungs-Setup für Brunhilde ---
        env = os.environ.copy()
        tool_paths = [path for path in [SIEGFRIED_DIR, CLAMAV_DIR] if path and Path(path).exists()]
        
        if tool_paths:
            original_path = env.get('PATH', '')
            env['PATH'] = os.pathsep.join(tool_paths) + os.pathsep + original_path
            print(f"Info: Der System-PATH wird temporär erweitert.")

        brunhilde_command = [
            sys.executable, "-m", "brunnhilde",
            str(source_path),
            str(brunhilde_report_path)
        ]
        
        print(f"\n--- Führe Brunhilde aus für {source_path}... ---")
        print(f"Befehl: {' '.join(brunhilde_command)}")
        
        stdout, stderr, returncode = run_command(brunhilde_command, env=env, stream_output=True) 
        
        print(f"Brunhilde Exit Code: {returncode}")
        print(f"--- Brunhilde-Ausführung beendet ---")
        
        # =================================================================
        # HIER BEGINNT DER NEUE, EINGEFÜGTE CODE-BLOCK FÜR TREE.TXT
        # =================================================================
        try:
            # Stellt sicher, dass der Zielordner existiert, bevor tree.txt geschrieben wird.
            brunhilde_report_path.mkdir(exist_ok=True)
            tree_output_file = brunhilde_report_path / "tree.txt"
            
            print(f"\n--- Erstelle 'tree.txt' manuell als Workaround... ---")
            
            # Verwendet 'cmd /c' für maximale Kompatibilität unter Windows
            tree_command = f'cmd /c tree "{str(source_path)}" /A /F > "{str(tree_output_file)}"'
            
            print(f"Führe Befehl aus: {tree_command}")
            # subprocess.run wird hier verwendet, da es robust ist und Fehler abfängt.
            subprocess.run(tree_command, shell=True, check=True, text=True, encoding='utf-8', errors='replace')
            
            if tree_output_file.exists() and tree_output_file.stat().st_size > 0:
                print(f"--- 'tree.txt' erfolgreich erstellt unter: {tree_output_file} ---")
            else:
                print(f"--- WARNUNG: 'tree.txt' konnte nicht manuell erstellt werden oder ist leer. ---")
        except subprocess.CalledProcessError as e:
            print(f"--- FEHLER beim Ausführen von 'tree.exe': Befehl schlug fehl mit Code {e.returncode}. ---")
            print(f"   Stderr: {e.stderr}")
        except Exception as e:
            print(f"--- FEHLER beim manuellen Erstellen von 'tree.txt': {e} ---")
        # =================================================================
        # HIER ENDET DER NEUE CODE-BLOCK
        # =================================================================

        if not brunhilde_report_path.exists():
            print(f"Fehler: Brunhilde-Berichtsordner nicht gefunden unter {brunhilde_report_path}.")
            if returncode != 0:
                print(f"Hinweis: Brunhilde beendete sich mit Exit Code {returncode}. Prüfen Sie die obige Ausgabe auf Fehler.")
            return brunhilde_metadata

        # --- Parsing der Brunhilde-Berichte (unverändert) ---
        csv_reports_dir = brunhilde_report_path / "csv_reports"
        if not csv_reports_dir.exists():
            print(f"Warnung: CSV-Berichtsverzeichnis nicht gefunden unter {csv_reports_dir}.")
            # Wir brechen hier nicht ab, da tree.txt vielleicht trotzdem erstellt wurde
            # und das Parsen der anderen Dateien weitergehen kann.
        
        # Parsen von formats.csv
        formats_csv = csv_reports_dir / "formats.csv"
        if formats_csv.exists():
            with open(formats_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                brunhilde_metadata['brunhilde_format_summary'] = json.dumps([row for row in reader])

        # ... (Rest des Parsings bleibt identisch) ...
        mimetypes_csv = csv_reports_dir / "mimetypes.csv"
        if mimetypes_csv.exists():
            with open(mimetypes_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                brunhilde_metadata['brunhilde_mime_type_summary'] = json.dumps([row for row in reader])
        
        warnings_by_file_path = {}
        siegfried_warnings_csv = csv_reports_dir / "siegfried_warnings.csv"
        if siegfried_warnings_csv.exists():
            with open(siegfried_warnings_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    file_path = row.get('File', '').strip()
                    if file_path:
                        warnings_by_file_path.setdefault(file_path, []).append(row)
            brunhilde_metadata['structured_siegfried_warnings'] = warnings_by_file_path

        unidentified_csv = csv_reports_dir / "unidentified.csv"
        if unidentified_csv.exists():
            with open(unidentified_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                unidentified_paths = {row.get('File', '').strip() for row in reader if row.get('File', '').strip()}
            brunhilde_metadata['structured_unidentified_files'] = list(unidentified_paths)

        virus_scan_log = brunhilde_report_path / "virus_scan_log.txt"
        if virus_scan_log.exists():
            with open(virus_scan_log, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()
                infected_match = re.search(r"Infected files: (\d+)", log_content)
                if infected_match:
                    infected_count = int(infected_match.group(1))
                    brunhilde_metadata['brunhilde_clamav_infected_files'] = str(infected_count)
                    if infected_count > 0:
                        virus_details = re.findall(r"^(.*?): (.*?) FOUND$", log_content, re.MULTILINE)
                        brunhilde_metadata['brunhilde_clamav_virus_details'] = json.dumps(virus_details)
                else:
                    brunhilde_metadata['brunhilde_clamav_status'] = "Log gefunden, aber Infektionsstatus unklar."
        else:
            brunhilde_metadata['brunhilde_clamav_status'] = "Kein virus_scan_log.txt gefunden."

    except Exception as e:
        print(f"Fehler beim Ausführen oder Parsen von Brunhilde: {e}")
    finally:
        if is_temp_dir and brunhilde_output_base_dir.exists():
            shutil.rmtree(brunhilde_output_base_dir)
            
    return brunhilde_metadata

if __name__ == "__main__":
    analysis_path = Path(BASE_DIR)

    if not analysis_path.is_dir():
        print(f"FEHLER: Das angegebene Verzeichnis '{analysis_path}' existiert nicht.")
        sys.exit(1)

    analysis_results = extract_brunhilde_info(analysis_path)
    
    if analysis_results:
        print("\n--- Zusammenfassung der Brunhilde-Analyse ---")
        
        try:
            with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                json.dump(analysis_results, f, indent=2, ensure_ascii=False)
            print(f"\nErgebnisse erfolgreich nach {OUTPUT_JSON} geschrieben.")
        except Exception as e:
            print(f"\nFehler beim Schreiben der JSON-Datei: {e}")
            
    else:
        print("\nKonnte keine Metadaten aus den Brunhilde-Berichten extrahieren.")

    print("Skript beendet.")