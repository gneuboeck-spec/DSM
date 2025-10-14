# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import subprocess
import mailbox
import email
import re
from email.header import decode_header
from datetime import datetime
import sys

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# TEIL 1: GLOBALE KONFIGURATION FÜR ALLE KONVERTIERUNGEN
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# --- PFADE ZU DEN EXTERNEN TOOLS (FÜR MACOS) ---
libreoffice_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
imagemagick_path = "magick"
inkscape_path = "/Applications/Inkscape.app/Contents/MacOS/inkscape"
ffmpeg_path = "ffmpeg"
ffprobe_path = "ffprobe"

# --- ZU VERARBEITENDE DATEITYPEN (ANHÄNGE) ---
office_map = {
    # Textdokumente
    ".doc": ("odt", "writer_pdf_Export"), ".docx": ("odt", "writer_pdf_Export"), ".dot": ("odt", "writer_pdf_Export"), ".rtf": ("odt", "writer_pdf_Export"), ".odt": ("odt", "writer_pdf_Export"), ".ott": ("odt", "writer_pdf_Export"), ".sxw": ("odt", "writer_pdf_Export"), ".stw": ("odt", "writer_pdf_Export"), ".fodt": ("odt", "writer_pdf_Export"), ".uot": ("odt", "writer_pdf_Export"), ".wpd": ("odt", "writer_pdf_Export"), ".wps": ("odt", "writer_pdf_Export"), ".abw": ("odt", "writer_pdf_Export"), ".sdw": ("odt", "writer_pdf_Export"), ".wri": ("odt", "writer_pdf_Export"), ".html": ("odt", "writer_pdf_Export"), ".htm": ("odt", "writer_pdf_Export"), ".txt": ("odt", "writer_pdf_Export"), ".pages": ("odt", "writer_pdf_Export"),
    # ClarisWorks / AppleWorks
    ".cwk": ("odt", "writer_pdf_Export"), ".cws": ("odt", "writer_pdf_Export"),
    # Tabellen
    ".xls": ("ods", "calc_pdf_Export"), ".xlsx": ("ods", "calc_pdf_Export"), ".xlw": ("ods", "calc_pdf_Export"), ".xlt": ("ods", "calc_pdf_Export"), ".ods": ("ods", "calc_pdf_Export"), ".ots": ("ods", "calc_pdf_Export"), ".sxc": ("ods", "calc_pdf_Export"), ".stc": ("ods", "calc_pdf_Export"), ".fods": ("ods", "calc_pdf_Export"), ".uos": ("ods", "calc_pdf_Export"),
    # Präsentationen
    ".ppt": ("odp", "impress_pdf_Export"), ".pptx": ("odp", "impress_pdf_Export"), ".pps": ("odp", "impress_pdf_Export"), ".pot": ("odp", "impress_pdf_Export"), ".odp": ("odp", "impress_pdf_Export"), ".otp": ("odp", "impress_pdf_Export"), ".sxi": ("odp", "impress_pdf_Export"), ".sti": ("odp", "impress_pdf_Export"), ".fodd": ("odp", "impress_pdf_Export"), ".uop": ("odp", "impress_pdf_Export"), ".key": ("odp", "impress_pdf_Export")
}
raster_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".heic", ".gif", ".tga", ".jfif"}
vector_extensions = {".svg", ".eps", ".ai", ".pdf", ".wmf"}
audio_extensions = {".aiff", ".flac", ".ogg", ".wav", ".m4a", ".wma", ".aac", ".mp3"}
video_extensions = {".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm", ".mpg", ".mpeg", ".m4v", ".vob", ".m2ts"}

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# TEIL 2: HILFSFUNKTIONEN (PARSING, LOGGING)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def log_to_console(message):
    print(message)

def sanitize_filename(text):
    if text is None: return "Unbenannt"
    text = re.sub(r'[<>:"/\\|?*]', '_', text)
    text = re.sub(r'\s+', '_', text.strip())
    if text.startswith('.'): text = text[1:]
    return text[:100]

def parse_subject(subject_raw):
    if subject_raw is None: return "Unbenannt"
    try:
        decoded = decode_header(subject_raw)
        subject = ''.join(str(t[0], t[1] or 'latin1') if isinstance(t[0], bytes) else str(t[0]) for t in decoded)
        return sanitize_filename(subject) or "Unbenannt"
    except Exception: return "Unbenannt"

def parse_date(date_raw):
    if date_raw is None: return "0000-00-00-00-00-00"
    try:
        return email.utils.parsedate_to_datetime(date_raw).strftime("%Y-%m-%d-%H-%M-%S")
    except Exception: return "0000-00-00-00-00-00"

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# TEIL 3: KONVERTIERUNGS-FUNKTIONEN FÜR ANHÄNGE
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def convert_office_document(input_path):
    log_to_console(f"      -> Office-Dokument erkannt. Konvertiere nach PDF/A...")
    root, filename = os.path.split(input_path)
    name, ext = os.path.splitext(filename)
    ext = ext.lower()
    
    if ext not in office_map: return

    target_odf_ext, pdf_export_filter = office_map[ext]
    odf_target_path = f"{input_path}.{target_odf_ext}"
    pdf_target_path = f"{input_path}.pdf"

    if os.path.exists(odf_target_path): os.remove(odf_target_path)
    if os.path.exists(pdf_target_path): os.remove(pdf_target_path)

    modern_odf_formats = {".odt", ".ods", ".odp", ".ott", ".ots", ".otp", ".fodt", ".fods", ".fodd"}
    source_for_pdf_export = ""

    if ext in modern_odf_formats:
        source_for_pdf_export = input_path
    else:
        cmd_odf = [libreoffice_path, "--headless", "--convert-to", target_odf_ext, "--outdir", root, input_path]
        subprocess.run(cmd_odf, capture_output=True)
        real_odf_path_by_lo = os.path.join(root, f"{name}.{target_odf_ext}")
        if os.path.exists(real_odf_path_by_lo):
            os.replace(real_odf_path_by_lo, odf_target_path)
            source_for_pdf_export = odf_target_path
        else:
            log_to_console(f"      -> [FEHLER] ODF-Konvertierung für '{filename}' fehlgeschlagen.")
            return
            
    pdfa_filter_string = f"pdf:{pdf_export_filter}:SelectPdfVersion=2"
    cmd_pdf = [libreoffice_path, "--headless", "--convert-to", pdfa_filter_string, "--outdir", root, source_for_pdf_export]
    subprocess.run(cmd_pdf, capture_output=True)
    
    real_pdf_path_by_lo = os.path.join(root, f"{os.path.splitext(os.path.basename(source_for_pdf_export))[0]}.pdf")
    if os.path.exists(real_pdf_path_by_lo):
        os.replace(real_pdf_path_by_lo, pdf_target_path)
        log_to_console(f"      -> [OK] PDF/A erstellt: {os.path.basename(pdf_target_path)}")
    else:
        log_to_console(f"      -> [FEHLER] PDF/A-Export für '{filename}' fehlgeschlagen.")
    
    if source_for_pdf_export != input_path and os.path.exists(source_for_pdf_export):
        os.remove(source_for_pdf_export)

def convert_raster_image(input_path):
    log_to_console(f"      -> Rasterbild erkannt. Konvertiere nach TIFF...")
    output_path = f"{input_path}.tiff"
    if os.path.exists(output_path): os.remove(output_path)
    cmd = [imagemagick_path, input_path, output_path]
    subprocess.run(cmd, capture_output=True)
    if os.path.exists(output_path):
        log_to_console(f"      -> [OK] TIFF erstellt: {os.path.basename(output_path)}")
    else:
        log_to_console(f"      -> [FEHLER] TIFF-Erstellung für '{os.path.basename(input_path)}' fehlgeschlagen.")

def convert_vector_image(input_path):
    log_to_console(f"      -> Vektorgrafik erkannt. Konvertiere nach PDF...")
    output_path = f"{input_path}.pdf"
    if os.path.exists(output_path): os.remove(output_path)
    cmd = [inkscape_path, input_path, f"--export-filename={output_path}", "--export-text-to-path", "--export-pdf-version=1.5"]
    subprocess.run(cmd, capture_output=True)
    if os.path.exists(output_path):
        log_to_console(f"      -> [OK] Vektor-PDF erstellt: {os.path.basename(output_path)}")
    else:
        log_to_console(f"      -> [FEHLER] Vektor-PDF-Erstellung für '{os.path.basename(input_path)}' fehlgeschlagen.")

def convert_audio_file(input_path):
    log_to_console(f"      -> Audiodatei erkannt. Erstelle MP3- und/oder WAV-Version...")
    name, ext = os.path.splitext(input_path)
    ext = ext.lower()
    
    mp3_path = f"{input_path}.mp3"
    wav_path = f"{input_path}.wav"
    
    if ext not in {".mp3", ".wav"}:
        cmd_mp3 = [ffmpeg_path, "-y", "-i", input_path, "-c:a", "libmp3lame", "-q:a", "2", mp3_path]
        subprocess.run(cmd_mp3, capture_output=True)
        cmd_wav = [ffmpeg_path, "-y", "-i", input_path, "-c:a", "pcm_s16le", wav_path]
        subprocess.run(cmd_wav, capture_output=True)
        log_to_console(f"      -> [OK] MP3 und WAV erstellt.")
    elif ext == ".mp3":
        if os.path.exists(wav_path): os.remove(wav_path)
        cmd_wav = [ffmpeg_path, "-y", "-i", input_path, "-c:a", "pcm_s16le", wav_path]
        subprocess.run(cmd_wav, capture_output=True)
        log_to_console(f"      -> [OK] WAV erstellt.")
    elif ext == ".wav":
        if os.path.exists(mp3_path): os.remove(mp3_path)
        cmd_mp3 = [ffmpeg_path, "-y", "-i", input_path, "-c:a", "libmp3lame", "-q:a", "2", mp3_path]
        subprocess.run(cmd_mp3, capture_output=True)
        log_to_console(f"      -> [OK] MP3 erstellt.")
    
def convert_video_file(input_path):
    log_to_console(f"      -> Videodatei erkannt. Konvertiere nach MP4...")
    output_path = f"{input_path}.mp4"
    cmd = [ffmpeg_path, "-y", "-i", input_path, "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", output_path]
    subprocess.run(cmd, capture_output=True)
    if os.path.exists(output_path):
        log_to_console(f"      -> [OK] MP4 erstellt: {os.path.basename(output_path)}")
    else:
        log_to_console(f"      -> [FEHLER] MP4-Erstellung für '{os.path.basename(input_path)}' fehlgeschlagen.")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# TEIL 4: KERNLOGIK ZUR E-MAIL- UND ANHANG-EXTRAKTION
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def process_attachment(filepath):
    """Analysiert einen Anhang und ruft die passende Konvertierungsfunktion auf."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext in office_map:
        convert_office_document(filepath)
    elif ext in raster_extensions:
        convert_raster_image(filepath)
    elif ext in vector_extensions:
        convert_vector_image(filepath)
    elif ext in audio_extensions:
        convert_audio_file(filepath)
    elif ext in video_extensions:
        convert_video_file(filepath)

def extract_attachments(msg_obj, eml_base_name, output_dir):
    """Extrahiert Anhänge und stößt deren Konvertierung an."""
    for part in msg_obj.walk():
        if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
            continue
        attachment_filename_raw = part.get_filename()
        if attachment_filename_raw:
            attachment_filename = sanitize_filename(parse_subject(attachment_filename_raw)) or f"Anhang_{datetime.now().timestamp()}"
            final_filename = f"{eml_base_name}.{attachment_filename}"
            filepath = os.path.join(output_dir, final_filename)
            try:
                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True))
                log_to_console(f"    [ANHANG] Extrahiert: {final_filename}")
                process_attachment(filepath)
            except Exception as e:
                log_to_console(f"    [FEHLER] Anhang konnte nicht gespeichert werden: {final_filename} ({e})")

def extract_emails_to_eml(mbox_path, eml_output_dir):
    """Extrahiert E-Mails aus einer MBOX-Datei, speichert sie als EML und verarbeitet Anhänge."""
    os.makedirs(eml_output_dir, exist_ok=True)
    try:
        # Wir verwenden die Standard-Klasse 'mailbox.mbox', die in allen Python 3 Versionen verfügbar ist.
        # Der 'factory'-Parameter ist entscheidend für den Umgang mit alten Eudora-Formaten.
        mbox = mailbox.mbox(mbox_path, factory=email.message_from_binary_file)
    except Exception as e:
        log_to_console(f"[FEHLER] MBOX-Datei konnte nicht geöffnet werden: {mbox_path} ({e})")
        return

    for i, msg in enumerate(mbox):
        date = parse_date(msg.get("Date"))
        subject = parse_subject(msg.get("Subject"))
        # KORREKTUR: Der Basisname für die EML und Anhänge wird hier eindeutig generiert
        eml_base_name = f"{date}_{subject}"
        eml_filename = f"{eml_base_name}.eml"
        eml_filepath = os.path.join(eml_output_dir, eml_filename)
        
        try:
            # KORREKTUR: Speichere zuerst die EML-Datei
            with open(eml_filepath, "wb") as f:
                f.write(msg.as_bytes())
            
            # KORREKTUR: DANN verarbeite die Anhänge für DIESE E-Mail
            extract_attachments(msg, eml_base_name, eml_output_dir)
            
        except Exception as e:
            log_to_console(f"[FEHLER] EML-Datei konnte nicht gespeichert oder Anhänge konnten nicht extrahiert werden: {eml_filename} ({e})")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# TEIL 5: SKRIPT-AUSFÜHRUNG
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def process_eudora_mailboxes(input_dir):
    """
    Durchsucht einen Ordner nach Eudora Mailbox-Dateien (die oft keine Endung haben) 
    und verarbeitet sie.
    """
    log_to_console(f"--- Starte Eudora-Mailbox-Verarbeitung im Ordner: {input_dir} ---")
    
    # Eudora legt viele Hilfsdateien an, die wir ignorieren wollen.
    ignore_extensions = {".toc", ".idx", ".tmp"}
    
    for filename in os.listdir(input_dir):
        full_path = os.path.join(input_dir, filename)
        if os.path.isdir(full_path):
            continue

        _, ext = os.path.splitext(filename)

        if ext.lower() in ignore_extensions or filename.startswith('.'):
            continue

        # Annahme: Jede übrige Datei ist eine Mailbox.
        mbox_path = full_path
        
        # KORREKTUR: Der Ausgabepfad soll neben der Mailbox-Datei liegen, nicht darin.
        # Und er soll die gleiche Logik wie im DBX-Skript verwenden: MailboxName.eml
        base_name = filename.removesuffix('.mbx') if filename.lower().endswith('.mbx') else filename
        eml_dir = os.path.join(os.path.dirname(mbox_path), f"{base_name}.eml")

        log_to_console(f"\n--- Verarbeite Mailbox: {filename} ---")
        
        extract_emails_to_eml(mbox_path, eml_dir)
        
        log_to_console(f"[OK] Verarbeitung für {filename} abgeschlossen. Ergebnisse in: {eml_dir}")

if __name__ == "__main__":
    # ❗️ WICHTIG: PASSE DIESEN PFAD AN! ❗️
    # Er sollte auf den Ordner zeigen, der deine Eudora-Mailbox-Dateien enthält
    # (z.B. der "Mail Folder" aus deinem "Eudora Folder").
    main_input_dir = "/Users/gregorneuboeck/Desktop/Eudora_files" 
    
    # Erlaube die Übergabe eines Pfades als Kommandozeilenargument
    if len(sys.argv) > 1:
        main_input_dir = sys.argv[1]

    if os.path.isdir(main_input_dir):
        process_eudora_mailboxes(main_input_dir)
        log_to_console("\nAlle Prozesse abgeschlossen.")
    else:
        log_to_console(f"[FEHLER] Ungültiger Eingabepfad: '{main_input_dir}'. Bitte passen Sie die Variable 'main_input_dir' im Skript an oder übergeben Sie einen Pfad als Argument.")