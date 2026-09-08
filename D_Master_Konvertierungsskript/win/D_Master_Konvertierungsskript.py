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
import time      # Für Warteschleifen
import glob      # Zum Finden der PDFs (Löst das Problem mit den Punkten)
import tempfile 

# ==============================================================================
# 🔧 KONFIGURATION
# ==============================================================================

# --- Audio-Konfiguration ---
FFMPEG_PATH = "ffmpeg.exe"
FFPROBE_PATH = "ffprobe.exe"
SOURCE_AUDIO_EXTENSIONS = {".aiff", ".flac", ".ogg", ".wav", ".m4a", ".wma", ".aac", ".mp3", ".opus", ".voc"}

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
    ".fods": ("ods", "calc_pdf_Export"), ".uos": ("ods", "calc_pdf_Export"), ".tsv": ("ods", "calc_pdf_Export"),
    ".ppt": ("odp", "impress_pdf_Export"),
    ".pptx": ("odp", "impress_pdf_Export"), ".pps": ("odp", "impress_pdf_Export"), ".pot": ("odp", "impress_pdf_Export"),
    ".odp": ("odp", "impress_pdf_Export"), ".otp": ("odp", "impress_pdf_Export"), ".sxi": ("odp", "impress_pdf_Export"),
    ".sti": ("odp", "impress_pdf_Export"), ".fodd": ("odp", "impress_pdf_Export"), ".uop": ("odp", "impress_pdf_Export"),
    ".key": ("odp", "impress_pdf_Export"), ".pdf": ("pdf", "draw_pdf_Export")
}
VALID_TEXT_EXTENSIONS = set(CONVERSION_MAP.keys())

# --- Video-Konfiguration ---
SOURCE_VIDEO_EXTENSIONS = {".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm", ".mpg", ".mpeg", ".m4v", ".vob", ".m2ts", ".mts",
    ".mxf", ".ogm", ".ts", ".mp4", ".ogv", ".r3d", ".3gp", ".asf", ".dv", ".f4v", ".gxf", ".m1v", ".m2v",
    ".mp2v", ".mpe", ".mpv", ".qt", ".rm", ".swf", ".tp", ".trp", ".vdr", ".viv", ".vivo", ".vro", ".wtv"}

# Globale Liste für fehlgeschlagene Konvertierungen
conversion_errors = []

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
# --- NEU: PDF/A ERKENNUNG
# ==============================================================================

def is_already_pdfa(filepath):
    """
    Prüft heuristisch, ob eine PDF-Datei bereits PDF/A-konform ist.
    Durchsucht die ersten 2 MB der Datei nach typischen XMP-Metadaten-Markern für PDF/A.
    """
    try:
        with open(filepath, 'rb') as f:
            # Lese einen großen Block vom Anfang (XMP steht oft im Header oder kurz danach)
            chunk = f.read(2097152) # 2 MB
            # Typische Marker für PDF/A im XMP Packet
            if b'pdfaid:part' in chunk or b'pdfaid:conformance' in chunk:
                return True
            # Alternativer Marker
            if b'PDF/A' in chunk:
                return True
    except Exception:
        pass
    return False

# ==============================================================================
# --- AUDIO-LOGIK
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
    if process.returncode == 0: log(f"         [OK] Erfolgreich konvertiert: {os.path.basename(output_path)} Primär."); return True
    else:
        stderr_output = process.stderr.read(); log(f"         [FEHLER] Konvertierung fehlgeschlagen für: {os.path.basename(input_path)}")
        if stderr_output: log(f"                  FFmpeg-Fehler: {stderr_output.strip()}");
        return False

def process_audio_file(filepath):
    root, filename = os.path.split(filepath); ext = filepath.suffix.lower()
    mp3_target_path = os.path.join(root, f"{filename}.mp3"); wav_target_path = os.path.join(root, f"{filename}.wav")
    errors_occured = False
    if ext not in {".mp3", ".wav"}:
        log("         -> Fremdformat erkannt. Erstelle MP3 und WAV.")
        if not convert_audio_with_progress(filepath, mp3_target_path, codec_options=["-c:a", "libmp3lame", "-q:a", "2"]): errors_occured = True
        if not convert_audio_with_progress(filepath, wav_target_path, codec_options=["-c:a", "pcm_s16le"]): errors_occured = True
    elif ext == ".mp3": 
        log("         -> MP3-Original erkannt. Erstelle nur WAV.")
        if not convert_audio_with_progress(filepath, wav_target_path, codec_options=["-c:a", "pcm_s16le"]): errors_occured = True
    elif ext == ".wav": 
        log("         -> WAV-Original erkannt. Erstelle nur MP3.")
        if not convert_audio_with_progress(filepath, mp3_target_path, codec_options=["-c:a", "libmp3lame", "-q:a", "2"]): errors_occured = True
    
    if errors_occured:
        conversion_errors.append((filename, "Audio-Konvertierung (FFmpeg) unvollständig oder fehlgeschlagen."))

# ==============================================================================
# --- BILD-LOGIK
# ==============================================================================

def process_image_file(filepath):
    root, filename = os.path.split(filepath); base, ext = os.path.splitext(filename); ext = ext.lower()
    tool_name = ""
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
        try: os.remove(output_path); log(f"         [INFO] Alte Zieldatei wird überschrieben.")
        except OSError: pass

    if run_generic_command(cmd): log(f"         [OK] Erfolgreich konvertiert.")
    else: 
        log(f"         [FEHLER] Konvertierung fehlgeschlagen.")
        conversion_errors.append((filename, f"Bild-Konvertierung ({tool_name}) fehlgeschlagen."))

# ==============================================================================
# --- TEXT/OFFICE-LOGIK (Inkl. Pfad-Fix und PDF/A-Check)
# ==============================================================================

def process_text_file(filepath):
    root, filename = os.path.split(filepath)
    name, ext = os.path.splitext(filename)
    ext = ext.lower()
    target_odf_ext, pdf_export_filter = CONVERSION_MAP[ext]
    
    # ODF Name bleibt gleich
    odf_filename = f"{name}{ext}.{target_odf_ext}"
    odf_path_target = os.path.join(root, odf_filename)
    
    # NEU: Sauberer Name für PDF-Derivate (vermeidet .pdf.pdf)
    if ext == ".pdf":
        pdf_filename = f"{name}pdf.pdf"
    else:
        pdf_filename = f"{name}{ext}.pdf"
        
    pdf_path = os.path.join(root, pdf_filename)
    
    if os.path.exists(odf_path_target): os.remove(odf_path_target)
    if os.path.exists(pdf_path): os.remove(pdf_path)

    source_for_pdf_export = ""
    
    # SCHRITT 1: ODF (oder PDF-Check)
    if ext == ".pdf": 
        # NEU: Prüfen ob bereits PDF/A
        if is_already_pdfa(filepath):
            log(f"         [OK] Datei ist bereits PDF/A. Überspringe Konvertierung.")
            return
            
        source_for_pdf_export = filepath
    else:
        log(f"         -> Schritt 1: Konvertiere zu ODF ({odf_filename})")
        
        # 1. Versuch: Standard-Konvertierung
        subprocess.run([LIBREOFFICE_PATH, "--headless", "--convert-to", target_odf_ext, "--outdir", root, filepath], capture_output=True)
        
        # 2. Versuch: Wenn .sdw erkannt wird, versuche StarWriter-Filter explizit
        if not any(f.startswith(name) and f.endswith(f".{target_odf_ext}") for f in os.listdir(root)) and ext == ".sdw":
            log(f"         [INFO] Standard-Filter fehlgeschlagen, erzwinge StarWriter-Import...")
            subprocess.run([LIBREOFFICE_PATH, "--headless", "--infilter=StarWriter 5.0", "--convert-to", target_odf_ext, "--outdir", root, filepath], capture_output=True)
        
        # 3. Versuch: Wenn immer noch nichts da ist, .doc Auto-Detection (für getarnte Dateien)
        if not any(f.startswith(name) and f.endswith(f".{target_odf_ext}") for f in os.listdir(root)):
            log(f"         [INFO] Filter fehlgeschlagen, versuche .doc Auto-Detection...")
            temp_doc = os.path.join(root, f"{name}_temp.doc")
            shutil.copy2(filepath, temp_doc)
            subprocess.run([LIBREOFFICE_PATH, "--headless", "--convert-to", target_odf_ext, "--outdir", root, temp_doc], capture_output=True)
            if os.path.exists(temp_doc): os.remove(temp_doc)

        # Suche nach der Datei
        generated_files = [f for f in os.listdir(root) if f.startswith(name) and f.endswith(f".{target_odf_ext}")]
        
        if generated_files:
            best_match = os.path.join(root, generated_files[0])
            os.replace(best_match, odf_path_target)
            source_for_pdf_export = odf_path_target
        else: 
            log(f"         [FEHLER] ODF-Erstellung fehlgeschlagen.")
            conversion_errors.append((filename, "LibreOffice: ODF-Zwischenschritt fehlgeschlagen."))
            return
    
    # SCHRITT 2: PDF/A
    log(f"         -> Schritt 2: Konvertiere zu PDF/A ({pdf_filename})")
    temp_output_dir = os.path.join(tempfile.gettempdir(), "lo_conversion_work")
    if os.path.exists(temp_output_dir): shutil.rmtree(temp_output_dir, ignore_errors=True)
    os.makedirs(temp_output_dir, exist_ok=True)
    
    pdfa_filter_string = f"pdf:{pdf_export_filter}:SelectPdfVersion=2"
    cmd_pdf = [LIBREOFFICE_PATH, "--headless", "--convert-to", pdfa_filter_string, "--outdir", temp_output_dir, source_for_pdf_export]
    subprocess.run(cmd_pdf, capture_output=True)
    
    time.sleep(1.0)
    generated_pdfs = glob.glob(os.path.join(temp_output_dir, "*.pdf"))
    if generated_pdfs:
        try:
            shutil.move(generated_pdfs[0], pdf_path)
            log(f"         [OK] Erfolgreich konvertiert.")
        except Exception as e:
            log(f"         [FEHLER] Fehler beim Verschieben: {e}")
            conversion_errors.append((filename, f"Dateisystem-Fehler beim Verschieben der PDF: {e}"))
    else: 
        log(f"         [FEHLER] PDF/A-Export fehlgeschlagen.")
        conversion_errors.append((filename, "LibreOffice: PDF/A-Export fehlgeschlagen."))
    
    shutil.rmtree(temp_output_dir, ignore_errors=True)

# ==============================================================================
# --- VIDEO-LOGIK (Mit Long-Path-Fix und R3D-Toleranz)
# ==============================================================================

def process_video_file(filepath):
    root, filename = os.path.split(filepath)
    path_obj = Path(filepath)
    ext = path_obj.suffix.lower()
    
    # 1. Intelligente Prüfung: Ist es bereits eine MKV mit den richtigen Codecs?
    if ext == ".mkv":
        try:
            # Video-Codec prüfen
            v_codec = subprocess.run(
                [FFPROBE_PATH, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name", "-of", "default=noprint_wrappers=1:nokey=1", str(filepath)],
                capture_output=True, text=True, check=True
            ).stdout.strip()
            
            # Audio-Codec prüfen (erster Audio-Stream)
            a_codec = subprocess.run(
                [FFPROBE_PATH, "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=codec_name", "-of", "default=noprint_wrappers=1:nokey=1", str(filepath)],
                capture_output=True, text=True, check=True
            ).stdout.strip()
            
            if v_codec == "ffv1" and a_codec in ["flac", ""]:
                log(f"         [INFO] Datei ist bereits im Archivformat (FFV1/FLAC in MKV). Konvertierung übersprungen.")
                return
            else:
                log(f"         [INFO] MKV erkannt, aber Codecs ({v_codec}/{a_codec}) entsprechen nicht dem Archivstandard. Wird neu kodiert.")
                mkv_target_path = os.path.join(root, f"{filename}")
        except Exception as e:
            log(f"         [WARNUNG] Codec-Prüfung fehlgeschlagen ({e}). Datei wird sicherheitshalber neu konvertiert.")
            mkv_target_path = os.path.join(root, f"{filename}")
    else:
        # Bei allen anderen Formaten: dateiname.originalendung.mkv
        mkv_target_path = os.path.join(root, f"{filename}.mkv")
    
    log(f"         Starte Konvertierung: {filename} → {os.path.basename(mkv_target_path)}")
    
    # WICHTIG: Absolute Pfade mit Windows Long-Path-Präfix (\\?\) erstellen
    abs_input = os.path.abspath(filepath)
    abs_output = os.path.abspath(mkv_target_path)
    if os.name == 'nt':
        abs_input = "\\\\?\\" + abs_input
        abs_output = "\\\\?\\" + abs_output

    # Sicherheitsmaßnahme: Verhindert Korruption, falls Quelle und Ziel identisch sind
    if abs_input == abs_output:
        temp_target_path = "\\\\?\\" + os.path.abspath(os.path.join(root, f"{path_obj.stem}_temp_convert.mkv"))
        final_target_path = abs_output
    else:
        temp_target_path = abs_output
        final_target_path = abs_output

    command = [
        FFMPEG_PATH, "-y",
        "-err_detect", "ignore_err",
        "-i", abs_input,
        "-c:v", "ffv1",
        "-c:a", "flac",
        temp_target_path
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
        
        if temp_target_path != final_target_path:
            if os.path.exists(final_target_path):
                os.remove(final_target_path)
            os.replace(temp_target_path, final_target_path)
            
        log(f"         [OK] Erfolgreich konvertiert.")
    except subprocess.CalledProcessError as e:
        log(f"         [FEHLER] Video-Konvertierung fehlgeschlagen.")
        if temp_target_path != final_target_path and os.path.exists(temp_target_path):
            os.remove(temp_target_path)
        conversion_errors.append((filename, f"Video-Konvertierung (FFmpeg) fehlgeschlagen: {e.stderr[:200]}"))

# ==============================================================================
# --- HAUPT-AUSFÜHRUNGSBLOCK ---
# ==============================================================================
if __name__ == "__main__":
    try:
        ac_number_input, disk_archive_id_input = sys.argv[1], sys.argv[2]
    except IndexError: print("FEHLER: AC-Nummer und Datenträger-ID wurden nicht übergeben."); sys.exit(1)

    validated_paths = setup_and_validate_paths(ac_number_input, disk_archive_id_input)
    if validated_paths:
        source_folder, LOG_FILE = validated_paths["source_folder"], validated_paths["log_file"]
        if os.path.exists(LOG_FILE): os.remove(LOG_FILE)
        LOG_FILE_HANDLE = open(LOG_FILE, "a", encoding="utf-8")
        
        log("Starte kombiniertes Konvertierungsskript.")
        
        all_valid_extensions = SOURCE_AUDIO_EXTENSIONS.union(VALID_IMAGE_EXTENSIONS).union(VALID_TEXT_EXTENSIONS).union(SOURCE_VIDEO_EXTENSIONS)
        
        files_to_process = []
        for root, _, files in os.walk(source_folder):
            for filename in files:
                if filename.startswith('.') or filename.startswith('~'): continue
                ext = Path(filename).suffix.lower()
                if ext in all_valid_extensions:
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
            for idx, filepath in enumerate(files_to_process, 1):
                ext = filepath.suffix.lower(); percent = (idx / total) * 100
                log(f"\n--- [{idx}/{total}] {percent:.2f}% Verarbeite '{filepath.name}' ---")
                if ext in SOURCE_AUDIO_EXTENSIONS: process_audio_file(filepath)
                elif ext in VALID_IMAGE_EXTENSIONS: process_image_file(filepath)
                elif ext in VALID_TEXT_EXTENSIONS: process_text_file(filepath)
                elif ext in SOURCE_VIDEO_EXTENSIONS: process_video_file(filepath)
                
            log("\n" + "="*60)
            log("VERARBEITUNG ABGESCHLOSSEN")
            log("="*60)

            # --- EXKLUSIVE FEHLER-ZUSAMMENFASSUNG ---
            if conversion_errors:
                summary = "\n🚨 ACHTUNG: Folgende Dateien konnten NICHT korrekt konvertiert werden:\n"
                summary += "!" * 70 + "\n"
                for fname, reason in conversion_errors:
                    summary += f" Datei: {fname}\n Grund: {reason}\n" + "-"*70 + "\n"
                
                # Ausgabe in Rot im Terminal
                print(f"\033[91m{summary}\033[0m")
                # Ins Log schreiben
                if LOG_FILE_HANDLE: LOG_FILE_HANDLE.write(summary)
            else:
                log("\n✅ Alle Dateien wurden erfolgreich ohne Fehler konvertiert.")

        # ==============================================================================
        # --- NEU: Tree-Generierung für den Transfer-Ordner (am Ende, damit alle Derivate enthalten sind)
        # ==============================================================================
        transfer_dir = validated_paths["source_folder"].parent
        transfer_files_dir = validated_paths["source_folder"]
        tree_filename = f"3_{disk_archive_id_input}_for-transfer_tree.txt"
        tree_output_file = transfer_dir / tree_filename

        log(f"\n--- Erstelle '{tree_filename}' für den Transfer-Ordner... ---")
        tree_command = f'cmd /c tree "{str(transfer_files_dir)}" /A /F > "{str(tree_output_file)}"'
        
        try:
            subprocess.run(tree_command, shell=True, check=True, text=True, encoding='utf-8', errors='replace')
            
            if tree_output_file.exists() and tree_output_file.stat().st_size > 0:
                log(f"--- '{tree_filename}' erfolgreich erstellt unter: {tree_output_file} ---")
            else:
                log(f"--- WARNUNG: '{tree_filename}' konnte nicht erstellt werden oder ist leer. ---")
        except subprocess.CalledProcessError as e:
            log(f"--- FEHLER beim Ausführen von 'tree.exe': Befehl schlug fehl mit Code {e.returncode}. ---")
        except Exception as e:
            log(f"--- FEHLER beim manuellen Erstellen von '{tree_filename}': {e} ---")
        # ==============================================================================

        # JETZT erst wird die Log-Datei geschlossen, nachdem ALLE log()-Aufrufe erledigt sind
        LOG_FILE_HANDLE.close()

        destination_folder = transfer_dir
        print("")
        if input("Zielordner oeffnen? (j/n): ").lower() == 'j':
            os.startfile(destination_folder)

    print("\nSkript beendet.")