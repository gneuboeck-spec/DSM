# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import subprocess
from datetime import datetime
import shutil
import sys

# --- KONFIGURATION ---
libreoffice_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
input_folder = "/Users/gregorneuboeck/Desktop/Texdateien_konvertieren"
log_file_path = os.path.join(input_folder, "konvertierungslog.txt")

# Erweiterte Konvertierungs-Map
conversion_map = {
    # --- Textdokumente (Ziel: ODT) ---
    ".doc": ("odt", "writer_pdf_Export"), ".docx": ("odt", "writer_pdf_Export"),
    ".dot": ("odt", "writer_pdf_Export"), ".rtf": ("odt", "writer_pdf_Export"),
    ".odt": ("odt", "writer_pdf_Export"), ".ott": ("odt", "writer_pdf_Export"),
    ".sxw": ("odt", "writer_pdf_Export"), ".stw": ("odt", "writer_pdf_Export"),
    ".fodt": ("odt", "writer_pdf_Export"), ".uot": ("odt", "writer_pdf_Export"),
    ".wpd": ("odt", "writer_pdf_Export"), ".wps": ("odt", "writer_pdf_Export"),
    ".abw": ("odt", "writer_pdf_Export"), ".sdw": ("odt", "writer_pdf_Export"),
    ".wri": ("odt", "writer_pdf_Export"), ".html": ("odt", "writer_pdf_Export"),
    ".htm": ("odt", "writer_pdf_Export"), ".txt": ("odt", "writer_pdf_Export"),
    ".pages": ("odt", "writer_pdf_Export"),

    # --- Tabellenkalkulationen (Ziel: ODS) ---
    ".xls": ("ods", "calc_pdf_Export"), ".xlsx": ("ods", "calc_pdf_Export"),
    ".xlw": ("ods", "calc_pdf_Export"), ".xlt": ("ods", "calc_pdf_Export"),
    ".ods": ("ods", "calc_pdf_Export"), ".ots": ("ods", "calc_pdf_Export"),
    ".sxc": ("ods", "calc_pdf_Export"), ".stc": ("ods", "calc_pdf_Export"),
    ".fods": ("ods", "calc_pdf_Export"), ".uos": ("ods", "calc_pdf_Export"),

    # --- Präsentationen (Ziel: ODP) ---
    ".ppt": ("odp", "impress_pdf_Export"), ".pptx": ("odp", "impress_pdf_Export"),
    ".pps": ("odp", "impress_pdf_Export"), ".pot": ("odp", "impress_pdf_Export"),
    ".odp": ("odp", "impress_pdf_Export"), ".otp": ("odp", "impress_pdf_Export"),
    ".sxi": ("odp", "impress_pdf_Export"), ".sti": ("odp", "impress_pdf_Export"),
    ".fodd": ("odp", "impress_pdf_Export"), ".uop": ("odp", "impress_pdf_Export"),
    ".key": ("odp", "impress_pdf_Export"),
    
    # --- PDF als Quelle (Ziel: PDF/A via Draw-Engine) ---
    ".pdf": ("pdf", "draw_pdf_Export")
}

# --- ENDE DER KONFIGURATION ---

def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
    try:
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(timestamp + msg + "\n")
    except Exception as e:
        print(f"KRITISCHER FEHLER: Konnte nicht in Log-Datei schreiben: {e}")
    print(msg)

def print_progress(current, total, filename):
    bar_length = 30
    filled_length = int(bar_length * current // total)
    bar = "#" * filled_length + "." * (bar_length - filled_length)
    percent = (current / total) * 100
    progress_line = f"\r[{bar}] {percent:5.1f}% ({current}/{total}) {filename[:50]:<50}"
    sys.stdout.write(progress_line)
    sys.stdout.flush()

# --- HAUPTPROGRAMM ---
log("Starte universellen Office-Konverter (inkl. PDF zu PDF/A). Suche nach Dateien...")

all_files = []
valid_source_extensions = set(conversion_map.keys())
odf_target_extensions = {".odt", ".ods", ".odp"}

for root, _, files in os.walk(input_folder):
    for filename in files:
        if filename.startswith('.') or filename.startswith('~'):
            continue
        parts = filename.lower().split('.')
        if len(parts) >= 3:
            original_ext = f".{parts[-2]}"
            derivat_ext = f".{parts[-1]}"
            if original_ext in valid_source_extensions and (derivat_ext in odf_target_extensions or derivat_ext == ".pdf"):
                continue
        
        ext = os.path.splitext(filename)[1].lower()
        if ext in conversion_map:
            all_files.append((root, filename))

total_files = len(all_files)
log(f"{total_files} Dateien gefunden, die den Kriterien entsprechen.")

if total_files == 0:
    log("Keine Dateien zum Konvertieren gefunden. Skript wird beendet.")
    sys.exit()

for i, (root, filename) in enumerate(all_files):
    name, ext = os.path.splitext(filename)
    ext = ext.lower()

    print_progress(i + 1, total_files, filename)

    input_path = os.path.join(root, filename)
    target_odf_ext, pdf_export_filter = conversion_map[ext]
    
    odf_filename = f"{name}{ext}.{target_odf_ext}"
    odf_path_target = os.path.join(root, odf_filename)
    pdf_filename = f"{name}{ext}.pdf"
    pdf_path = os.path.join(root, pdf_filename)
    
    # --- KORRIGIERTE LOGIK HIER ---
    if ext == ".pdf":
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
    else:
        # if os.path.exists(odf_path_target):
        #     os.remove(odf_path_target) #  <<< DIESE ZEILE WURDE AUSKOMMENTIERT
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    # --- AB HIER BEGINNT DIE NEUE, ROBUSTERE LOGIK ---
    
    subprocess.call(["pkill", "-f", "soffice"]) # Prozesse vor jedem Schritt beenden
    
    source_for_pdf_export = ""
    conversion_successful = True
    is_original_odf_or_pdf = ext in {".odt", ".ods", ".odp", ".pdf"}

    if is_original_odf_or_pdf:
        log(f"\nDatei ist bereits ein modernes ODF/PDF-Format: {filename}")
        source_for_pdf_export = input_path
    else:
        cmd_convert = [libreoffice_path, "--headless", "--convert-to", target_odf_ext, "--outdir", root, input_path]
        log(f"\nKonvertiere: {filename} → {odf_filename}")
        result = subprocess.run(cmd_convert, capture_output=True)
        
        real_odf_name_by_lo = f"{name}.{target_odf_ext}"
        real_odf_path_by_lo = os.path.join(root, real_odf_name_by_lo)

        if os.path.exists(real_odf_path_by_lo):
            os.replace(real_odf_path_by_lo, odf_path_target)
            source_for_pdf_export = odf_path_target
        else:
            log(f"[FEHLER] Konvertierung zu ODF fehlgeschlagen für: {filename}")
            conversion_successful = False

    if conversion_successful:
        pdfa_filter_string = f"pdf:{pdf_export_filter}:SelectPdfVersion=2"
        
        if ext == ".pdf":
            temp_output_dir = os.path.join(root, "temp_pdf_conversion")
            os.makedirs(temp_output_dir, exist_ok=True)
            cmd_pdf = [libreoffice_path, "--headless", "--convert-to", pdfa_filter_string, "--outdir", temp_output_dir, source_for_pdf_export]
        else:
            cmd_pdf = [libreoffice_path, "--headless", "--convert-to", pdfa_filter_string, "--outdir", root, source_for_pdf_export]

        log(f"Exportiere PDF/A-2b: {pdf_filename}")
        subprocess.run(cmd_pdf, capture_output=True)

        if ext == ".pdf":
            real_pdf_path_by_lo = os.path.join(temp_output_dir, filename)
        else:
            base_name_for_pdf = os.path.splitext(os.path.basename(source_for_pdf_export))[0]
            real_pdf_path_by_lo = os.path.join(root, f"{base_name_for_pdf}.pdf")

        if os.path.exists(real_pdf_path_by_lo):
            shutil.move(real_pdf_path_by_lo, pdf_path)
            log(f"[OK] PDF/A-2b gespeichert: {pdf_filename}")
        else:
            log(f"[FEHLER] PDF/A-2b Export fehlgeschlagen für: {filename}")
        
        if ext == ".pdf" and os.path.exists(temp_output_dir):
            shutil.rmtree(temp_output_dir)

    # Aufräumen der ODF-Zwischendatei
    # if not is_original_odf_or_pdf and os.path.exists(odf_path_target):
    #     os.remove(odf_path_target) # <<< Diese Zeile war hier und ist jetzt auskommentiert

print()
log("Alle Konvertierungen abgeschlossen.")