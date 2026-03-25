# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import sys
import subprocess
import re
from datetime import datetime
from pathlib import Path
import shutil

# ==============================================================================
# 🔧 KONFIGURATION (1:1 aus Ihren Skripten übernommen)
# ==============================================================================

# --- Audio-Konfiguration ---
FFMPEG_PATH = "ffmpeg.exe"
FFPROBE_PATH = "ffprobe.exe"
SOURCE_AUDIO_EXTENSIONS = {".aiff", ".flac", ".ogg", ".wav", ".m4a", ".wma", ".aac", ".mp3"}

# --- Bild-Konfiguration ---
IMAGEMAGICK_PATH = "magick.exe"
INKSCAPE_PATH = r"C:\Program Files\Inkscape\bin\inkscape.exe"
GHOSTSCRIPT_PATH = "gswin64c.exe"
RASTER_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".heic", ".tga", ".gif", ".jfif"}
GHOSTSCRIPT_FORMATS = {".eps", ".ai"}
VECTOR_EXTENSIONS = {".svg", ".wmf"}
RASTER_TARGET_EXT = ".tiff"
VECTOR_TARGET_EXT = ".pdf"
VALID_IMAGE_EXTENSIONS = RASTER_EXTENSIONS.union(VECTOR_EXTENSIONS).union(GHOSTSCRIPT_FORMATS)

# --- Text/Office-Konfiguration ---
LIBREOFFICE_PATH = "C:/Program Files/LibreOffice/program/soffice.exe"
CONVERSION_MAP = {
    ".doc": ("odt", "writer_pdf_Export"), ".docx": ("odt", "writer_pdf_Export"), ".dot": ("odt", "writer_pdf_Export"),
    ".rtf": ("odt", "writer_pdf_Export"), ".odt": ("odt", "writer_pdf_Export"), ".ott": ("odt", "writer_pdf_Export"),
    ".sxw": ("odt", "writer_pdf_Export"), ".stw": ("odt", "writer_pdf_Export"), ".fodt": ("odt", "writer_pdf_Export"),
    ".uot": ("odt", "writer_pdf_Export"), ".wpd": ("odt", "writer_pdf_Export"), ".wps": ("odt", "writer_pdf_Export"),
    ".abw": ("odt", "writer_pdf_Export"), ".sdw": ("odt", "writer_pdf_Export"), ".wri": ("odt", "writer_pdf_Export"),
    ".html": ("odt", "writer_pdf_Export"), ".htm": ("odt", "writer_pdf_Export"), ".txt": ("odt", "writer_pdf_Export"),
    ".pages": ("odt", "writer_pdf_Export"), ".wbk": ("odt", "writer_pdf_Export"), ".cwk": ("odt", "writer_pdf_Export"),
    ".cws": ("odt", "writer_pdf_Export"), ".xls": ("ods", "calc_pdf_Export"), ".xlsx": ("ods", "calc_pdf_Export"),
    ".xlw": ("ods", "calc_pdf_Export"), ".xlt": ("ods", "calc_pdf_Export"), ".ods": ("ods", "calc_pdf_Export"),
    ".ots": ("ods", "calc_pdf_Export"), ".sxc": ("ods", "calc_pdf_Export"), ".stc": ("ods", "calc_pdf_Export"),
    ".fods": ("ods", "calc_pdf_Export"), ".uos": ("ods", "calc_pdf_Export"), ".ppt": ("odp", "impress_pdf_Export"),
    ".pptx": ("odp", "impress_pdf_Export"), ".pps": ("odp", "impress_pdf_Export"), ".pot": ("odp", "impress_pdf_Export"),
    ".odp": ("odp", "impress_pdf_Export"), ".otp": ("odp", "impress_pdf_Export"), ".sxi": ("odp", "impress_pdf_Export"),
    ".sti": ("odp", "impress_pdf_Export"), ".fodd": ("odp", "impress_pdf_Export"), ".uop": ("odp", "impress_pdf_Export"),
    ".key": ("odp", "impress_pdf_Export"), ".pdf": ("pdf", "draw_pdf_Export")
}
VALID_TEXT_EXTENSIONS = set(CONVERSION_MAP.keys())

# --- Video-Konfiguration ---
SOURCE_VIDEO_EXTENSIONS = {".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm", ".mpg", ".mpeg", ".m4v", ".vob", ".m2ts", ".mts",
    ".mxf", ".ogm", ".ts"}


# ==============================================================================
# --- PFAD- & TOOL-VALIDIERUNG
# ==============================================================================

def setup_and_validate_paths(ac_number, disk_archive_id):
    project_base_path = Path.home() / "Documents/data" / ac_number / disk_archive_id
    transfer_folder = project_base_path / f"3_{disk_archive_id}_for-transfer"
    
    paths = { "source_folder": transfer_folder / "files", "log_file": transfer_folder / f"3_{disk_archive_id}_for-transfer_all-conversions.log" }

    if not paths["source_folder"].is_dir():
        print(f"\033[91mFehler: Der Quell-Ordner wurde nicht gefunden:\n{paths['source_folder']}\033[0m"); return None

    required_tools = [ FFMPEG_PATH, FFPROBE_PATH, IMAGEMAGICK_PATH, INKSCAPE_PATH, GHOSTSCRIPT_PATH, LIBREOFFICE_PATH ]
    missing_tools = [tool for tool in required_tools if not shutil.which(tool)]
    
    if missing_tools:
        print("\033[91mFehler: Die folgenden benötigten Programme wurden nicht gefunden:\033[0m")
        for tool in missing_tools: print(f"- {tool}")
        print("\nBitte installieren Sie die Programme und/oder fügen Sie deren Ordner zum Windows PATH hinzu."); return None

    print("\033[92mAlle Pfade und Programme wurden erfolgreich gefunden und validiert.\033[0m"); return paths

# ==============================================================================
# --- HELPER-FUNKTIONEN
# ==============================================================================

LOG_FILE_HANDLE = None

def log(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "); full_message = timestamp + message
    print(full_message)
    if LOG_FILE_HANDLE:
        try: LOG_FILE_HANDLE.write(full_message + "\n")
        except Exception as e: print(f"\033[91mKRITISCHER FEHLER: Konnte nicht in Log-Datei schreiben: {e}\033[0m")

def run_generic_command(command, cwd=None):
    try:
        command_str_list = [str(item) for item in command]
        log(f"         Befehl: {' '.join(command_str_list)}")
        result = subprocess.run(command_str_list, capture_output=True, text=True, encoding='utf-8', errors='ignore', cwd=cwd)
        if result.returncode == 0: return True
        else:
            log(f"         [FEHLER] Befehl fehlgeschlagen (Code {result.returncode})")
            if result.stderr: log(f"                  Fehlermeldung: {result.stderr.strip()}")
            return False
    except FileNotFoundError: log(f"         [KRITISCHER FEHLER] Befehl '{command[0]}' nicht gefunden."); return False
    except Exception as e: log(f"         [FEHLER] Ein unerwartetes Problem ist aufgetreten: {e}"); return False

# ==============================================================================
# --- AUDIO-LOGIK (1:1 aus Ihrem Skript übernommen) ---
# ==============================================================================

def get_audio_duration(input_path):
    try:
        result = subprocess.run([FFPROBE_PATH, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(input_path)], capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception: log(f"         [FEHLER] Dauer für '{os.path.basename(input_path)}' konnte nicht ermittelt werden."); return None

def convert_audio_with_progress(input_path, output_path, codec_options=None):
    duration = get_audio_duration(input_path)
    if duration is None: return False
    log(f"         Starte Konvertierung: {os.path.basename(input_path)} → {os.path.basename(output_path)}")
    command = [FFMPEG_PATH, "-y", "-i", input_path]
    if codec_options: command.extend(codec_options)
    command.extend([output_path, "-progress", "pipe:1", "-nostats", "-loglevel", "error"])
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, encoding='utf-8', errors='replace')
    while True:
        line = process.stdout.readline();
        if not line: break
        match = re.search(r'out_time_ms=(\d+)', line)
        if match:
            progress = min(int(match.group(1)) / (duration * 1_000_000), 1.0) if duration > 0 else 1.0
            bar = "#" * int(progress * 40); sys.stdout.write(f"\r[{bar:<40}] {progress*100:.1f}%"); sys.stdout.flush()
    process.wait(); sys.stdout.write('\r' + ' ' * 80 + '\r'); sys.stdout.flush()
    if process.returncode == 0: log(f"         [OK] Erfolgreich konvertiert: {os.path.basename(output_path)}"); return True
    else:
        stderr_output = process.stderr.read(); log(f"         [FEHLER] Konvertierung fehlgeschlagen für: {os.path.basename(input_path)}")
        if stderr_output: log(f"                  FFmpeg-Fehler: {stderr_output.strip()}");
        return False

def process_audio_file(filepath):
    root, filename = os.path.split(filepath); ext = filepath.suffix.lower()
    mp3_target_path = os.path.join(root, f"{filename}.mp3"); wav_target_path = os.path.join(root, f"{filename}.wav")
    if ext not in {".mp3", ".wav"}:
        log("         -> Fremdformat erkannt. Erstelle MP3 und WAV.")
        convert_audio_with_progress(filepath, mp3_target_path, codec_options=["-c:a", "libmp3lame", "-q:a", "2"])
        convert_audio_with_progress(filepath, wav_target_path, codec_options=["-c:a", "pcm_s16le"])
    elif ext == ".mp3": log("         -> MP3-Original erkannt. Erstelle nur WAV."); convert_audio_with_progress(filepath, wav_target_path, codec_options=["-c:a", "pcm_s16le"])
    elif ext == ".wav": log("         -> WAV-Original erkannt. Erstelle nur MP3."); convert_audio_with_progress(filepath, mp3_target_path, codec_options=["-c:a", "libmp3lame", "-q:a", "2"])

# ==============================================================================
# --- BILD-LOGIK (1:1 aus Ihrem Skript übernommen) ---
# ==============================================================================

def process_image_file(filepath):
    root, filename = os.path.split(filepath); base, ext = os.path.splitext(filename); ext = ext.lower()
    if ext in RASTER_EXTENSIONS:
        tool_name, target_ext = "ImageMagick", RASTER_TARGET_EXT; output_filename = f"{base}{ext}{target_ext}"
        output_path = os.path.join(root, output_filename); cmd = [IMAGEMAGICK_PATH, "-quiet", filepath, output_path]
    elif ext in GHOSTSCRIPT_FORMATS:
        tool_name, target_ext = "Ghostscript", VECTOR_TARGET_EXT; output_filename = f"{base}{ext}{target_ext}"
        output_path = os.path.join(root, output_filename); cmd = [GHOSTSCRIPT_PATH, "-sDEVICE=pdfwrite", "-dBATCH", "-dNOPAUSE", f"-sOutputFile={output_path}", filepath]
    elif ext in VECTOR_EXTENSIONS:
        tool_name, target_ext = "Inkscape", VECTOR_TARGET_EXT; output_filename = f"{base}{ext}{target_ext}"
        output_path = os.path.join(root, output_filename); cmd = [INKSCAPE_PATH, filepath, f"--export-filename={output_path}", "--export-text-to-path", "--export-pdf-version=1.5"]
    else: return
    log(f"         Konvertiere mit {tool_name}: {filename} -> {output_filename}")
    if os.path.exists(output_path):
        try: os.remove(output_path); log(f"         [INFO] Alte Zieldatei wird überschrieben: {output_filename}")
        except OSError as e: log(f"         [FEHLER] Alte Zieldatei konnte nicht gelöscht werden: {output_filename} ({e})"); return
    if run_generic_command(cmd): log(f"         [OK] Erfolgreich konvertiert.")
    else: log(f"         [FEHLER] Konvertierung fehlgeschlagen.")

# ==============================================================================
# --- TEXT/OFFICE-LOGIK (1:1 aus Ihrem Skript übernommen) ---
# ==============================================================================

def process_text_file(filepath):
    root, filename = os.path.split(filepath); name, ext = os.path.splitext(filename); ext = ext.lower()
    target_odf_ext, pdf_export_filter = CONVERSION_MAP[ext]
    odf_filename = f"{name}{ext}.{target_odf_ext}"; odf_path_target = os.path.join(root, odf_filename)
    pdf_filename = f"{name}{ext}.pdf"; pdf_path = os.path.join(root, pdf_filename)
    
    if os.path.exists(odf_path_target): os.remove(odf_path_target)
    if os.path.exists(pdf_path): os.remove(pdf_path)

    is_original_pdf = (ext == ".pdf")
    if is_original_pdf: source_for_pdf_export = filepath
    else:
        log(f"         -> Schritt 1: Konvertiere zu ODF ({odf_filename})")
        cmd_convert = [LIBREOFFICE_PATH, "--headless", "--convert-to", target_odf_ext, "--outdir", root, filepath]
        subprocess.run(cmd_convert, capture_output=True, text=True)
        real_odf_name_by_lo = f"{name}.{target_odf_ext}"; real_odf_path_by_lo = os.path.join(root, real_odf_name_by_lo)
        if os.path.exists(real_odf_path_by_lo):
            os.replace(real_odf_path_by_lo, odf_path_target); source_for_pdf_export = odf_path_target
        else: log(f"\n         [FEHLER] Konvertierung zu ODF fehlgeschlagen für: {filename}"); return
    
    log(f"         -> Schritt 2: Konvertiere zu PDF/A ({pdf_filename})")
    pdfa_filter_string = f"pdf:{pdf_export_filter}:SelectPdfVersion=2"
    temp_output_dir = os.path.join(root, "temp_pdf_conversion"); os.makedirs(temp_output_dir, exist_ok=True)
    cmd_pdf = [LIBREOFFICE_PATH, "--headless", "--convert-to", pdfa_filter_string, "--outdir", temp_output_dir, source_for_pdf_export]
    subprocess.run(cmd_pdf, capture_output=True, text=True)
    base_name_for_pdf = os.path.splitext(os.path.basename(source_for_pdf_export))[0]
    real_pdf_path_by_lo = os.path.join(temp_output_dir, f"{base_name_for_pdf}.pdf")
    if os.path.exists(real_pdf_path_by_lo):
        shutil.move(real_pdf_path_by_lo, pdf_path); log(f"         [OK] Konvertierung erfolgreich: {filename} -> {pdf_filename}")
    else: log(f"         [FEHLER] PDF/A-Export fehlgeschlagen für: {filename}")
    if os.path.exists(temp_output_dir): shutil.rmtree(temp_output_dir)

# ==============================================================================
# --- VIDEO-LOGIK (1:1 aus Ihrem Skript übernommen) ---
# ==============================================================================

def process_video_file(filepath):
    """Konvertiert eine Videodatei nach MP4."""
    root, filename = os.path.split(filepath)
    mp4_target_path = os.path.join(root, f"{filename}.mp4")
    
    log(f"         Starte Konvertierung: {filename} → {os.path.basename(mp4_target_path)}")
    
    command = [
        FFMPEG_PATH, "-y", "-i", filepath,
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        mp4_target_path
    ]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
        log(f"         [OK] Erfolgreich konvertiert: {os.path.basename(mp4_target_path)}")
    except subprocess.CalledProcessError as e:
        log(f"         [FEHLER] Konvertierung fehlgeschlagen für: {filename}")
        log(f"                  FFmpeg-Fehler: {e.stderr.strip()}")

# ==============================================================================
# --- HAUPT-AUSFÜHRUNGSBLOCK ---
# ==============================================================================
if __name__ == "__main__":
    try:
        ac_number_input, disk_archive_id_input = sys.argv[1], sys.argv[2]
        print(f"Werte aus der Kommandozeile erhalten: AC={ac_number_input}, ID={disk_archive_id_input}")
    except IndexError: print("FEHLER: AC-Nummer und Datenträger-ID wurden nicht übergeben."); sys.exit(1)

    validated_paths = setup_and_validate_paths(ac_number_input, disk_archive_id_input)
    if validated_paths:
        source_folder, LOG_FILE = validated_paths["source_folder"], validated_paths["log_file"]
        if os.path.exists(LOG_FILE): os.remove(LOG_FILE)
        LOG_FILE_HANDLE = open(LOG_FILE, "a", encoding="utf-8")
        print(f"\nSkript wird mit folgenden Pfaden ausgeführt:\n- Quell-Ordner: {source_folder}\n- Log-Datei: {LOG_FILE}\n")
        log("Starte kombiniertes Konvertierungsskript.")
        
        all_valid_extensions = SOURCE_AUDIO_EXTENSIONS.union(VALID_IMAGE_EXTENSIONS).union(VALID_TEXT_EXTENSIONS).union(SOURCE_VIDEO_EXTENSIONS)
        
        files_to_process = []
        for root, _, files in os.walk(source_folder):
            for filename in files:
                if filename.startswith('.') or filename.startswith('~'): continue
                ext = Path(filename).suffix.lower()
                if ext in all_valid_extensions:
                    # Robuste Logik zur Vermeidung von Doppelkonvertierung
                    name_part = Path(filename).stem
                    is_derivative = False
                    for source_ext in all_valid_extensions:
                        if name_part.lower().endswith(source_ext): is_derivative = True; break
                    
                    if is_derivative and ext != '.pdf': continue
                    if is_derivative and ext == '.pdf' and '.' in name_part: continue
                    
                    files_to_process.append(Path(root) / filename)
        
        if not files_to_process: log("Keine zu verarbeitenden Dateien gefunden.")
        else:
            total = len(files_to_process)
            log(f"{total} relevante Dateien gefunden. Beginne Verarbeitung...")
            for idx, filepath in enumerate(files_to_process, 1):
                ext = filepath.suffix.lower(); percent = (idx / total) * 100
                log(f"\n--- [{idx}/{total}] {percent:.2f}% Verarbeite '{filepath.name}' ---")

                if ext in SOURCE_AUDIO_EXTENSIONS: process_audio_file(filepath)
                elif ext in VALID_IMAGE_EXTENSIONS: process_image_file(filepath)
                elif ext in VALID_TEXT_EXTENSIONS: process_text_file(filepath)
                elif ext in SOURCE_VIDEO_EXTENSIONS: process_video_file(filepath)
                
            log("\nAlle Konvertierungen abgeschlossen.")
        LOG_FILE_HANDLE.close()

        # --- ANFANG: HINZUGEFÜGTER CODE-BLOCK ---
        # Der Zielordner ist der übergeordnete Ordner des Quellordners (also der "for-transfer"-Ordner)
        destination_folder = validated_paths["source_folder"].parent
        
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