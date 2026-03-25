# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT


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

SIEGFRIED_DIR = r"C:\Program Files\Siegfried"
CLAMAV_DIR = ""  # Leer lassen, wenn nicht verwendet, z.B.: r"C:\Program Files\ClamAV"


# --- 2. Funktion zur dynamischen Erstellung und Validierung der Projekt-Pfade ---
def setup_and_validate_analysis_paths(ac_number, disk_archive_id, siegfried_dir, clamav_dir):
    """
    Erstellt und validiert die Projekt-Pfade für die Analyse mit Brunnhilde, Siegfried etc.
    und prüft die Verfügbarkeit der externen Tools.
    """
    project_base_path = Path.home() / "Documents/data" / ac_number / disk_archive_id
    extracted_files_path = project_base_path / f"2_{disk_archive_id}_extracted-files"

    paths = {
        "base_dir": extracted_files_path / "files",
        "brunnhilde_output_dir": extracted_files_path / f"2_{disk_archive_id}_extracted-files_brunnhilde",
        "output_json": extracted_files_path / f"2_{disk_archive_id}_extracted-files_brunnhilde-summary.json",
        "siegfried_dir": Path(siegfried_dir) if siegfried_dir else None,
        "clamav_dir": Path(clamav_dir) if clamav_dir else None,
        "final_json_path": extracted_files_path / f"2_{disk_archive_id}_extracted-files_brunnhilde-summary.json",
        "final_tree_path": extracted_files_path / f"2_{disk_archive_id}_extracted-files_tree.txt",
    }

    if not paths["base_dir"].is_dir():
        print(f"\033[91mFehler: Das Basis-Verzeichnis mit den Dateien wurde nicht gefunden:\n{paths['base_dir']}\033[0m")
        return None
    
    if not extracted_files_path.is_dir():
        print(f"\033[91mFehler: Das Verzeichnis für die extrahierten Dateien wurde nicht gefunden:\n{extracted_files_path}\033[0m")
        return None

    if paths["siegfried_dir"]:
        siegfried_exe = paths["siegfried_dir"] / "sf.exe"
        if not siegfried_exe.is_file():
            print(f"\033[91mFehler: 'sf.exe' wurde nicht im Siegfried-Verzeichnis gefunden:\n{paths['siegfried_dir']}\033[0m")
            return None
    else:
        print("\033[93mWarnung: Kein Pfad für Siegfried (SIEGFRIED_DIR) angegeben.\033[0m")

    if paths["clamav_dir"]:
        clamav_exe = paths["clamav_dir"] / "clamscan.exe"
        if not clamav_exe.is_file():
            print(f"\033[91mFehler: 'clamscan.exe' wurde nicht im ClamAV-Verzeichnis gefunden:\n{paths['clamav_dir']}\033[0m")
            return None

    print("\033[92mAlle Projekt-Pfade und Tools wurden erfolgreich gefunden und validiert.\033[0m")
    return paths

# ==============================================================================
# --- Skript-Logik (Angepasst für robuste Ausführung unter Windows) ---
# ==============================================================================

# <<< HIER IST DIE EINZIGE KORREKTUR >>>
def run_command(command, env=None, stream_output=False):
    """
    Führt einen Shell-Befehl aus. Verwendet shell=True, um Probleme mit dem
    Python Launcher / Inkscape auf Windows zu umgehen.
    """
    stdout_target = sys.stdout if stream_output else subprocess.PIPE
    stderr_target = sys.stderr if stream_output else subprocess.PIPE
    try:
        # Der Befehl wird als String übergeben, was für shell=True erforderlich ist.
        # Pfade mit Leerzeichen werden durch Anführungszeichen geschützt.
        command_str = ' '.join(f'"{arg}"' for arg in command)
        
        result = subprocess.run(command_str, stdout=stdout_target, stderr=stderr_target, text=True, check=False, env=env, encoding='utf-8', errors='replace', shell=True)
        return result.stdout, result.stderr, result.returncode
    except FileNotFoundError:
        print(f"Fehler: Befehl nicht gefunden: '{command[0]}'.")
        return "", f"Befehl nicht gefunden: '{command[0]}'", -1
    except Exception as e:
        print(f"Unerwarteter Fehler beim Ausführen von Befehl '{' '.join(command)}': {e}")
        return "", str(e), -1

def extract_brunnhilde_info(source_path, brunnhilde_output_dir):
    """
    Führt Brunnhilde aus, erstellt manuell die tree.txt und extrahiert Metadaten.
    """
    brunnhilde_metadata = {}
    
    brunnhilde_output_base_dir = Path(brunnhilde_output_dir) if brunnhilde_output_dir else Path(tempfile.mkdtemp(prefix="brunnhilde_output_"))
    is_temp_dir = not brunnhilde_output_dir

    brunnhilde_output_base_dir.mkdir(parents=True, exist_ok=True)

    identifier = Path(source_path).name.replace('.', '_') + "_collection_report"
    brunnhilde_report_path = brunnhilde_output_base_dir / identifier

    try:
        if brunnhilde_report_path.exists():
            print(f"Lösche vorhandenen Brunnhilde-Berichtsordner: {brunnhilde_report_path}")
            shutil.rmtree(brunnhilde_report_path)

        env = os.environ.copy()
        
        tool_paths = [path for path in [SIEGFRIED_DIR, CLAMAV_DIR] if path and Path(path).exists()]
        if tool_paths:
            env['PATH'] = os.pathsep.join(tool_paths) + os.pathsep + env['PATH']
            print(f"Info: Umgebung für Brunnhilde wird temporär erweitert.")
        
        brunnhilde_command = [
            sys.executable, "-m", "brunnhilde",
            str(source_path),
            str(brunnhilde_report_path)
        ]
        
        print(f"\n--- Führe Brunnhilde aus für {source_path}... ---")
        print(f"Befehl: {' '.join(brunnhilde_command)}")
        
        stdout, stderr, returncode = run_command(brunnhilde_command, env=env, stream_output=True) 
        
        print(f"Brunnhilde Exit Code: {returncode}")
        print(f"--- Brunnhilde-Ausführung beendet ---")
        
        try:
            brunnhilde_report_path.mkdir(exist_ok=True)
            tree_output_file = brunnhilde_report_path / "tree.txt"
            
            print(f"\n--- Erstelle 'tree.txt' manuell als Workaround... ---")
            
            tree_command = f'cmd /c tree "{str(source_path)}" /A /F > "{str(tree_output_file)}"'
            
            print(f"Führe Befehl aus: {tree_command}")
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

        if not brunnhilde_report_path.exists():
            print(f"Fehler: Brunnhilde-Berichtsordner nicht gefunden unter {brunnhilde_report_path}.")
            if returncode != 0:
                print(f"Hinweis: Brunnhilde beendete sich mit Exit Code {returncode}. Prüfen Sie die obige Ausgabe auf Fehler.")
            return brunnhilde_metadata

        csv_reports_dir = brunnhilde_report_path / "csv_reports"
        if not csv_reports_dir.exists():
            print(f"Warnung: CSV-Berichtsverzeichnis nicht gefunden unter {csv_reports_dir}.")
        
        formats_csv = csv_reports_dir / "formats.csv"
        if formats_csv.exists():
            with open(formats_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                brunnhilde_metadata['brunhilde_format_summary'] = json.dumps([row for row in reader])

        mimetypes_csv = csv_reports_dir / "mimetypes.csv"
        if mimetypes_csv.exists():
            with open(mimetypes_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                brunnhilde_metadata['brunhilde_mime_type_summary'] = json.dumps([row for row in reader])
        
        warnings_by_file_path = {}
        siegfried_warnings_csv = csv_reports_dir / "siegfried_warnings.csv"
        if siegfried_warnings_csv.exists():
            with open(siegfried_warnings_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    file_path = row.get('File', '').strip()
                    if file_path:
                        warnings_by_file_path.setdefault(file_path, []).append(row)
            brunnhilde_metadata['structured_siegfried_warnings'] = warnings_by_file_path

        unidentified_csv = csv_reports_dir / "unidentified.csv"
        if unidentified_csv.exists():
            with open(unidentified_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                unidentified_paths = {row.get('File', '').strip() for row in reader if row.get('File', '').strip()}
            brunnhilde_metadata['structured_unidentified_files'] = list(unidentified_paths)

        virus_scan_log = brunnhilde_report_path / "virus_scan_log.txt"
        if virus_scan_log.exists():
            with open(virus_scan_log, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()
                infected_match = re.search(r"Infected files: (\d+)", log_content)
                if infected_match:
                    infected_count = int(infected_match.group(1))
                    brunnhilde_metadata['brunhilde_clamav_infected_files'] = str(infected_count)
                    if infected_count > 0:
                        virus_details = re.findall(r"^(.*?): (.*?) FOUND$", log_content, re.MULTILINE)
                        brunnhilde_metadata['brunhilde_clamav_virus_details'] = json.dumps(virus_details)
                else:
                    brunnhilde_metadata['brunhilde_clamav_status'] = "Log gefunden, aber Infektionsstatus unklar."
        else:
            brunnhilde_metadata['brunhilde_clamav_status'] = "Kein virus_scan_log.txt gefunden."

    except Exception as e:
        print(f"Fehler beim Ausführen oder Parsen von Brunnhilde: {e}")
    finally:
        if is_temp_dir and brunnhilde_output_base_dir.exists():
            shutil.rmtree(brunnhilde_output_base_dir)
            
    return brunnhilde_metadata


# --- Haupt-Ausführungsblock ---
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

    validated_paths = setup_and_validate_analysis_paths(ac_number_input, disk_archive_id_input, SIEGFRIED_DIR, CLAMAV_DIR)

    if validated_paths:
        BASE_DIR = validated_paths["base_dir"]
        BRUNNHILDE_OUTPUT_DIR = validated_paths["brunnhilde_output_dir"]
        OUTPUT_JSON = validated_paths["output_json"]
        
        print("\nSkript wird mit folgenden Pfaden ausgeführt:")
        print(f"- Basis-Verzeichnis: {BASE_DIR}")
        print(f"- Brunnhilde-Ausgabe: {BRUNNHILDE_OUTPUT_DIR}")
        print(f"- Temporäre JSON-Ausgabe: {OUTPUT_JSON}")
        if SIEGFRIED_DIR: print(f"- Siegfried-Verzeichnis: {SIEGFRIED_DIR}")
        if CLAMAV_DIR: print(f"- ClamAV-Verzeichnis: {CLAMAV_DIR}")

        analysis_path = Path(BASE_DIR)
        if not analysis_path.is_dir():
            print(f"FEHLER: Das angegebene Verzeichnis '{analysis_path}' existiert nicht.")
            sys.exit(1)

        analysis_results = extract_brunnhilde_info(analysis_path, BRUNNHILDE_OUTPUT_DIR)
        
        if analysis_results:
            print("\n--- Zusammenfassung der Brunnhilde-Analyse ---")
            
            try:
                with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                    json.dump(analysis_results, f, indent=2, ensure_ascii=False)
                print(f"\nErgebnisse erfolgreich nach {OUTPUT_JSON} geschrieben.")
            except Exception as e:
                print(f"\nFehler beim Schreiben der JSON-Datei: {e}")

            print("\n--- Finalisiere Berichte durch Umbenennen und Verschieben... ---")
            
            source_json = OUTPUT_JSON
            dest_json = validated_paths["final_json_path"]
            
            identifier = Path(BASE_DIR).name.replace('.', '_') + "_collection_report"
            source_tree = BRUNNHILDE_OUTPUT_DIR / identifier / "tree.txt"
            dest_tree = validated_paths["final_tree_path"]

            try:
                if source_json.exists():
                    shutil.move(str(source_json), str(dest_json))
                    print(f"Erfolgreich verschoben: {source_json.name} -> {dest_json.name}")
                else:
                    print(f"FEHLER: Quelldatei {source_json} für Verschieben nicht gefunden.")
            except Exception as e:
                print(f"FEHLER beim Verschieben der JSON-Datei: {e}")

            try:
                if source_tree.exists():
                    shutil.move(str(source_tree), str(dest_tree))
                    print(f"Erfolgreich verschoben: tree.txt -> {dest_tree.name}")
                else:
                    print(f"FEHLER: Quelldatei {source_tree} für Verschieben nicht gefunden.")
            except Exception as e:
                print(f"FEHLER beim Verschieben der tree.txt: {e}")
                
        else:
            print("\nKonnte keine Metadaten aus den Brunnhilde-Berichten extrahieren.")

        # --- ANFANG: HINZUGEFÜGTER CODE-BLOCK ---
        # Der Zielordner ist das übergeordnete Verzeichnis des 'base_dir'
        destination_folder = validated_paths["base_dir"].parent
        
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