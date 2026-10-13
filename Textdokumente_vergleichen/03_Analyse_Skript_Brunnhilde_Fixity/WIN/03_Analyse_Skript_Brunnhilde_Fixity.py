# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import sys
import json
import subprocess
import re
import shutil
import csv
import hashlib
import ctypes
import tempfile
from pathlib import Path

# GUI-Importe für die Dialogfenster
import tkinter as tk
from tkinter import filedialog, messagebox

# ==============================================================================
# 🔧 DYNAMISCHE PFADERMITTLUNG FÜR EXTERNE TOOLS
# ==============================================================================

def find_executable_dir(tool_name, fallback_path):
    """Findet das Verzeichnis eines Tools im System-PATH oder nutzt den Fallback-Pfad."""
    # 1. Versuche: Tool im PATH finden (z.B. wenn über Installer zum PATH hinzugefügt)
    exe_path = shutil.which(tool_name)
    if exe_path:
        return str(Path(exe_path).parent)
    
    # 2. Fallback: Hardcodierter Pfad (für den alten Rechner)
    if Path(fallback_path).exists():
        return fallback_path
    
    # 3. Wenn nichts gefunden wird, gib den Fallback zurück (Skript wirft dann Fehlermeldung)
    return fallback_path

# ==============================================================================
# 🔧 KONFIGURATION (Dynamisch ermittelt)
# ==============================================================================

SIEGFRIED_DIR = find_executable_dir("sf", r"C:\Program Files\Siegfried")
CLAMAV_DIR = find_executable_dir("clamscan", r"C:\Program Files\ClamAV")

# --- Hilfsfunktion für SHA256 ---
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

# --- Funktion zur Validierung der gewählten Pfade und Tools ---
def setup_and_validate_paths(source_dir, output_dir, siegfried_dir, clamav_dir):
    """
    Validiert die vom Benutzer ausgewählten Pfade und prüft die Verfügbarkeit der externen Tools.
    """
    source_path = Path(source_dir).resolve()
    output_path = Path(output_dir).resolve()

    if not source_path.is_dir():
        return None, f"Das ausgewählte Quellverzeichnis existiert nicht:\n{source_path}"
    
    if not output_path.is_dir():
        return None, f"Das ausgewählte Zielverzeichnis existiert nicht:\n{output_path}"

    # Prefix für die Dateinamen erstellen (basierend auf dem Quellordner-Namen)
    prefix = source_path.name.replace(' ', '_').replace('.', '_')

    # WICHTIG: Verhindern, dass der temp-Ordner im Quellverzeichnis liegt!
    # Sonst scannt Brunnhilde seine eigenen Ausgabedateien (Error: empty source).
    brunnhilde_output_dir = output_path / f"{prefix}_brunnhilde_temp"
    if output_path == source_path or source_path in output_path.parents:
        safe_output = source_path.parent / f"{source_path.name}_Brunnhilde_Reports"
        safe_output.mkdir(parents=True, exist_ok=True)
        brunnhilde_output_dir = safe_output / f"{prefix}_brunnhilde_temp"
        print(f"\033[93mWarnung: Zielverzeichnis liegt im Quellverzeichnis.\033[0m")
        print(f"Temp-Ordner wurde umgeleitet nach: {brunnhilde_output_dir}")

    paths = {
        "base_dir": source_path,
        "output_dir": output_path,
        "brunnhilde_output_dir": brunnhilde_output_dir,
        "final_brunnhilde_dir": output_path / f"{prefix}_collection_report",
        "siegfried_dir": Path(siegfried_dir) if siegfried_dir else None,
        "clamav_dir": Path(clamav_dir) if clamav_dir else None,
    }

    if paths["siegfried_dir"]:
        siegfried_exe = paths["siegfried_dir"] / "sf.exe"
        if not siegfried_exe.is_file():
            return None, f"'sf.exe' wurde nicht im Siegfried-Verzeichnis gefunden:\n{paths['siegfried_dir']}"
    else:
        print("\033[93mWarnung: Kein Pfad für Siegfried (SIEGFRIED_DIR) angegeben.\033[0m")

    if paths["clamav_dir"]:
        clamav_exe = paths["clamav_dir"] / "clamscan.exe"
        if not clamav_exe.is_file():
            return None, f"'clamscan.exe' wurde nicht im ClamAV-Verzeichnis gefunden:\n{paths['clamav_dir']}"

    print("\033[92mAlle Pfade und Tools wurden erfolgreich validiert.\033[0m")
    return paths, "OK"

# ==============================================================================
# --- Skript-Logik ---
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
    """
    command_str = ' '.join(f'"{arg}"' for arg in command)
    
    process = subprocess.Popen(
        command_str,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=True,
        env=env,
        encoding='utf-8',
        errors='replace'
    )

    full_output = []
    clamav_warning_triggered = False

    for line in iter(process.stdout.readline, ""):
        print(line, end="")
        full_output.append(line)

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
    
    brunnhilde_output_base_dir = Path(brunnhilde_output_dir)
    brunnhilde_output_base_dir.mkdir(parents=True, exist_ok=True)

    identifier = Path(source_path).name.replace(' ', '_').replace('.', '_') + "_collection_report"
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
        
        # --- FIX: Robuste Python-Erkennung gegen Inkscape-Konflikt ---
        python_exe = sys.executable
        
        # Teste, ob das aktuelle Python 'brunnhilde' hat. 
        # Wenn nicht (z.B. bei Inkscape-Python), versuche den Launcher 'py'.
        try:
            subprocess.run([python_exe, "-c", "import brunnhilde"], check=True, capture_output=True)
        except Exception:
            py_launcher = shutil.which("py")
            if py_launcher:
                # Teste explizit Version 3.13 oder Default mit 'py -3'
                test_cmd = [py_launcher, "-3", "-c", "import brunnhilde"]
                result = subprocess.run(test_cmd, capture_output=True)
                if result.returncode == 0:
                    # Wir nutzen 'py -3', weil das garantiert die Hauptinstallation meint
                    python_exe = f"{py_launcher} -3" 
                else:
                    # Nochmal ohne Versionsflag, falls 'py -3' nicht geht
                    test_cmd_default = [py_launcher, "-c", "import brunnhilde"]
                    result_def = subprocess.run(test_cmd_default, capture_output=True)
                    if result_def.returncode == 0:
                        python_exe = py_launcher

        # Baue den Befehl dynamisch zusammen
        if " " in python_exe:
            # Fall: Es ist ein String wie "C:\...\py.exe -3" -> Aufspalten
            cmd_parts = python_exe.split() + ["-m", "brunnhilde", str(source_path), str(brunnhilde_report_path)]
        else:
            # Fall: Es ist ein direkter Pfad zu python.exe
            cmd_parts = [python_exe, "-m", "brunnhilde", str(source_path), str(brunnhilde_report_path)]
            
        brunnhilde_command = cmd_parts
        # ------------------------------------------------------------------
        
        print(f"\n--- Führe Brunnhilde aus für {source_path}... ---")
        print(f"Befehl: {' '.join(brunnhilde_command)}")
        
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
            
    return brunnhilde_metadata

# ==============================================================================
# --- Haupt-Ausführungsblock (ANGEPASST FÜR MENU.PY) ===========================
# ==============================================================================
if __name__ == "__main__":
    # 1. Pfade aus sys.argv holen (werden von der menu.py übergeben)
    if len(sys.argv) < 3:
        print("❌ Fehler: Eingabe- und Ausgabe-Pfad fehlen.")
        print("Verwendung: python 01_Analyse_Skript_Brunnhilde_Fixity.py <eingabe_pfad> <ausgabe_pfad>")
        input("Drücken Sie die Eingabetaste, um dieses Fenster zu schließen...")
        sys.exit(1)

    source_dir = sys.argv[1]
    output_dir = sys.argv[2]

    # 2. GUI initialisieren und Hauptfenster verstecken (nur für den finalen Dialog benötigt)
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    root.update()

    try:
        print(f"\nStarte Brunnhilde-Analyse...")
        print(f"Quellverzeichnis: {source_dir}")
        print(f"Zielverzeichnis:  {output_dir}")
        print("=" * 60)

        # 3. Pfade validieren
        validated_paths, msg = setup_and_validate_paths(
            source_dir, output_dir, SIEGFRIED_DIR, CLAMAV_DIR
        )

        if not validated_paths:
            messagebox.showerror("Fehler bei der Validierung", msg)
            input("Drücken Sie die Eingabetaste, um dieses Fenster zu schließen...")
            sys.exit(1)

        # 4. Analyse durchführen
        analysis_path = validated_paths["base_dir"]
        brunnhilde_out_dir = validated_paths["brunnhilde_output_dir"]
        
        print(f"\nStarte Analyse von: {analysis_path}")
        analysis_results = extract_brunnhilde_info(analysis_path, brunnhilde_out_dir)
        
        # Identifier für den Report-Ordner definieren
        prefix = Path(analysis_path).name.replace(' ', '_').replace('.', '_')
        identifier = prefix + "_collection_report"
        report_dir = brunnhilde_out_dir / identifier
        
        # 5. Ergebnisse speichern
        if analysis_results:
            # Sicherstellen, dass der Report-Ordner existiert
            report_dir.mkdir(parents=True, exist_ok=True)
            
            # JSON direkt in den Report-Ordner schreiben
            output_json_path = report_dir / f"{prefix}_brunnhilde-summary.json"
            
            try:
                with open(output_json_path, 'w', encoding='utf-8') as f:
                    json.dump(analysis_results, f, indent=2, ensure_ascii=False)
                print(f"\nErfolgreich gespeichert: {output_json_path}")
            except Exception as e:
                print(f"\nFehler beim Schreiben der JSON-Datei: {e}")
                messagebox.showwarning("Speicherfehler", f"JSON konnte nicht gespeichert werden:\n{e}")

        # 6. Kompletten Brunnhilde-Berichtsordner in den Zielordner verschieben
        source_brunnhilde_dir = report_dir
        dest_brunnhilde_dir = validated_paths["final_brunnhilde_dir"]
        
        try:
            if source_brunnhilde_dir.exists():
                if dest_brunnhilde_dir.exists():
                    shutil.rmtree(dest_brunnhilde_dir)
                shutil.move(str(source_brunnhilde_dir), str(dest_brunnhilde_dir))
                print(f"Brunnhilde-Berichtsordner erfolgreich verschoben nach: {dest_brunnhilde_dir}")
            else:
                print("Kein Brunnhilde-Berichtsordner zum Verschieben gefunden.")
        except Exception as e:
            print(f"FEHLER beim Verschieben des Brunnhilde-Berichtsordners: {e}")

        # 7. Aufräumen (Temp-Ordner und ggf. den leeren übergeordneten Reports-Ordner löschen)
        try:
            temp_brunnhilde_dir = validated_paths["brunnhilde_output_dir"]
            if temp_brunnhilde_dir.exists():
                shutil.rmtree(temp_brunnhilde_dir)
                
            # NEU: Prüfen, ob der übergeordnete Ordner (z.B. kdb_Brunnhilde_Reports) jetzt leer ist
            parent_dir = temp_brunnhilde_dir.parent
            if parent_dir.exists() and not any(parent_dir.iterdir()):
                parent_dir.rmdir()  # rmdir löscht den Ordner nur, wenn er komplett leer ist
                print(f"Leerer übergeordneter Ordner bereinigt: {parent_dir}")
        except Exception as e:
            pass  # Sicher ist sicher, falls Berechtigungen fehlen

        # 8. Abschluss-Dialog
        print("\nAnalyse erfolgreich abgeschlossen!")
        if messagebox.askyesno("Analyse abgeschlossen", f"Die Analyse ist fertig.\n\nMöchten Sie den Zielordner öffnen?\n{output_dir}"):
            os.startfile(output_dir)

    except Exception as e:
        messagebox.showerror("Unerwarteter Fehler", f"Ein Fehler ist aufgetreten:\n{str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        # 9. Fenster offen halten für Doppelklick-Start
        print("\n" + "="*50)
        input("Drücken Sie die Eingabetaste, um dieses Fenster zu schließen...")