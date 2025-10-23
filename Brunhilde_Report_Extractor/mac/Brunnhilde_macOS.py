# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

#!/usr/bin/env python3
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
# 🔧 KONFIGURATION
# ==============================================================================
BASE_DIR = sys.argv[1] if len(sys.argv) > 1 else "/Users/gregorneuboeck/Desktop/Test_Metadaten auslesen"
BRUNHILDE_OUTPUT_DIR = "/Users/gregorneuboeck/Desktop/Brunhilde_Reports"
OUTPUT_JSON = "/Users/gregorneuboeck/Desktop/brunhilde_summary.json"

# ==============================================================================
# --- Skript-Logik (Exakt aus Ihrem funktionierenden Skript übernommen) ---
# ==============================================================================

def run_command(command, env=None, stream_output=False):
    """
    Führt einen Shell-Befehl aus.
    Dies ist die Version aus Ihrem funktionierenden Hauptskript.
    """
    stdout_target = sys.stdout if stream_output else subprocess.PIPE
    stderr_target = sys.stderr if stream_output else subprocess.PIPE
    try:
        result = subprocess.run(command, stdout=stdout_target, stderr=stderr_target, text=True, check=False, env=env)
        return result.stdout, result.stderr, result.returncode
    except FileNotFoundError:
        print(f"Fehler: Befehl nicht gefunden: '{command[0]}'.")
        return "", f"Befehl nicht gefunden: '{command[0]}'", -1
    except Exception as e:
        print(f"Unerwarteter Fehler beim Ausführen von Befehl '{' '.join(command)}': {e}")
        return "", str(e), -1

def list_directory_contents(path):
    """Listet rekursiv den Inhalt eines Verzeichnisses auf."""
    contents = []
    if path.exists() and path.is_dir():
        for root_dir, dirs, files in os.walk(path):
            current_level = Path(root_dir).relative_to(path)
            for d in dirs:
                contents.append(f"  - {current_level / d}/")
            for f in files:
                contents.append(f"  - {current_level / f}")
    return contents

def extract_brunhilde_info(source_path):
    """
    Führt Brunhilde aus und extrahiert Metadaten.
    Dies ist die Version aus Ihrem funktionierenden Hauptskript.
    """
    brunhilde_metadata = {}
    brunhilde_output_base_dir = None
    is_temp_dir = False

    if BRUNHILDE_OUTPUT_DIR: 
        brunhilde_output_base_dir = Path(BRUNHILDE_OUTPUT_DIR)
        brunhilde_output_base_dir.mkdir(parents=True, exist_ok=True)
    else:
        brunhilde_output_base_dir = Path(tempfile.mkdtemp(prefix="brunhilde_output_"))
        is_temp_dir = True

    identifier = Path(source_path).name.replace('.', '_') + "_collection_report"
    brunhilde_report_path = brunhilde_output_base_dir / identifier

    try:
        if brunhilde_report_path.exists():
            print(f"Lösche vorhandenen Brunhilde-Berichtsordner: {brunhilde_report_path}")
            shutil.rmtree(brunhilde_report_path)

        brunhilde_command = [
            sys.executable, "-m", "brunnhilde",
            str(source_path),
            str(brunhilde_report_path)
        ]
        
        print(f"\n--- Führe Brunhilde aus für {source_path} (mit ClamAV)... ---")
        print(f"Befehl: {' '.join(brunhilde_command)}")
        
        stdout, stderr, returncode = run_command(brunhilde_command, env=os.environ.copy(), stream_output=True) 
        
        print(f"Brunhilde Exit Code: {returncode}")
        print(f"--- Brunhilde-Ausführung beendet ---")
        
        if not brunhilde_report_path.exists():
            print(f"Fehler: Brunhilde-Berichtsordner nicht gefunden unter {brunhilde_report_path}.")
            if returncode != 0:
                print(f"Hinweis: Brunhilde beendete sich mit Exit Code {returncode}.")
            return brunhilde_metadata

        csv_reports_dir = brunhilde_report_path / "csv_reports"
        if not csv_reports_dir.exists():
            print(f"Warnung: CSV-Berichtsverzeichnis nicht gefunden unter {csv_reports_dir}.")
            return brunhilde_metadata
        
        # Parsen von formats.csv
        formats_csv = csv_reports_dir / "formats.csv"
        if formats_csv.exists():
            with open(formats_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                brunhilde_metadata['brunhilde_format_summary'] = json.dumps([row for row in reader])

        # Parsen von mimetypes.csv
        mimetypes_csv = csv_reports_dir / "mimetypes.csv"
        if mimetypes_csv.exists():
            with open(mimetypes_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                brunhilde_metadata['brunhilde_mime_type_summary'] = json.dumps([row for row in reader])
        
        # Parsen von siegfried_warnings.csv
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

        # Parsen von unidentified.csv
        unidentified_csv = csv_reports_dir / "unidentified.csv"
        if unidentified_csv.exists():
            with open(unidentified_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                unidentified_paths = {row.get('File', '').strip() for row in reader if row.get('File', '').strip()}
            brunhilde_metadata['structured_unidentified_files'] = list(unidentified_paths)

        # Parsen von virus_scan_log.txt
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
    analysis_path = sys.argv[1] if len(sys.argv) > 1 else BASE_DIR

    if not Path(analysis_path).is_dir():
        print(f"FEHLER: Das angegebene Verzeichnis '{analysis_path}' existiert nicht.")
        sys.exit(1)

    analysis_results = extract_brunhilde_info(analysis_path)
    
    if analysis_results:
        print("\n--- Zusammenfassung der Brunhilde-Analyse ---")
        
        # Speichern der Ergebnisse in eine JSON-Datei
        try:
            with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                json.dump(analysis_results, f, indent=2, ensure_ascii=False)
            print(f"\nErgebnisse erfolgreich nach {OUTPUT_JSON} geschrieben.")
        except Exception as e:
            print(f"\nFehler beim Schreiben der JSON-Datei: {e}")
            
    else:
        print("\nKonnte keine Metadaten aus den Brunhilde-Berichten extrahieren.")

    print("Skript beendet.")