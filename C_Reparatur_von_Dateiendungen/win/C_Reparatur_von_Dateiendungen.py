# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import subprocess
import json
import sys
import mimetypes
from pathlib import Path
import shutil
from datetime import datetime
import zipfile
import csv

# ==============================================================================
# 🔧 KONFIGURATION
# ==============================================================================

def setup_and_validate_repair_paths(ac_number, disk_archive_id):
    project_base_path = Path.home() / "Documents/data" / ac_number / disk_archive_id
    transfer_folder = project_base_path / f"3_{disk_archive_id}_for-transfer"
    
    # Pfad zu Siegfried fest hinterlegen
    SIEGFRIED_EXE = r"C:\Program Files\Siegfried\sf.exe"
    
    paths = {
        "analysis_folder": transfer_folder / "files",
        "log_file": transfer_folder / f"3_{disk_archive_id}_for-transfer_repair-file-extension.log",
        "ffprobe_exec": "ffprobe.exe",
        "siegfried_exec": SIEGFRIED_EXE
    }
    
    if not paths["analysis_folder"].is_dir(): 
        print(f"\033[91mFehler: Analyse-Ordner nicht gefunden: {paths['analysis_folder']}\033[0m")
        return None
    if not paths["log_file"].parent.is_dir(): 
        print(f"\033[91mFehler: Log-Ordner nicht gefunden: {paths['log_file'].parent}\033[0m")
        return None
    
    # Siegfried-Pfad Prüfung
    if not Path(paths["siegfried_exec"]).exists(): 
        print(f"\033[91mFehler: Siegfried nicht gefunden unter: {paths['siegfried_exec']}\033[0m")
        return None
    
    if not shutil.which(paths["ffprobe_exec"]): 
        print(f"\033[91mFehler: '{paths['ffprobe_exec']}' nicht im PATH gefunden.\033[0m")
        return None
    
    print("\033[92mAlle Pfade und Programme wurden erfolgreich gefunden und validiert.\033[0m")
    return paths

# PRONOM-Mapping
pronom_to_ext_map = {
    "fmt/189": ".pdf", "fmt/190": ".pdf", "fmt/191": ".pdf", "fmt/276": ".pdf",
    "fmt/40": ".doc", "x-fmt/65": ".doc", "fmt/612": ".docx",
    "fmt/214": ".xls", "fmt/595": ".xlsx",
    "fmt/291": ".odt", "fmt/290": ".ods", "fmt/292": ".odp",
    "fmt/353": ".tif", "fmt/354": ".tif",
    "fmt/14": ".jpg", "fmt/15": ".jpg", "fmt/11": ".png",
    "fmt/846": ".cwk", "fmt/1439": ".pages", "fmt/397": ".mus",
    "fmt/279": ".flac", "fmt/569": ".mkv", "fmt/203": ".ogg", "fmt/384": ".mxf",
    "x-fmt/191": ".sam", "x-fmt/18": ".csv", "fmt/280": ".tex",
    "fmt/596": ".m4a",
    "fmt/838": ".dbx"
}

format_name_to_ext_map = {"AppleWorks Word Processing": ".cwk", "Ami Pro": ".sam"}

# Windows-Systemdateien, die keinen archivischen Wert haben und gelöscht werden können
SYSTEM_JUNK_FILES = ["IndexerVolumeGuid"]

DRY_RUN = False

# ==============================================================================
# --- Skript-Logik ---
# ==============================================================================

ffprobe_path_executable = ""
LOG_FILE_HANDLE = None
mimetypes.add_type('message/rfc822', '.eml', strict=False); mimetypes.init()

def log(message):
    print(message)
    if LOG_FILE_HANDLE: LOG_FILE_HANDLE.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

def run_command_with_json_output(command):
    try:
        process = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        return json.loads(process.stdout) if process.returncode == 0 and process.stdout else None
    except: return None

def has_video_stream(filepath):
    if not ffprobe_path_executable: return None
    command = [ffprobe_path_executable, "-v", "error", "-show_entries", "stream=codec_type", "-select_streams", "v", "-of", "json", str(filepath)]
    return bool(run_command_with_json_output(command))

def determine_extension_siegfried(filepath, match):
    pronom_id, mime_type, format_name = match.get("id"), match.get("mime"), match.get("format")
    if pronom_id in pronom_to_ext_map: return pronom_to_ext_map[pronom_id], "PRONOM ID (Manuell)"
    if pronom_id == 'fmt/199': return (".mp4", "MPEG-4 (mit Video)") if has_video_stream(filepath) else (".m4a", "MPEG-4 (nur Audio)")
    
    if mime_type and mime_type not in ['text/plain', 'application/octet-stream']:
        ext = mimetypes.guess_extension(mime_type)
        if ext: return ext, "MIME-Typ (Automatisch)"
            
    if format_name in format_name_to_ext_map: return format_name_to_ext_map[format_name], "Formatname (Manuell)"
    return None, None

def is_likely_text_file(filepath, threshold=0.9):
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(1024)
            if not chunk: return True
            text_characters = bytes(range(32, 127)) + b'\n\r\t'
            text_count = sum(1 for byte in chunk if byte in text_characters)
            return (text_count / len(chunk)) >= threshold
    except: return False

def determine_text_table_extension(filepath):
    try:
        with open(filepath, 'r', encoding='latin-1') as f:
            if f.readline(10).strip().startswith("ID;"): return '.slk', 'Fallback (SYLK-Signatur)'
    except: pass
    
    delimiters = [';', ',', '\t', '|']
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [line.strip() for line in f.readlines(4096) if line.strip()]
            if len(lines) >= 3:
                for d in delimiters:
                    counts = [line.count(d) for line in lines]
                    non_zero = [c for c in counts if c > 0]
                    if non_zero and non_zero.count(max(set(non_zero), key=non_zero.count)) >= 3:
                        return '.csv', f'Fallback (CSV-Struktur "{d}")'
    except: pass
    return None, None

def determine_extension_fallback(filepath):
    if zipfile.is_zipfile(filepath):
        try:
            with zipfile.ZipFile(filepath, 'r') as zf:
                if 'mimetype' in zf.namelist():
                    m = zf.read('mimetype').decode('utf-8').strip()
                    if 'opendocument.text' in m: return '.odt', 'Fallback (ZIP-Mimetype)'
                    if 'opendocument.spreadsheet' in m: return '.ods', 'Fallback (ZIP-Mimetype)'
        except: pass

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            header = f.read(2048)
            if '<office:document-content' in header: return '.odt', 'Fallback (Flat XML)'
            if '<office:document-spreadsheet' in header: return '.ods', 'Fallback (Flat XML)'
    except: pass
    
    ext, source = determine_text_table_extension(filepath)
    if ext: return ext, source
    if is_likely_text_file(filepath): return '.txt', 'Fallback (Plain Text)'
    return None, None

def main():
    # WICHTIG: global MUSS die erste Zeile in der Funktion sein
    global ffprobe_path_executable, LOG_FILE_HANDLE
    
    try:
        ac_in, id_in = sys.argv[1], sys.argv[2]
    except IndexError:
        ac_in, id_in = input("AC: "), input("ID: ")

    # --- AUTOMATISCHER TRANSFER VON STUFE 2 NACH STUFE 3 ---
    project_root = Path.home() / "Documents/data" / ac_in / id_in
    source_stage2 = project_root / f"2_{id_in}_extracted-files" / "files"
    target_stage3 = project_root / f"3_{id_in}_for-transfer" / "files"

    if not target_stage3.exists():
        if source_stage2.exists():
            print(f"\033[94mVorbereitung: Kopiere Dateien von Stufe 2 nach Stufe 3...\033[0m")
            try:
                shutil.copytree(source_stage2, target_stage3)
                print(f"\033[92m[OK] Dateien erfolgreich nach Stufe 3 kopiert.\033[0m")
            except Exception as e:
                print(f"\033[91m[FEHLER] Kopieren fehlgeschlagen: {e}\033[0m")
                sys.exit(1)
        else:
            print(f"\033[91mFehler: Quell-Daten in Stufe 2 nicht gefunden ({source_stage2})\033[0m")
            sys.exit(1)
    
    # Validierung der Pfade (Siegfried, FFprobe etc.)
    config = setup_and_validate_repair_paths(ac_in, id_in)
    if not config: sys.exit(1)
    
    LOG_FILE_HANDLE = open(config["log_file"], 'w', encoding='utf-8')
    ffprobe_path_executable = shutil.which(config["ffprobe_exec"])

    log(f"Skript gestartet am {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" + "-" * 40)
    if DRY_RUN: log("🚨 SIMULATIONSMODUS AKTIV.")

    path_obj = Path(config["analysis_folder"])
    files_to_check = [p for p in path_obj.rglob('*') if p.is_file() and not p.name.startswith('.') and not p.suffix]
    
    if not files_to_check:
        log("\n✅ Keine Dateien ohne Dateiendung gefunden.")
    else:
        log(f"{len(files_to_check)} Datei(en) ohne Endung gefunden...\n" + "-" * 40)
        renamed_count = 0; unidentified_count = 0; deleted_count = 0

        for filepath in files_to_check:
            # --- NEU: System-Müll erkennen und löschen ---
            if filepath.name in SYSTEM_JUNK_FILES:
                prefix = "[SIMULATION]" if DRY_RUN else "🗑️ Gelöscht"
                log(f"{prefix}: '{filepath.name}' (Windows-Systemdatei ohne archivischen Wert)")
                if not DRY_RUN:
                    try: 
                        filepath.unlink()
                        deleted_count += 1
                    except OSError as e: 
                        log(f"    ❌ FEHLER beim Löschen: {e}")
                else:
                    deleted_count += 1
                continue
            
            # Nutzt den festen Siegfried-Pfad aus der config
            siegfried_result = run_command_with_json_output([config["siegfried_exec"], "-json", str(filepath)])
            new_ext, source = None, None
            
            if siegfried_result and siegfried_result.get("files") and siegfried_result["files"][0].get("matches"):
                new_ext, source = determine_extension_siegfried(filepath, siegfried_result["files"][0]["matches"][0])

            if not new_ext:
                new_ext, source = determine_extension_fallback(filepath)
            
            if new_ext:
                new_path = filepath.with_suffix(new_ext)
                counter = 1
                while new_path.exists():
                    new_path = filepath.parent / f"{filepath.stem}_{counter}{new_ext}"
                    counter += 1
                
                prefix = "[SIMULATION]" if DRY_RUN else "✅ Umbenannt"
                log(f"{prefix}: '{filepath.name}' -> '{new_path.name}' [via {source}]")
                if not DRY_RUN:
                    try: filepath.rename(new_path); renamed_count += 1
                    except OSError as e: log(f"    ❌ FEHLER: {e}")
                else: renamed_count += 1
            else:
                fmt_name, p_id = "Unbekannt", "UNKNOWN"
                if siegfried_result and siegfried_result.get("files") and siegfried_result["files"][0].get("matches"):
                    m = siegfried_result["files"][0]["matches"][0]
                    fmt_name, p_id = m.get("format", fmt_name), m.get("id", p_id)
                
                log(f"❓ Nicht zugeordnet: '{filepath.name}' (Siegfried: {fmt_name}, PRONOM: {p_id})")
                unidentified_count += 1

        log("-" * 40 + f"\nAnalyse abgeschlossen.")
        log(f"Dateien {'simuliert' if DRY_RUN else 'umbenannt'}: {renamed_count}")
        log(f"System-Müll {'simuliert' if DRY_RUN else 'gelöscht'}: {deleted_count}")
        log(f"Nicht zugeordnet: {unidentified_count}")

    LOG_FILE_HANDLE.close()
    
    open_q = input("\nAnalyse beendet. Zielordner öffnen? (j/n): ").lower()
    if open_q == 'j': os.startfile(config["analysis_folder"])

if __name__ == "__main__":
    main()