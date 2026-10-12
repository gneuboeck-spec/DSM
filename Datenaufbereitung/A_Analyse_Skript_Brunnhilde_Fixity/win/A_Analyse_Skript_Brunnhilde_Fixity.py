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
import hashlib
import ctypes
from pathlib import Path

# ==============================================================================
# 🔧 KONFIGURATION (Dynamische Pfadermittlung für Portabilität)
# ==============================================================================

def find_tool_dir(tool_name, fallback_path):
    """Findet das Verzeichnis eines Tools im System-PATH oder nutzt den Fallback."""
    # 1. Versuche: Tool im PATH finden (z.B. wenn über Installer zum PATH hinzugefügt)
    exe_path = shutil.which(tool_name)
    if exe_path:
        return str(Path(exe_path).parent)
    
    # 2. Fallback: Hardcodierter Pfad (für den alten Rechner, falls nicht im PATH)
    if Path(fallback_path).exists():
        return fallback_path
    
    # 3. Wenn nichts gefunden wird, geben wir den Fallback zurück (das Skript wirft dann eine saubere Fehlermeldung)
    return fallback_path

# Dynamische Zuweisung der Pfade
SIEGFRIED_DIR = find_tool_dir("sf", r"C:\Program Files\Siegfried")
CLAMAV_DIR = find_tool_dir("clamscan", r"C:\Program Files\ClamAV") 

# --- NEU: Hilfsfunktion für SHA256 ---
def calculate_sha256(filepath):
    """Berechnet die SHA-256 Prüfsumme einer Datei."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(8192), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        return f"Error: {str(e)}"


# --- 2. Funktion zur dynamischen Erstellung und Validierung der Projekt-Pfade ---
def setup_and_validate_analysis_paths(ac_number, disk_archive_id, siegfried_dir, clamav_dir, project_base_path_override=None):
    """
    Erstellt und validiert die Projekt-Pfade für die Analyse mit Brunnhilde, Siegfried etc.
    und prüft die Verfügbarkeit der externen Tools.
    """
    # NEU: Wenn ein Pfad aus dem Menü übergeben wurde, nutzen wir diesen.
    # Andernfalls greift der alte Fallback-Pfad.
    if project_base_path_override:
        project_base_path = Path(project_base_path_override)
    else:
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
# --- Skript-Logik (Angepasst für Echtzeit-Überwachung der ClamAV Warnung) ---
# ==============================================================================

def trigger_clamav_admin_update():
    """
    Öffnet ein separates CMD-Fenster mit Administratorrechten und führt
    darin das ClamAV-Update (freshclam.exe) automatisch aus.
    """
    print("\n\033[93m" + "!" * 60)
    print(" HINWEIS: Virendefinitionsdatei ist älter als 7 Tage!")
    print(" Es öffnet sich jetzt ein eigenes Administrator-Fenster,")
    print(" in dem das Update (freshclam.exe) automatisch gestartet wird.")
    print("!" * 60 + "\033[0m\n")

    # Kleine Batch-Datei für das erhöhte Fenster erstellen
    bat_path = Path(tempfile.gettempdir()) / "freshclam_admin_update.bat"
    bat_content = (
        "@echo off\r\n"
        "title ClamAV Update (Administrator)\r\n"
        f'cd /d "{CLAMAV_DIR}"\r\n'
        "echo.\r\n"
        "echo ==================================================\r\n"
        "echo  ClamAV Virendefinitionen werden aktualisiert ...\r\n"
        "echo ==================================================\r\n"
        "echo.\r\n"
        "freshclam.exe\r\n"
        "echo.\r\n"
        "echo Update beendet. Dieses Fenster kann geschlossen werden.\r\n"
        "pause\r\n"
    )
    try:
        bat_path.write_text(bat_content, encoding="utf-8")
    except Exception as e:
        print(f"[FEHLER] Batch-Datei konnte nicht erstellt werden: {e}")
        return False

    # Batch-Datei erhöht starten ("runas" löst die UAC-Abfrage aus)
    ret = ctypes.windll.shell32.ShellExecuteW(
        None,           # Kein Elternfenster
        "runas",        # Administratorrechte anfordern
        str(bat_path),  # Auszuführende Datei
        None,           # Keine Parameter
        None,           # Standard-Arbeitsverzeichnis
        1,              # Fenster normal anzeigen
    )

    if ret > 32:
        print("✅ Administrator-Fenster für das ClamAV-Update wurde geöffnet.")
        print("   Die laufende Analyse läuft mit den bisherigen Definitionen weiter,")
        print("   das Update gilt ab dem nächsten Lauf.")
        return True
    else:
        print(f"⚠️ Administrator-Fenster konnte nicht geöffnet werden (Code {ret}).")
        print("   Mögliche Ursache: UAC-Abfrage abgelehnt oder keine Berechtigung.")
        print("   Update bitte manuell durchführen:")
        print(f'     cd "{CLAMAV_DIR}"')
        print("     freshclam.exe")
        return False

def run_command(command, env=None, monitor_clamav=False):
    """
    Führt einen Shell-Befehl aus und gibt stdout, stderr und den Returncode zurück.
    Wenn monitor_clamav True ist, wird der Output live auf 'older than 7 days' geprüft.
    """
    command_str = ' '.join(f'"{arg}"' for arg in command)
    
    # Wir nutzen Popen für die Echtzeit-Überwachung des Outputs
    process = subprocess.Popen(
        command_str,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, # Leitet stderr zu stdout um
        text=True,
        shell=True,
        env=env,
        encoding='utf-8',
        errors='replace'
    )

    full_output = []
    clamav_warning_triggered = False

    # Liest den Output Zeile für Zeile, während das Programm läuft
    for line in iter(process.stdout.readline, ""):
        print(line, end="") # Zeigt die Zeile im Terminal an (wie vorher)
        full_output.append(line)

        # Prüfe live auf die ClamAV Warnung
        if monitor_clamav and not clamav_warning_triggered:
            if "older than 7 days" in line.lower():
                trigger_clamav_admin_update()
                clamav_warning_triggered = True

    process.stdout.close()
    return_code = process.wait()
    
    return "".join(full_output), "", return_code

def extract_brunnhilde_info(source_path, brunnhilde_output_dir):
    """
    Führt Brunnhilde aus, erstellt manuell die tree.txt und extrahiert Metadaten.
    """
    brunnhilde_metadata = {}

    # --- TEIL: SHA-256 GENERIERUNG ---
    print(f"\n--- Generiere SHA-256 Prüfsummen für alle Dateien... ---")
    sha_list = []
    for root, _, files in os.walk(source_path):
        for name in files:
            filepath = Path(root) / name
            rel_path = filepath.relative_to(source_path)
            print(f" Hashing: {rel_path}")
            sha_list.append({
                "file": str(rel_path),
                "sha256": calculate_sha256(filepath)
            })
    brunnhilde_metadata['file_fixity_sha256'] = sha_list
    
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
        
        # MONITOR_CLAMAV ist hier auf True gesetzt
        stdout, stderr, returncode = run_command(brunnhilde_command, env=env, monitor_clamav=True) 
        
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
        except Exception as e:
            print(f"--- FEHLER beim manuellen Erstellen von 'tree.txt': {e} ---")

        if not brunnhilde_report_path.exists():
            print(f"Fehler: Brunnhilde-Berichtsordner nicht gefunden unter {brunnhilde_report_path}.")
            return brunnhilde_metadata

        csv_reports_dir = brunnhilde_report_path / "csv_reports"
        
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
                    brunnhilde_metadata['brunhilde_clamav_status'] = "Log gefunden."
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
    try:
        ac_number_input = sys.argv[1]
        disk_archive_id_input = sys.argv[2]
        
        # NEU: Datenpfad aus menu.py übernehmen (sys.argv[3] oder Umgebungsvariable DATA_PATH)
        if len(sys.argv) >= 4:
            data_path_input = Path(sys.argv[3])
        else:
            data_path_input = Path(os.environ.get("DATA_PATH", Path.home() / "Documents/data" / ac_number_input / disk_archive_id_input))
            
    except IndexError:
        print("FEHLER: AC-Nummer und Datenträger-ID wurden nicht übergeben.")
        sys.exit(1)

    validated_paths = setup_and_validate_analysis_paths(
        ac_number_input, 
        disk_archive_id_input, 
        SIEGFRIED_DIR, 
        CLAMAV_DIR,
        project_base_path_override=data_path_input
    )

    if validated_paths:
        BASE_DIR = validated_paths["base_dir"]
        BRUNNHILDE_OUTPUT_DIR = validated_paths["brunnhilde_output_dir"]
        OUTPUT_JSON = validated_paths["output_json"]
        
        analysis_path = Path(BASE_DIR)
        analysis_results = extract_brunnhilde_info(analysis_path, BRUNNHILDE_OUTPUT_DIR)
        
        if analysis_results:
            try:
                with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                    json.dump(analysis_results, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"\nFehler beim Schreiben der JSON-Datei: {e}")

            identifier = Path(BASE_DIR).name.replace('.', '_') + "_collection_report"
            source_tree = BRUNNHILDE_OUTPUT_DIR / identifier / "tree.txt"
            dest_tree = validated_paths["final_tree_path"]

            try:
                if source_tree.exists():
                    shutil.move(str(source_tree), str(dest_tree))
            except Exception as e:
                print(f"FEHLER beim Verschieben der tree.txt: {e}")
                
        destination_folder = validated_paths["base_dir"].parent
        
        print("")
        open_folder = input("Zielordner oeffnen? (j/n): ").lower()
        if open_folder == 'j':
            if sys.platform == "win32":
                os.startfile(destination_folder)
            elif sys.platform == "darwin":
                subprocess.run(["open", destination_folder])
            else:
                subprocess.run(["xdg-open", destination_folder])

    print("\nSkript beendet.")