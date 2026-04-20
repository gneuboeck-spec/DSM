# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import subprocess
from datetime import datetime
import shutil
import sys
from pathlib import Path

# ==============================================================================
# 🔧 KONFIGURATION
# ==============================================================================

# --- 1. System-Pfade (manuell anpassen, falls nötig) ---
LIBREOFFICE_PATH = "C:/Program Files/LibreOffice/program/soffice.exe"

# --- 2. Konvertierungs-Map für Dateitypen ---
CONVERSION_MAP = {
    # Textdokumente
    ".doc": ("odt", "writer_pdf_Export"), ".docx": ("odt", "writer_pdf_Export"),
    ".dot": ("odt", "writer_pdf_Export"), ".rtf": ("odt", "writer_pdf_Export"),
    ".odt": ("odt", "writer_pdf_Export"), ".ott": ("odt", "writer_pdf_Export"),
    ".sxw": ("odt", "writer_pdf_Export"), ".stw": ("odt", "writer_pdf_Export"),
    ".fodt": ("odt", "writer_pdf_Export"), ".uot": ("odt", "writer_pdf_Export"),
    ".wpd": ("odt", "writer_pdf_Export"), ".wps": ("odt", "writer_pdf_Export"),
    ".abw": ("odt", "writer_pdf_Export"), ".sdw": ("odt", "writer_pdf_Export"),
    ".wri": ("odt", "writer_pdf_Export"), ".html": ("odt", "writer_pdf_Export"),
    ".htm": ("odt", "writer_pdf_Export"), ".txt": ("odt", "writer_pdf_Export"),
    ".pages": ("odt", "writer_pdf_Export"), ".wbk": ("odt", "writer_pdf_Export"),
    ".cwk": ("odt", "writer_pdf_Export"), ".cws": ("odt", "writer_pdf_Export"),
    # Tabellen
    ".xls": ("ods", "calc_pdf_Export"), ".xlsx": ("ods", "calc_pdf_Export"),
    ".xlw": ("ods", "calc_pdf_Export"), ".xlt": ("ods", "calc_pdf_Export"),
    ".ods": ("ods", "calc_pdf_Export"), ".ots": ("ods", "calc_pdf_Export"),
    ".sxc": ("ods", "calc_pdf_Export"), ".stc": ("ods", "calc_pdf_Export"),
    ".fods": ("ods", "calc_pdf_Export"), ".uos": ("ods", "calc_pdf_Export"),
    # Präsentationen
    ".ppt": ("odp", "impress_pdf_Export"), ".pptx": ("odp", "impress_pdf_Export"),
    ".pps": ("odp", "impress_pdf_Export"), ".pot": ("odp", "impress_pdf_Export"),
    ".odp": ("odp", "impress_pdf_Export"), ".otp": ("odp", "impress_pdf_Export"),
    ".sxi": ("odp", "impress_pdf_Export"), ".sti": ("odp", "impress_pdf_Export"),
    ".fodd": ("odp", "impress_pdf_Export"), ".uop": ("odp", "impress_pdf_Export"),
    ".key": ("odp", "impress_pdf_Export"),
    # PDF zu PDF/A
    ".pdf": ("pdf", "draw_pdf_Export")
}

# --- 3. Funktion zur dynamischen Erstellung und Validierung der Projekt-Pfade ---
def setup_and_validate_paths(ac_number, disk_archive_id, libreoffice_path):
    project_base_path = Path.home() / "Documents/data" / ac_number / disk_archive_id
    transfer_folder = project_base_path / f"3_{disk_archive_id}_for-transfer"

    paths = {
        "input_folder": transfer_folder / "files",
        "log_path": transfer_folder / f"3_{disk_archive_id}_for-transfer_text-conversion.log",
        "libreoffice_exec": Path(libreoffice_path)
    }

    if not paths["libreoffice_exec"].is_file():
        print(f"\033[91mFehler: LibreOffice wurde nicht gefunden unter:\n{paths['libreoffice_exec']}\033[0m")
        return None
        
    if not paths["input_folder"].is_dir():
        print(f"\033[91mFehler: Der Eingabe-Ordner wurde nicht gefunden:\n{paths['input_folder']}\033[0m")
        return None
        
    if not paths["log_path"].parent.is_dir():
        print(f"\033[91mFehler: Der Ordner für die Log-Datei existiert nicht:\n{paths['log_path'].parent}\033[0m")
        return None

    print("\033[92mAlle Pfade und Programme wurden erfolgreich gefunden und validiert.\033[0m")
    return paths

# ==============================================================================
# --- HILFSFUNKTIONEN ---
# ==============================================================================
LOG_FILE_PATH = None

def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
    print(msg)
    if LOG_FILE_PATH:
        try:
            with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
                f.write(timestamp + msg.strip() + "\n")
        except Exception as e:
            print(f"\033[91mKRITISCHER FEHLER: Konnte nicht in Log-Datei schreiben: {e}\033[0m")

def print_progress(current, total, filename):
    bar_length = 30
    filled_length = int(bar_length * current // total)
    bar = "#" * filled_length + "." * (bar_length - filled_length)
    percent = (current / total) * 100
    progress_line = f"\r[{bar}] {percent:5.1f}% ({current}/{total}) {filename[:50]:<50}"
    sys.stdout.write(progress_line)
    sys.stdout.flush()

# ==============================================================================
# --- HAUPT-AUSFÜHRUNGSBLOCK ---
# ==============================================================================
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

    validated_paths = setup_and_validate_paths(ac_number_input, disk_archive_id_input, LIBREOFFICE_PATH)

    if validated_paths:
        input_folder = validated_paths["input_folder"]
        LOG_FILE_PATH = validated_paths["log_path"]
        libreoffice_path = str(validated_paths["libreoffice_exec"])

        if os.path.exists(LOG_FILE_PATH):
            os.remove(LOG_FILE_PATH)

        print("\nSkript wird mit folgenden Pfaden ausgeführt:")
        print(f"- Eingabe-Ordner: {input_folder}")
        print(f"- Log-Datei: {LOG_FILE_PATH}")
        print(f"- LibreOffice: {libreoffice_path}\n")

        log("Starte universellen Office-Konverter. Suche nach Dateien...")

        all_files = []
        valid_source_extensions = set(CONVERSION_MAP.keys())
        
        # ***** ENDGÜLTIGE, ROBUSTE LOGIK ZUR DATEISUCHE *****
        for root, _, files in os.walk(input_folder):
            for filename in files:
                if filename.startswith('.') or filename.startswith('~'):
                    continue

                name_part, ext_part = os.path.splitext(filename)
                current_ext = ext_part.lower()

                if current_ext not in valid_source_extensions:
                    continue

                # REGEL 1: Wenn es eine PDF ist, ignoriere sie, wenn sie bereits ein Derivat ist.
                if current_ext == '.pdf':
                    if '.' in name_part:
                        continue
                
                # REGEL 2: Für alle anderen Formate, ignoriere sie, wenn sie bereits ein Derivat sind.
                else:
                    is_derivative = False
                    for source_ext in valid_source_extensions:
                        if name_part.lower().endswith(source_ext):
                            is_derivative = True
                            break
                    if is_derivative:
                        continue
                
                all_files.append((root, filename))

        total_files = len(all_files)
        log(f"{total_files} neue Dateien gefunden, die den Kriterien entsprechen.")

        if total_files == 0:
            log("Keine neuen Dateien zum Konvertieren gefunden. Skript wird beendet.")
        else:
            for i, (root, filename) in enumerate(all_files):
                name, ext = os.path.splitext(filename)
                ext = ext.lower()

                print_progress(i + 1, total_files, filename)

                input_path = os.path.join(root, filename)
                target_odf_ext, pdf_export_filter = CONVERSION_MAP[ext]
                
                odf_filename = f"{name}{ext}.{target_odf_ext}"
                odf_path_target = os.path.join(root, odf_filename)
                pdf_filename = f"{name}{ext}.pdf"
                pdf_path = os.path.join(root, pdf_filename)
                
                if os.path.exists(odf_path_target): os.remove(odf_path_target)
                if os.path.exists(pdf_path): os.remove(pdf_path)

                is_original_pdf = (ext == ".pdf")

                if is_original_pdf:
                    source_for_pdf_export = input_path
                else:
                    cmd_convert = [libreoffice_path, "--headless", "--convert-to", target_odf_ext, "--outdir", root, input_path]
                    subprocess.run(cmd_convert, capture_output=True, text=True)
                    
                    real_odf_name_by_lo = f"{name}.{target_odf_ext}"
                    real_odf_path_by_lo = os.path.join(root, real_odf_name_by_lo)

                    if os.path.exists(real_odf_path_by_lo):
                        os.replace(real_odf_path_by_lo, odf_path_target)
                        source_for_pdf_export = odf_path_target
                    else:
                        log(f"\n[FEHLER] Konvertierung zu ODF fehlgeschlagen für: {filename}")
                        continue

                pdfa_filter_string = f"pdf:{pdf_export_filter}:SelectPdfVersion=2"
                
                temp_output_dir = os.path.join(root, "temp_pdf_conversion")
                os.makedirs(temp_output_dir, exist_ok=True)

                cmd_pdf = [libreoffice_path, "--headless", "--convert-to", pdfa_filter_string, "--outdir", temp_output_dir, source_for_pdf_export]
                subprocess.run(cmd_pdf, capture_output=True, text=True)

                base_name_for_pdf = os.path.splitext(os.path.basename(source_for_pdf_export))[0]
                real_pdf_path_by_lo = os.path.join(temp_output_dir, f"{base_name_for_pdf}.pdf")

                if os.path.exists(real_pdf_path_by_lo):
                    shutil.move(real_pdf_path_by_lo, pdf_path)
                    log(f"\n[OK] Konvertierung erfolgreich: {filename} -> {pdf_filename}")
                else:
                    log(f"\n[FEHLER] PDF/A-Export fehlgeschlagen für: {filename}")
                
                if os.path.exists(temp_output_dir):
                    shutil.rmtree(temp_output_dir)
            
            print()
            log("Alle Konvertierungen abgeschlossen.")

        # --- ANFANG: HINZUGEFÜGTER CODE-BLOCK (MIT KORREKTUR) ---
        destination_folder = validated_paths["input_folder"].parent
        
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