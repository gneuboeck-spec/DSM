# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
# SPDX-FileCopyrightText: 2025 Google LLC (für Windows-Anpassungen)
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
    paths = {
        "analysis_folder": transfer_folder / "files",
        "log_file": transfer_folder / f"3_{disk_archive_id}_for-transfer_repair-file-extension.log",
        "ffprobe_exec": "ffprobe.exe"
    }
    if not paths["analysis_folder"].is_dir(): print(f"\033[91mFehler: Analyse-Ordner nicht gefunden: {paths['analysis_folder']}\033[0m"); return None
    if not paths["log_file"].parent.is_dir(): print(f"\033[91mFehler: Log-Ordner nicht gefunden: {paths['log_file'].parent}\033[0m"); return None
    if not shutil.which(paths["ffprobe_exec"]): print(f"\033[91mFehler: '{paths['ffprobe_exec']}' nicht im PATH gefunden.\033[0m"); return None
    print("\033[92mAlle Pfade und Programme wurden erfolgreich gefunden und validiert.\033[0m")
    return paths

pronom_to_ext_map = {
    "fmt/846": ".cwk", "x-fmt/65": ".doc", "fmt/1439": ".pages", "fmt/397": ".mus", "x-fmt/23": ".mid", "x-fmt/230": ".mid",
    "fmt/575": ".musicxml", "fmt/896": ".musicxml", "fmt/569": ".mkv", "fmt/279": ".flac", "fmt/1038": ".r3d", "fmt/134": ".ts",
    "fmt/585": ".ts", "fmt/203": ".ogg", "fmt/946": ".opus", "fmt/117": ".flv", "x-fmt/382": ".flv", "fmt/384": ".mxf",
    "fmt/200": ".mxf", "fmt/120": ".psd", "x-fmt/92": ".psd", "fmt/280": ".tex", "fmt/838": ".dbx", "x-fmt/191": ".sam",
    "x-fmt/18": ".csv", "fmt/291": ".odt",
}
format_name_to_ext_map = {"AppleWorks Word Processing": ".cwk"}
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
    except (FileNotFoundError, json.JSONDecodeError, Exception): return None

def has_video_stream(filepath):
    if not ffprobe_path_executable: return None
    command = [ffprobe_path_executable, "-v", "error", "-show_entries", "stream=codec_type", "-select_streams", "v", "-of", "json", str(filepath)]
    return bool(run_command_with_json_output(command))

def determine_extension_siegfried(filepath, match):
    pronom_id, mime_type, format_name = match.get("id"), match.get("mime"), match.get("format")
    if pronom_id in pronom_to_ext_map: return pronom_to_ext_map[pronom_id], "PRONOM ID (Manuell)"
    if pronom_id == 'fmt/199': return (".mp4", "MPEG-4 (mit Video)") if has_video_stream(filepath) else (".m4a", "MPEG-4 (nur Audio)")
    
    if mime_type:
        if mime_type == 'text/plain':
            return None, None

        ext = mimetypes.guess_extension(mime_type)
        if ext:
            return ext, "MIME-Typ (Automatisch)"
            
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
    except Exception:
        return False

def determine_text_table_extension(filepath):
    try:
        with open(filepath, 'r', encoding='latin-1') as f:
            if f.readline(10).strip().startswith("ID;"):
                return '.slk', 'Fallback (SYLK-Signatur)'
    except Exception:
        pass

    determined_encoding = None
    try:
        with open(filepath, 'rb') as f:
            bom = f.read(4)
            if bom.startswith(b'\xff\xfe') or bom.startswith(b'\xfe\xff'): determined_encoding = 'utf-16'
            elif bom.startswith(b'\xef\xbb\xbf'): determined_encoding = 'utf-8-sig'
    except Exception: pass
    
    encodings_to_try = [determined_encoding] if determined_encoding else ['utf-8', 'cp1252', 'latin-1', 'utf-16']
    delimiters = [';', ',', '\t', '|']

    for encoding in filter(None, encodings_to_try):
        try:
            with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
                lines = [line.strip() for line in f.readlines(4096) if line.strip()]
                if len(lines) < 3: continue

                for d in delimiters:
                    counts = [line.count(d) for line in lines]
                    non_zero_counts = [c for c in counts if c > 0]
                    if not non_zero_counts: continue
                    
                    most_common_count = max(set(non_zero_counts), key=non_zero_counts.count)
                    if non_zero_counts.count(most_common_count) >= 3:
                        return '.csv', f'Fallback (CSV-Struktur, Trennzeichen: "{d}")'
        except Exception:
            continue
            
    return None, None

def determine_extension_fallback(filepath):
    if zipfile.is_zipfile(filepath):
        try:
            with zipfile.ZipFile(filepath, 'r') as zf:
                if 'mimetype' in zf.namelist():
                    mimetype_content = zf.read('mimetype').decode('utf-8').strip()
                    if mimetype_content == 'application/vnd.oasis.opendocument.text': return '.odt', 'Fallback (ZIP-Mimetype)'
                    if mimetype_content == 'application/vnd.oasis.opendocument.spreadsheet': return '.ods', 'Fallback (ZIP-Mimetype)'
                    if mimetype_content == 'application/vnd.oasis.opendocument.presentation': return '.odp', 'Fallback (ZIP-Mimetype)'
        except Exception: pass

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            header_content = f.read(2048)
            if '<office:document-content' in header_content: return '.odt', 'Fallback (Flat XML-Tag)'
            if '<office:document-spreadsheet' in header_content: return '.ods', 'Fallback (Flat XML-Tag)'
            if '<office:document-presentation' in header_content: return '.odp', 'Fallback (Flat XML-Tag)'
    except Exception: pass
    
    ext, source = determine_text_table_extension(filepath)
    if ext:
        return ext, source

    if is_likely_text_file(filepath):
        return '.txt', 'Fallback (Inhaltsanalyse: Plain Text)'

    return None, None

def main():
    global ffprobe_path_executable, LOG_FILE_HANDLE
    
    try:
        ac_number_input = sys.argv[1]
        disk_archive_id_input = sys.argv[2]
        print(f"Werte aus der Kommandozeile erhalten: AC={ac_number_input}, ID={disk_archive_id_input}")
    except IndexError:
        print("FEHLER: AC-Nummer und Datenträger-ID wurden nicht übergeben.")
        print("Dieses Skript sollte über die 'start.bat'-Datei und das Menü gestartet werden.")
        print("\nBitte geben Sie die Daten manuell ein:")
        ac_number_input = input("AC-Nummer eingeben: ")
        disk_archive_id_input = input("Datenträger-ID eingeben: ")
    
    config_paths = setup_and_validate_repair_paths(ac_number_input, disk_archive_id_input)
    if not config_paths: sys.exit(1)
        
    base_path, log_file_path, ffprobe_path_config = config_paths["analysis_folder"], config_paths["log_file"], config_paths["ffprobe_exec"]
    print(f"\nSkript wird mit folgenden Pfaden ausgeführt:\n- Ordner: {base_path}\n- Log: {log_file_path}\n- FFprobe: {ffprobe_path_config}")

    try:
        Path(log_file_path).parent.mkdir(parents=True, exist_ok=True)
        LOG_FILE_HANDLE = open(log_file_path, 'w', encoding='utf-8')
    except IOError as e: print(f"❌ KRITISCHER FEHLER: Log-Datei konnte nicht erstellt werden: {e}"); sys.exit(1)

    try:
        log(f"Skript gestartet am {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" + "-" * 40)
        if DRY_RUN: log("🚨 SIMULATIONSMODUS AKTIV.")
        if not shutil.which("sf"): log("❌ KRITISCHER FEHLER: Siegfried ('sf.exe') nicht gefunden."); sys.exit(1)

        found_ffprobe_path = shutil.which(ffprobe_path_config)
        if found_ffprobe_path:
            ffprobe_path_executable = found_ffprobe_path; log(f"✅ ffprobe gefunden: {ffprobe_path_executable}")
        else:
            log(f"⚠️  WARNUNG: '{ffprobe_path_config}' nicht gefunden.")

        path_obj = Path(base_path)
        log(f"\nAnalysiere: {path_obj}")
        
        files_to_check = [p for p in path_obj.rglob('*') if p.is_file() and not p.name.startswith('.') and '.' not in p.name]
        
        # --- KORREKTE LOGIK ---
        if not files_to_check:
            log("\n✅ Keine Dateien ohne Dateiendung gefunden.")
        else:
            log(f"{len(files_to_check)} Datei(en) ohne Endung gefunden...\n" + "-" * 40)
            renamed_count = 0; unidentified_count = 0

            for filepath in files_to_check:
                siegfried_result = run_command_with_json_output(["sf", "-json", str(filepath)])
                new_ext, source = None, None
                
                if siegfried_result and siegfried_result.get("files", [{}])[0].get("matches"):
                    new_ext, source = determine_extension_siegfried(filepath, siegfried_result["files"][0]["matches"][0])

                if not new_ext:
                    new_ext, source = determine_extension_fallback(filepath)
                
                if new_ext:
                    new_path = filepath.with_suffix(new_ext)
                    prefix = "[SIMULATION]" if DRY_RUN else "✅ Umbenannt"
                    log(f"{prefix}: '{filepath.name}' -> '{new_path.name}' [via {source}]")
                    if not DRY_RUN:
                        try:
                            if new_path.exists(): log(f"    ⚠️  ZIEL EXISTIERT BEREITS: '{new_path.name}'."); continue
                            filepath.rename(new_path); renamed_count += 1
                        except OSError as e: log(f"    ❌ FEHLER: {e}")
                    else: renamed_count += 1
                else:
                    format_name, pronom_id = "Unbekannt", "UNKNOWN"
                    if siegfried_result and siegfried_result.get("files", [{}])[0].get("matches"):
                        match = siegfried_result["files"][0]["matches"][0]
                        format_name, pronom_id = match.get("format", format_name), match.get("id", pronom_id)
                    log(f"❓ Nicht zugeordnet: '{filepath.name}' (Siegfried: {format_name}, PRONOM: {pronom_id})")
                    unidentified_count += 1

            log("-" * 40 + f"\nAnalyse abgeschlossen.\nDateien {'simuliert' if DRY_RUN else 'umbenannt'}: {renamed_count}\nNicht zugeordnet: {unidentified_count}")
            if unidentified_count > 0: log("\nTipp: PRONOM-IDs zur 'pronom_to_ext_map' hinzufügen.")
            if DRY_RUN and renamed_count > 0: log("\n⚠️  Wenn korrekt, setze DRY_RUN = False.")

    finally:
        if LOG_FILE_HANDLE:
            log("-" * 40 + f"\nProtokoll gespeichert: {log_file_path}"); LOG_FILE_HANDLE.close()

    destination_folder = log_file_path.parent
    
    print("")
    open_folder = input("Zielordner oeffnen? (j/n): ").lower()
    if open_folder == 'j':
        if sys.platform == "win32":
            os.startfile(str(destination_folder))
        elif sys.platform == "darwin":
            subprocess.run(["open", str(destination_folder)])
        else:
            subprocess.run(["xdg-open", str(destination_folder)])
        print("\033[92mZielordner geoeffnet\033[0m")

if __name__ == "__main__":
    main()