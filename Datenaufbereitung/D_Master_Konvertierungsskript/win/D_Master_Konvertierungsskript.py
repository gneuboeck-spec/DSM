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
import glob      # Zum Finden der PDFs
import tempfile 
import mailbox   # Für MBOX/DBX Verarbeitung
import email     # Für E-Mail Parsing
import email.utils
from email.header import decode_header
import email.header # Explizit für Header-Typ-Checking

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class Fore: GREEN = RED = YELLOW = CYAN = MAGENTA = WHITE = ""
    class Style: RESET_ALL = ""

# ==============================================================================
# 🔧 DYNAMISCHE PFADERMITTLUNG FÜR EXTERNE TOOLS
# ==============================================================================

def find_executable(tool_name, fallback_path):
    """Findet eine ausführbare Datei im System-PATH oder nutzt den Fallback-Pfad."""
    exe_path = shutil.which(tool_name)
    if exe_path:
        return exe_path
    
    if Path(fallback_path).exists():
        return fallback_path
    
    return fallback_path

# ==============================================================================
# 🔧 KONFIGURATION
# ==============================================================================

# --- Audio-Konfiguration ---
FFMPEG_PATH = "ffmpeg.exe"
FFPROBE_PATH = "ffprobe.exe"
SOURCE_AUDIO_EXTENSIONS = {".aiff", ".flac", ".ogg", ".wav", ".m4a", ".wma", ".aac", ".mp3", ".opus", ".voc"}

# --- Bild-Konfiguration ---
IMAGEMAGICK_PATH = "magick.exe"
INKSCAPE_PATH = find_executable("inkscape.exe", r"C:\Program Files\Inkscape\bin\inkscape.exe")
GHOSTSCRIPT_PATH = "gswin64c.exe"
RASTER_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".heic", ".tga", ".gif", ".jfif"}
GHOSTSCRIPT_FORMATS = {".eps", ".ai"}
VECTOR_EXTENSIONS = {".svg", ".wmf"}
RASTER_TARGET_EXT = ".tiff"
VECTOR_TARGET_EXT = ".pdf"
VALID_IMAGE_EXTENSIONS = RASTER_EXTENSIONS.union(VECTOR_EXTENSIONS).union(GHOSTSCRIPT_FORMATS)

# --- Text/Office-Konfiguration ---
LIBREOFFICE_PATH = find_executable("soffice.exe", r"C:\Program Files\LibreOffice\program\soffice.exe")
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

# --- NEU: DBX / E-MAIL KONFIGURATION ---
DBX_CONV_PATH = "DbxConv.exe"

# Globale Liste für fehlgeschlagene Konvertierungen
conversion_errors = []

# ==============================================================================
# --- PFAD- & TOOL-VALIDIERUNG
# ==============================================================================

def setup_and_validate_paths(ac_number, disk_archive_id, project_base_path_override=None):
    if project_base_path_override:
        project_base_path = Path(project_base_path_override)
    else:
        project_base_path = Path.home() / "Documents/data" / ac_number / disk_archive_id
        
    transfer_folder = project_base_path / f"3_{disk_archive_id}_for-transfer"
    
    paths = { "source_folder": transfer_folder / "files", "log_file": transfer_folder / f"3_{disk_archive_id}_for-transfer_all-conversions.log" }

    if not paths["source_folder"].is_dir():
        print(f"{Fore.RED}Fehler: Der Quell-Ordner wurde nicht gefunden:\n{paths['source_folder']}{Style.RESET_ALL}"); return None

    required_tools = [ FFMPEG_PATH, FFPROBE_PATH, IMAGEMAGICK_PATH, INKSCAPE_PATH, GHOSTSCRIPT_PATH, LIBREOFFICE_PATH, DBX_CONV_PATH ]
    missing_tools = [tool for tool in required_tools if not shutil.which(tool)]
    
    if missing_tools:
        print(f"{Fore.RED}Fehler: Die folgenden benötigten Programme wurden nicht gefunden:{Style.RESET_ALL}")
        for tool in missing_tools: print(f"- {tool}")
        print(f"\n{Fore.YELLOW}Bitte installieren Sie die Programme und/oder fügen Sie deren Ordner zum Windows PATH hinzu.{Style.RESET_ALL}"); return None

    print(f"{Fore.GREEN}Alle Pfade und Programme wurden erfolgreich gefunden und validiert.{Style.RESET_ALL}"); return paths

# ==============================================================================
# --- HELPER-FUNKTIONEN
# ==============================================================================

LOG_FILE_HANDLE = None

def log(message):
    # NEU: Robuste Bereinigung der aktuellen Konsolenzeile vor jeder Ausgabe
    sys.stdout.write('\r') 
    sys.stdout.write(' ' * 150) 
    sys.stdout.write('\r') 
    sys.stdout.flush()

    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
    full_message = timestamp + message
    print(full_message)
    
    if LOG_FILE_HANDLE:
        try: 
            LOG_FILE_HANDLE.write(full_message + "\n")
        except Exception as e: 
            print(f"{Fore.RED}KRITISCHER FEHLER: Konnte nicht in Log-Datei schreiben: {e}{Style.RESET_ALL}")

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
# --- NEU: HELPER FÜR DBX & E-MAIL
# ==============================================================================

def sanitize_filename(text):
    """Bereinigt Dateinamen für Windows-Kompatibilität."""
    if text is None: 
        return "Unbenannt"
    
    try:
        if isinstance(text, email.header.Header):
            text = str(text)
    except:
        pass
    
    if not isinstance(text, str):
        try:
            text = str(text)
        except:
            return "Unbenannt"
    
    try:
        decoded_parts = decode_header(text)
        clean_text = ""
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                clean_text += part.decode(encoding or 'latin1', errors='replace')
            else:
                clean_text += str(part)
        text = clean_text
    except Exception:
        pass
    
    text = re.sub(r'[<>:"/\\|?*]', '_', text)
    text = re.sub(r'\s+', '_', text.strip())
    if text.startswith('.'): 
        text = text[1:]
    return text[:100] or "Unbenannt"

# ==============================================================================
# --- NEU: PDF/A ERKENNUNG
# ==============================================================================

def is_already_pdfa(filepath):
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(2097152) 
            if b'pdfaid:part' in chunk or b'pdfaid:conformance' in chunk:
                return True
            if b'PDF/A' in chunk:
                return True
    except Exception:
        pass
    return False

# ==============================================================================
# --- NEU: DBX & E-MAIL LOGIK
# ==============================================================================

def extract_emails_from_dbx(dbx_path, output_dir):
    """Konvertiert DBX zu MBOX und extrahiert E-Mails sowie Anhänge."""
    root = dbx_path.parent
    mbx_temp_path = root / f"{dbx_path.stem}.mbx"
    mbox_path = root / f"{dbx_path.stem}.mbox"
    
    if mbx_temp_path.exists(): 
        mbx_temp_path.unlink()
    if mbox_path.exists(): 
        mbox_path.unlink()
    
    cmd = [DBX_CONV_PATH, "-mbxrd", "-dn", "-ic", "-senddate", str(dbx_path)]
    
    log(f"         Führe DbxConv aus...")
    res = run_generic_command(cmd, cwd=str(root))
    
    if not res or not mbx_temp_path.exists():
        log(f"         [FEHLER] DbxConv konnte {dbx_path.name} nicht konvertieren.")
        conversion_errors.append((dbx_path.name, "DBX Konvertierung fehlgeschlagen."))
        return

    try:
        mbx_temp_path.rename(mbox_path)
    except Exception as e:
        log(f"         [FEHLER] Rename zu .mbox fehlgeschlagen: {e}")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        mbox = mailbox.mbox(str(mbox_path))
        count = 0
        for msg in mbox:
            count += 1
            
            date_str = "0000-00-00-00-00"
            try:
                date_header = msg.get("Date")
                if date_header is not None:
                    if hasattr(date_header, '__str__') and not isinstance(date_header, str):
                        date_header = str(date_header)
                    date_obj = email.utils.parsedate_to_datetime(date_header)
                    date_str = date_obj.strftime("%Y-%m-%d-%H-%M-%S")
            except Exception as e:
                log(f"         [WARNUNG] Datum konnte nicht geparst werden: {e}")
                pass
            
            try:
                subject_header = msg.get("Subject")
                if subject_header is not None:
                    subject_str = sanitize_filename(subject_header)
                else:
                    subject_str = "Kein_Subject"
            except Exception as e:
                log(f"         [WARNUNG] Subject konnte nicht extrahiert werden: {e}")
                subject_str = "Fehlerhaftes_Subject"
            
            base_name = f"{date_str}_{subject_str}"
            
            eml_path = output_dir / f"{base_name}.eml"
            try:
                with open(eml_path, "w", encoding="utf-8", errors="replace") as f:
                    f.write(msg.as_string())
            except Exception as e:
                log(f"         [FEHLER] Konnte EML nicht speichern: {e}")
            
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
                    continue
                
                att_filename_raw = part.get_filename()
                if att_filename_raw:
                    try:
                        att_filename = sanitize_filename(att_filename_raw)
                        final_att_name = f"{base_name}_{att_filename}"
                        att_path = output_dir / final_att_name
                        
                        with open(att_path, "wb") as f:
                            f.write(part.get_payload(decode=True))
                        log(f"         [ANHANG] Extrahiert: {final_att_name}")
                    except Exception as e:
                        log(f"         [FEHLER] Anhang Fehler bei '{att_filename_raw}': {e}")
                        
        log(f"         [OK] {count} E-Mails und Anhänge aus {dbx_path.name} extrahiert.")
        
    except Exception as e:
        log(f"         [FEHLER] MBOX Parsing Fehler: {e}")
        conversion_errors.append((dbx_path.name, f"MBOX Parsing Fehler: {e}"))

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
    
    last_progress = 0.0
    while True:
        line = process.stdout.readline()
        if not line: break
        match = re.search(r'out_time_ms=(\d+)', line)
        if match:
            current_progress = min(int(match.group(1)) / (duration * 1_000_000), 1.0) if duration > 0 else 1.0
            last_progress = current_progress
            bar = "#" * int(current_progress * 40)
            sys.stdout.write(f"\r[{bar:<40}] {current_progress*100:.1f}%")
            sys.stdout.flush()

    process.wait()
    
    if process.returncode == 0 and last_progress < 1.0:
        sys.stdout.write(f"\r[{'#' * 40}] 100.0%")
        sys.stdout.flush()
        time.sleep(0.1) 

    sys.stdout.write('\r' + ' ' * 80 + '\r')
    sys.stdout.flush()
    
    if process.returncode == 0: 
        log(f"         [OK] Erfolgreich konvertiert: {os.path.basename(output_path)} Primär.")
        return True
    else:
        stderr_output = process.stderr.read()
        log(f"         [FEHLER] Konvertierung fehlgeschlagen für: {os.path.basename(input_path)}")
        if stderr_output: 
            log(f"                  FFmpeg-Fehler: {stderr_output.strip()}")
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
    
    # NEU: Definition der nativen LibreOffice-Formate
    native_lo_formats = {".odt", ".ods", ".odp", ".ott", ".ots", ".otp"}
    
    # Bestimmung des PDF-Namens
    if ext == ".pdf":
        pdf_filename = f"{name}pdf.pdf"
    elif ext in native_lo_formats:
        # Bei nativen Formaten: dateiname.pdf (kein doppeltes .odt.pdf)
        pdf_filename = f"{name}.pdf"
    else:
        # Bei Fremdfomaten: dateiname.ext.pdf
        pdf_filename = f"{name}{ext}.pdf"
        
    pdf_path = os.path.join(root, pdf_filename)
    
    # Altes PDF löschen, falls vorhanden
    if os.path.exists(pdf_path): 
        try:
            os.remove(pdf_path)
        except:
            pass

    source_for_pdf_export = ""
    
    if ext == ".pdf": 
        if is_already_pdfa(filepath):
            log(f"         [OK] Datei ist bereits PDF/A. Überspringe Konvertierung.")
            return
        source_for_pdf_export = filepath
    elif ext in native_lo_formats:
        # NEU: Kein Zwischenschritt für native Formate!
        log(f"         [INFO] Natives LibreOffice-Format erkannt. Direkter PDF/A-Export.")
        source_for_pdf_export = filepath
    else:
        # Fremdfomate brauchen den ODF-Zwischenschritt
        odf_filename = f"{name}{ext}.{target_odf_ext}"
        odf_path_target = os.path.join(root, odf_filename)
        
        if os.path.exists(odf_path_target): 
            try: os.remove(odf_path_target)
            except: pass

        log(f"         -> Schritt 1: Konvertiere zu ODF ({odf_filename})")
        
        subprocess.run([LIBREOFFICE_PATH, "--headless", "--convert-to", target_odf_ext, "--outdir", root, filepath], capture_output=True)
        
        if not any(f.startswith(name) and f.endswith(f".{target_odf_ext}") for f in os.listdir(root)) and ext == ".sdw":
            log(f"         [INFO] Standard-Filter fehlgeschlagen, erzwinge StarWriter-Import...")
            subprocess.run([LIBREOFFICE_PATH, "--headless", "--infilter=StarWriter 5.0", "--convert-to", target_odf_ext, "--outdir", root, filepath], capture_output=True)
        
        if not any(f.startswith(name) and f.endswith(f".{target_odf_ext}") for f in os.listdir(root)):
            log(f"         [INFO] Filter fehlgeschlagen, versuche .doc Auto-Detection...")
            temp_doc = os.path.join(root, f"{name}_temp.doc")
            shutil.copy2(filepath, temp_doc)
            subprocess.run([LIBREOFFICE_PATH, "--headless", "--convert-to", target_odf_ext, "--outdir", root, temp_doc], capture_output=True)
            if os.path.exists(temp_doc): os.remove(temp_doc)

        generated_files = [f for f in os.listdir(root) if f.startswith(name) and f.endswith(f".{target_odf_ext}")]
        
        if generated_files:
            best_match = os.path.join(root, generated_files[0])
            os.replace(best_match, odf_path_target)
            source_for_pdf_export = odf_path_target
        else: 
            log(f"         [WARNUNG] ODF-Erstellung fehlgeschlagen (vermutlich Draw/Impress o.ä.).")
            log(f"         [INFO] Versuche direkten PDF/A-Export aus Originaldatei (Fallback)...")
            source_for_pdf_export = filepath 
    
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
    
    if ext == ".mkv":
        try:
            v_codec = subprocess.run(
                [FFPROBE_PATH, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name", "-of", "default=noprint_wrappers=1:nokey=1", str(filepath)],
                capture_output=True, text=True, check=True
            ).stdout.strip()
            
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
        mkv_target_path = os.path.join(root, f"{filename}.mkv")
    
    log(f"         Starte Konvertierung: {filename} → {os.path.basename(mkv_target_path)}")
    
    abs_input = os.path.abspath(filepath)
    abs_output = os.path.abspath(mkv_target_path)
    if os.name == 'nt':
        abs_input = "\\\\?\\" + abs_input
        abs_output = "\\\\?\\" + abs_output

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
        ac_number_input = sys.argv[1]
        disk_archive_id_input = sys.argv[2]
        
        if len(sys.argv) >= 4:
            data_path_input = Path(sys.argv[3])
        else:
            data_path_input = Path(os.environ.get("DATA_PATH", Path.home() / "Documents/data" / ac_number_input / disk_archive_id_input))
            
    except IndexError: 
        print(f"{Fore.RED}[FEHLER] AC-Nummer und Datenträger-ID wurden nicht übergeben.{Style.RESET_ALL}")
        sys.exit(1)

    validated_paths = setup_and_validate_paths(
        ac_number_input, 
        disk_archive_id_input,
        project_base_path_override=data_path_input
    )
    
    if validated_paths:
        source_folder, LOG_FILE = validated_paths["source_folder"], validated_paths["log_file"]
        if os.path.exists(LOG_FILE): os.remove(LOG_FILE)
        LOG_FILE_HANDLE = open(LOG_FILE, "a", encoding="utf-8")
        
        log("Starte kombiniertes Konvertierungsskript.")
        
        log("\n--- Stufe 0: Suche und Entpacke DBX-Container ---")
        dbx_files = list(source_folder.rglob("*.dbx"))
        if dbx_files:
            for dbx_file in dbx_files:
                log(f"Verarbeite Container: {dbx_file.name}")
                target_dir = dbx_file.parent / f"{dbx_file.stem}_extracted"
                extract_emails_from_dbx(dbx_file, target_dir)
        else:
            log("Keine DBX-Container gefunden.")

        all_valid_extensions = SOURCE_AUDIO_EXTENSIONS.union(VALID_IMAGE_EXTENSIONS).union(VALID_TEXT_EXTENSIONS).union(SOURCE_VIDEO_EXTENSIONS)
        
        # --- DATEI-FILTER UND DERIVAT-ERKENNUNG (STRENGE LOGIK) ---
        files_to_process = []
        
        def is_derivative_of_existing_source(filepath, all_files_in_root):
            """
            Prüft, ob eine Datei ein Derivat ist, dessen Originalquelle noch im Ordner liegt.
            """
            name = filepath.stem.lower() 
            ext = filepath.suffix.lower() 
            
            target_formats = {".odt", ".ods", ".odp", ".pdf", ".mp3", ".wav", ".tiff", ".mkv"}
            if ext not in target_formats:
                return False

            for src_ext in all_valid_extensions:
                if name.endswith(src_ext):
                    potential_source_name = name 
                    for f in all_files_in_root:
                        if f.lower() == potential_source_name:
                            return True
            return False

        folder_contents = {}
        for root, _, files in os.walk(source_folder):
            folder_contents[root] = set(files)

        for root, _, files in os.walk(source_folder):
            for filename in files:
                if filename.startswith('.') or filename.startswith('~'): 
                    continue
                
                filepath = Path(root) / filename
                ext = filepath.suffix.lower()
                
                if ext not in all_valid_extensions:
                    continue
                
                if is_derivative_of_existing_source(filepath, folder_contents[root]):
                    log(f"         [SKIP] Derivat von vorhandener Quelle übersprungen: {filename}")
                    continue

                files_to_process.append(filepath)
        
        if not files_to_process: 
            log("Keine zu verarbeitenden Dateien gefunden.")
        else:
            total = len(files_to_process)
            for idx, filepath in enumerate(files_to_process, 1):
                ext = filepath.suffix.lower()
                percent = (idx / total) * 100
                
                name_part = filepath.stem
                root_dir = filepath.parent
                
                derivatives_to_clean = [
                    root_dir / f"{filepath.name}.mp3",
                    root_dir / f"{filepath.name}.wav",
                    root_dir / f"{filepath.name}.tiff",
                    root_dir / f"{filepath.name}.pdf",
                    root_dir / f"{filepath.name}.mkv"
                ]
                
                if ext in VALID_TEXT_EXTENSIONS:
                     target_odf_ext, _ = CONVERSION_MAP[ext]
                     # Nur löschen, wenn es sich um ein Fremdfomat handelt
                     if ext not in {".odt", ".ods", ".odp"}:
                         derivatives_to_clean.append(root_dir / f"{filepath.name}.{target_odf_ext}")

                for deriv in derivatives_to_clean:
                    if deriv.exists():
                        try:
                            deriv.unlink()
                            log(f"         [INFO] Altes Derivat gelöscht: {deriv.name}")
                        except Exception:
                            pass

                log(f"\n--- [{idx}/{total}] {percent:.2f}% Verarbeite '{filepath.name}' ---")
                
                if ext in SOURCE_AUDIO_EXTENSIONS: process_audio_file(filepath)
                elif ext in VALID_IMAGE_EXTENSIONS: process_image_file(filepath)
                elif ext in VALID_TEXT_EXTENSIONS: process_text_file(filepath)
                elif ext in SOURCE_VIDEO_EXTENSIONS: process_video_file(filepath)
                
            log("\n" + "="*60)
            log("VERARBEITUNG ABGESCHLOSSEN")
            log("="*60)

            if conversion_errors:
                summary = "\n🚨 ACHTUNG: Folgende Dateien konnten NICHT korrekt konvertiert werden:\n"
                summary += "!" * 70 + "\n"
                for fname, reason in conversion_errors:
                    summary += f" Datei: {fname}\n Grund: {reason}\n" + "-"*70 + "\n"
                
                print(f"{Fore.RED}{summary}{Style.RESET_ALL}")
                if LOG_FILE_HANDLE: LOG_FILE_HANDLE.write(summary)
            else:
                log("\n✅ Alle Dateien wurden erfolgreich ohne Fehler konvertiert.")

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

        log(f"📝 Detailliertes Konvertierungs-Log gespeichert unter: {LOG_FILE}")

        LOG_FILE_HANDLE.close()

        destination_folder = transfer_dir
        print("")
        if input(f"{Fore.YELLOW}Zielordner oeffnen? (j/n): {Style.RESET_ALL}").lower() == 'j':
            os.startfile(destination_folder)

    print(f"\n{Fore.CYAN}Skript beendet.{Style.RESET_ALL}")