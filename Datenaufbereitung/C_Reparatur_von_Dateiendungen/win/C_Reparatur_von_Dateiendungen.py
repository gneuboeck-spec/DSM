# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import subprocess
import json
import sys
import mimetypes
import shutil
import logging
import argparse
import zipfile
import re
from pathlib import Path
from datetime import datetime

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class Fore: GREEN = RED = YELLOW = CYAN = MAGENTA = WHITE = ""
    class Style: RESET_ALL = ""

# ==============================================================================
# 🔧 KONFIGURATION & MAPPINGS
# ==============================================================================

# Windows-Systemdateien, die keinen archivischen Wert haben und gelöscht werden können
SYSTEM_JUNK_FILES = ["IndexerVolumeGuid"]

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

format_name_to_ext_map = {
    "AppleWorks Word Processing": ".cwk", 
    "Ami Pro": ".sam"
}

# MIME-Typ-Mapping für problematische Fälle
mime_to_ext_map = {
    'application/xml': '.xml',
    'text/xml': '.xml',
    'application/rtf': '.rtf',
    'text/rtf': '.rtf',
    'application/vnd.oasis.opendocument.text': '.odt',
    'application/vnd.oasis.opendocument.spreadsheet': '.ods',
    'application/vnd.oasis.opendocument.presentation': '.odp',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
    'text/markdown': '.md',
    'text/x-markdown': '.md',
    'text/plain': '.txt',
}

# ==============================================================================
# 🔧 DYNAMISCHE PFADERMITTLUNG FÜR EXTERNE TOOLS
# ==============================================================================

def find_tool(tool_name, fallback_path):
    """Findet ein Tool im System-PATH oder nutzt den Fallback-Pfad."""
    # 1. Versuche: Tool im PATH finden
    exe_path = shutil.which(tool_name)
    if exe_path:
        return exe_path
    
    # 2. Fallback: Hardcodierter Pfad (für den alten Rechner)
    if Path(fallback_path).exists():
        return fallback_path
    
    # 3. Wenn nichts gefunden wird, gib den Fallback zurück (Skript wirft dann Fehlermeldung)
    return fallback_path

# Dynamische Zuweisung des Siegfried-Pfads
SIEGFRIED_EXE = find_tool("sf", r"C:\Program Files\Siegfried\sf.exe")

# ==============================================================================
# 🔧 LOGGING SETUP (Mit Farberhalt für die Konsole)
# ==============================================================================

class ColoredFormatter(logging.Formatter):
    """Formatter, der Log-Level in der Konsole einfärbt, aber die Nachricht (mit Emojis) intakt lässt."""
    COLORS = {
        'DEBUG': '\033[94m',      # Blau
        'INFO': '\033[92m',       # Grün
        'WARNING': '\033[93m',    # Gelb
        'ERROR': '\033[91m',      # Rot
        'CRITICAL': '\033[91m\033[1m', # Fett Rot
        'RESET': '\033[0m'
    }

    def format(self, record):
        log_msg = super().format(record)
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        return f"{color}{log_msg}{self.COLORS['RESET']}"

def setup_logging(log_file_path):
    """Konfiguriert Logging für Datei (sauber) und Konsole (farbig)."""
    logger = logging.getLogger("ExtensionRepair")
    logger.setLevel(logging.INFO)
    
    # File Handler (sauberer Text, kein ANSI-Code)
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", datefmt='%Y-%m-%d %H:%M:%S'))
    
    # Stream Handler (farbig für die Konsole)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter("[%(asctime)s] %(levelname)s: %(message)s", datefmt='%H:%M:%S'))
    
    # Verhindert doppelte Logs, falls die Funktion mehrfach aufgerufen wird
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
    return logger

# ==============================================================================
# 🔧 HILFSFUNKTIONEN
# ==============================================================================

def setup_and_validate_repair_paths(ac_number, disk_archive_id, project_base_path, logger):
    transfer_folder = project_base_path / f"3_{disk_archive_id}_for-transfer"
    
    paths = {
        "analysis_folder": transfer_folder / "files",
        "log_file": transfer_folder / f"3_{disk_archive_id}_for-transfer_repair-file-extension.log",
        "ffprobe_exec": "ffprobe.exe",
        "siegfried_exec": SIEGFRIED_EXE  # Dynamisch ermittelter Pfad
    }
    
    if not paths["analysis_folder"].is_dir(): 
        logger.error(f"Analyse-Ordner nicht gefunden: {paths['analysis_folder']}")
        return None
    if not paths["log_file"].parent.is_dir(): 
        try:
            paths["log_file"].parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            logger.error(f"Log-Ordner kann nicht erstellt werden: {paths['log_file'].parent}")
            return None
    
    if not Path(paths["siegfried_exec"]).exists(): 
        logger.error(f"Siegfried nicht gefunden unter: {paths['siegfried_exec']}")
        return None
    
    if not shutil.which(paths["ffprobe_exec"]): 
        logger.error(f"'{paths['ffprobe_exec']}' nicht im PATH gefunden.")
        return None
    
    logger.info("✅ Alle Pfade und Programme wurden erfolgreich gefunden und validiert.")
    logger.info(f"📂 Analyse-Ordner: {paths['analysis_folder']}")
    return paths

def run_command_with_json_output(command, logger):
    """Führt einen Befehl aus und gibt JSON zurück. Fängt spezifische Fehler ab."""
    try:
        process = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', check=True)
        return json.loads(process.stdout) if process.stdout else None
    except FileNotFoundError:
        logger.error(f"Programm nicht gefunden: {command[0]}")
        return None
    except subprocess.CalledProcessError as e:
        logger.error(f"Befehl fehlgeschlagen: {' '.join(command)}. Fehler: {e.stderr.strip()}")
        return None
    except json.JSONDecodeError:
        logger.error(f"Ungültige JSON-Ausgabe von: {' '.join(command)}")
        return None
    except Exception as e:
        logger.error(f"Unerwarteter Fehler bei {' '.join(command)}: {e}")
        return None

def has_video_stream(filepath, ffprobe_path):
    if not ffprobe_path: 
        return None
    command = [ffprobe_path, "-v", "error", "-show_entries", "stream=codec_type", "-select_streams", "v", "-of", "json", str(filepath)]
    result = run_command_with_json_output(command, logging.getLogger("ExtensionRepair"))
    return bool(result)

def check_opendocument_type(filepath):
    """Prüft den MIME-Typ in OpenDocument-Dateien (ZIP-Struktur)."""
    if not zipfile.is_zipfile(filepath):
        return None
    try:
        with zipfile.ZipFile(filepath, 'r') as zf:
            if 'mimetype' in zf.namelist():
                m = zf.read('mimetype').decode('utf-8').strip()
                if 'opendocument.text' in m:
                    return '.odt'
                if 'opendocument.spreadsheet' in m:
                    return '.ods'
                if 'opendocument.presentation' in m:
                    return '.odp'
    except Exception:
        pass
    return None

def check_flat_opendocument_type(filepath):
    """Prüft den MIME-Typ in Flat OpenDocument-Dateien (FODT, FODS, FODP)."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            header = f.read(8192)
            if '<office:document' in header:
                if 'office:mimetype="application/vnd.oasis.opendocument.text"' in header:
                    return '.fodt'
                if 'office:mimetype="application/vnd.oasis.opendocument.spreadsheet"' in header:
                    return '.fods'
                if 'office:mimetype="application/vnd.oasis.opendocument.presentation"' in header:
                    return '.fodp'
    except Exception:
        pass
    return None

def is_markdown_file(filepath):
    """Prüft, ob eine Datei Markdown-Syntax enthält."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(16384)
            
            # Markdown-Indikatoren
            indicators = 0
            
            # Überschriften mit # (#, ##, ###, etc.)
            if re.search(r'^#{1,6}\s+\S+', content, re.MULTILINE):
                indicators += 2
            
            # Überschriften mit Unterstreichung (=== oder ---)
            if re.search(r'^.+\n[=\-]{3,}\s*$', content, re.MULTILINE):
                indicators += 2
            
            # Fett (**text** oder __text__)
            if re.search(r'\*\*[^*\n]+\*\*', content):
                indicators += 1
            if re.search(r'__[^_\n]+__', content):
                indicators += 1
            
            # Kursiv (*text* oder _text_)
            if re.search(r'(?<!\*)\*(?!\*)([^*\n]+)(?<!\*)\*(?!\*)', content):
                indicators += 1
            
            # Links [text](url)
            if re.search(r'\[[^\]]+\]\([^)]+\)', content):
                indicators += 2
            
            # Bilder ![alt](url)
            if re.search(r'!\[[^\]]*\]\([^)]+\)', content):
                indicators += 2
            
            # Ungeordnete Listen (- oder * oder + am Zeilenanfang)
            if re.search(r'^[\-\*\+]\s+\S+', content, re.MULTILINE):
                indicators += 1
            
            # Geordnete Listen (1. 2. etc.)
            if re.search(r'^\d+\.\s+\S+', content, re.MULTILINE):
                indicators += 1
            
            # Code-Blöcke (```)
            if '```' in content:
                indicators += 2
            
            # Inline-Code (`code`)
            if re.search(r'`[^`\n]+`', content):
                indicators += 1
            
            # Blockquotes (> text)
            if re.search(r'^>\s+\S+', content, re.MULTILINE):
                indicators += 1
            
            # Horizontale Linien (---, ***, ___)
            if re.search(r'^[\-\*\_]{3,}\s*$', content, re.MULTILINE):
                indicators += 1
            
            # Tabellen (| Spalte | Spalte |)
            if re.search(r'^\|.+\|$', content, re.MULTILINE):
                indicators += 2
            
            # HTML-Tags die in Markdown üblich sind
            if re.search(r'<(br|hr|img|a|em|strong|code|pre)\b', content, re.IGNORECASE):
                indicators += 1
            
            # Mindestens 2 Indikatoren für Markdown
            return indicators >= 2
            
    except Exception:
        return False

def check_magic_bytes(filepath):
    """Prüft Magic Bytes für spezifische Dateiformate."""
    try:
        with open(filepath, 'rb') as f:
            header = f.read(16)
            
            # PSD (Adobe Photoshop) - Magic Bytes: 8BPS
            if header.startswith(b'8BPS'):
                return '.psd', 'Magic Bytes (PSD)'
            
            # FLV (Flash Video) - Magic Bytes: FLV
            if header.startswith(b'FLV'):
                return '.flv', 'Magic Bytes (FLV)'
            
    except Exception:
        pass
    return None, None

def check_musicxml(filepath):
    """Prüft, ob eine Datei MusicXML ist."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            header = f.read(8192)
            # MusicXML hat spezifische Root-Tags
            if '<score-partwise' in header or '<score-timewise' in header:
                return '.musicxml', 'MusicXML (Signatur)'
    except Exception:
        pass
    return None, None

def determine_extension_siegfried(filepath, match, ffprobe_path, logger):
    pronom_id = match.get("id")
    mime_type = match.get("mime")
    format_name = match.get("format")
    
    # 1. PRONOM ID (Manuell)
    if pronom_id in pronom_to_ext_map:
        ext = pronom_to_ext_map[pronom_id]
        # Spezielle Behandlung für ODT/ODS/ODP: Prüfe ZIP-Struktur
        if pronom_id in ['fmt/290', 'fmt/291', 'fmt/292']:
            zip_ext = check_opendocument_type(filepath)
            if zip_ext and zip_ext != ext:
                return zip_ext, f'PRONOM ID (korrigiert durch ZIP-Mimetype: {pronom_id} -> {zip_ext})'
        return ext, "PRONOM ID (Manuell)"
    
    # 2. MPEG-4 Sonderbehandlung
    if pronom_id == 'fmt/199':
        is_video = has_video_stream(filepath, ffprobe_path)
        if is_video:
            return ".mp4", "MPEG-4 (mit Video)"
        else:
            return ".m4a", "MPEG-4 (nur Audio)"
    
    # 3. MIME-Typ mit Korrekturen
    if mime_type and mime_type not in ['application/octet-stream']:
        # Bei XML-MIME-Typen: Erst Flat XML prüfen
        if mime_type in ['application/xml', 'text/xml']:
            flat_ext = check_flat_opendocument_type(filepath)
            if flat_ext:
                return flat_ext, f'MIME-Typ (korrigiert durch Flat XML: {mime_type} -> {flat_ext})'
        
        # Bei text/plain: Erst Markdown prüfen
        if mime_type == 'text/plain':
            if is_markdown_file(filepath):
                return '.md', 'MIME-Typ (korrigiert durch Markdown-Erkennung: text/plain -> .md)'
        
        # Erst unser eigenes Mapping prüfen
        if mime_type in mime_to_ext_map:
            return mime_to_ext_map[mime_type], "MIME-Typ (Manuell)"
        # Dann Standard-Mapping
        ext = mimetypes.guess_extension(mime_type)
        if ext:
            return ext, "MIME-Typ (Automatisch)"
    
    # 4. Formatname
    if format_name in format_name_to_ext_map:
        return format_name_to_ext_map[format_name], "Formatname (Manuell)"
    
    return None, None

def is_likely_text_file(filepath, threshold=0.9):
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(1024)
            if not chunk: 
                return True
            text_characters = bytes(range(32, 127)) + b'\n\r\t'
            text_count = sum(1 for byte in chunk if byte in text_characters)
            return (text_count / len(chunk)) >= threshold
    except Exception: 
        return False

def determine_text_table_extension(filepath):
    # Nur für Textdateien prüfen - binäre Dateien können kein CSV sein
    if not is_likely_text_file(filepath, threshold=0.85):
        return None, None
        
    try:
        with open(filepath, 'r', encoding='latin-1') as f:
            if f.readline(10).strip().startswith("ID;"): 
                return '.slk', 'Fallback (SYLK-Signatur)'
    except Exception: 
        pass
    
    delimiters = [';', ',', '\t', '|']
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [line.strip() for line in f.readlines(4096) if line.strip()]
            if len(lines) >= 5:  # Mindestens 5 Zeilen
                for d in delimiters:
                    counts = [line.count(d) for line in lines]
                    # Nur Zeilen mit mindestens 2 Trennzeichen zählen
                    valid_counts = [c for c in counts if c >= 2]
                    if len(valid_counts) >= 5:  # Mindestens 5 Zeilen mit >=2 Trennzeichen
                        # Prüfen, ob die Anzahl konsistent ist (alle innerhalb ±2)
                        if max(valid_counts) - min(valid_counts) <= 2:
                            return '.csv', f'Fallback (CSV-Struktur "{d}")'
    except Exception: 
        pass
    return None, None

def determine_extension_fallback(filepath, logger):
    # 1. Magic Bytes prüfen (PSD, FLV, etc.)
    magic_ext, magic_source = check_magic_bytes(filepath)
    if magic_ext:
        return magic_ext, magic_source
    
    # 2. ZIP-basierte Erkennung (OpenDocument, Office Open XML)
    if zipfile.is_zipfile(filepath):
        try:
            with zipfile.ZipFile(filepath, 'r') as zf:
                # OpenDocument MIME-Typ
                if 'mimetype' in zf.namelist():
                    m = zf.read('mimetype').decode('utf-8').strip()
                    if 'opendocument.text' in m: 
                        return '.odt', 'Fallback (ZIP-Mimetype)'
                    if 'opendocument.spreadsheet' in m: 
                        return '.ods', 'Fallback (ZIP-Mimetype)'
                    if 'opendocument.presentation' in m:
                        return '.odp', 'Fallback (ZIP-Mimetype)'
                
                # Office Open XML (docx, xlsx, pptx)
                namelist = zf.namelist()
                if any('word/' in n for n in namelist):
                    return '.docx', 'Fallback (ZIP-Struktur: word/)'
                if any('xl/' in n for n in namelist):
                    return '.xlsx', 'Fallback (ZIP-Struktur: xl/)'
                if any('ppt/' in n for n in namelist):
                    return '.pptx', 'Fallback (ZIP-Struktur: ppt/)'
        except Exception: 
            pass

    # 3. MusicXML prüfen
    musicxml_ext, musicxml_source = check_musicxml(filepath)
    if musicxml_ext:
        return musicxml_ext, musicxml_source

    # 4. Flat XML (FODT, FODS, FODP)
    flat_ext = check_flat_opendocument_type(filepath)
    if flat_ext:
        return flat_ext, f'Fallback (Flat XML: {flat_ext})'

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            header = f.read(8192)
            if '<office:document' in header:
                # Generisches Office XML
                if '<office:document-content' in header:
                    return '.xml', 'Fallback (Flat XML - Content)'
                if '<office:document-spreadsheet' in header:
                    return '.xml', 'Fallback (Flat XML - Spreadsheet)'
    except Exception: 
        pass
    
    # 5. CSV-Erkennung (streng, nur für Textdateien)
    ext, source = determine_text_table_extension(filepath)
    if ext: 
        return ext, source
    
    # 6. Markdown-Erkennung (nur für Textdateien)
    if is_likely_text_file(filepath, threshold=0.85):
        if is_markdown_file(filepath):
            return '.md', 'Fallback (Markdown-Syntax)'
    
    # 7. Plain Text
    if is_likely_text_file(filepath): 
        return '.txt', 'Fallback (Plain Text)'
        
    return None, None

# ==============================================================================
# 🚀 HAUPTLOGIK
# ==============================================================================

def parse_arguments():
    parser = argparse.ArgumentParser(description="Repariert verlorene Dateiendungen basierend auf PRONOM und Fallbacks.")
    
    # KORREKTUR: nargs="?" macht die Argumente optional, erlaubt aber die Übergabe OHNE --ac / --id Flags
    parser.add_argument("ac", nargs="?", default=None, help="AC Nummer (z.B. AC123). Falls nicht angegeben, wird interaktiv gefragt.")
    parser.add_argument("id", nargs="?", default=None, help="Disk Archive ID (z.B. DISK01). Falls nicht angegeben, wird interaktiv gefragt.")
    parser.add_argument("data_path", nargs="?", default=None, help="Datenpfad (aus menu.py übergeben).")
    parser.add_argument("--dryrun", action="store_true", help="Nur simulieren, keine Änderungen an Dateien vornehmen.")
    
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    # Interaktiver Fallback, falls keine Argumente übergeben wurden
    ac_in = args.ac or input("AC: ").strip()
    id_in = args.id or input("ID: ").strip()
    DRY_RUN = args.dryrun

    # NEU: Datenpfad aus menu.py übernehmen (sys.argv[3] oder Umgebungsvariable DATA_PATH)
    if args.data_path:
        project_root = Path(args.data_path)
    else:
        env_path = os.environ.get("DATA_PATH")
        if env_path:
            project_root = Path(env_path)
        else:
            project_root = Path.home() / "Documents/data" / ac_in / id_in

    source_stage2 = project_root / f"2_{id_in}_extracted-files" / "files"
    target_stage3 = project_root / f"3_{id_in}_for-transfer" / "files"

    # Automatischer Transfer von Stufe 2 nach Stufe 3
    if not target_stage3.exists():
        if source_stage2.exists():
            print(f"{Fore.CYAN}Vorbereitung: Kopiere Dateien von Stufe 2 nach Stufe 3...{Style.RESET_ALL}")
            try:
                shutil.copytree(source_stage2, target_stage3)
                print(f"{Fore.GREEN}[OK] Dateien erfolgreich nach Stufe 3 kopiert.{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[FEHLER] Kopieren fehlgeschlagen: {e}{Style.RESET_ALL}")
                sys.exit(1)
        else:
            print(f"{Fore.RED}Fehler: Quell-Daten in Stufe 2 nicht gefunden ({source_stage2}){Style.RESET_ALL}")
            sys.exit(1)
    
    # Logger initialisieren
    temp_log_path = target_stage3 / f"3_{id_in}_for-transfer_repair-file-extension.log"
    logger = setup_logging(temp_log_path)

    logger.info(f"Skript gestartet am {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("-" * 40)
    if DRY_RUN: 
        logger.warning("🚨 SIMULATIONSMODUS AKTIV. Es werden keine Dateien verändert.")

    # Validierung der Pfade (Übergabe des ermittelten project_root)
    config = setup_and_validate_repair_paths(ac_in, id_in, project_root, logger)
    if not config: 
        logger.error("Konfiguration fehlgeschlagen. Skript wird beendet.")
        sys.exit(1)
    
    ffprobe_path = shutil.which(config["ffprobe_exec"])

    path_obj = Path(config["analysis_folder"])
    
    # DEBUG: Zeige alle Dateien im Verzeichnis
    all_files = [p for p in path_obj.rglob('*') if p.is_file()]
    files_with_ext = [p for p in all_files if p.suffix]
    files_without_ext = [p for p in all_files if not p.name.startswith('.') and not p.suffix]
    
    logger.info(f"📊 DEBUG: {len(all_files)} Dateien insgesamt gefunden")
    logger.info(f"📊 DEBUG: {len(files_with_ext)} Dateien MIT Endung")
    logger.info(f"📊 DEBUG: {len(files_without_ext)} Dateien OHNE Endung")
    
    if files_with_ext and len(files_with_ext) <= 5:
        for f in files_with_ext[:5]:
            logger.info(f"   📄 Mit Endung: {f.name} (suffix: '{f.suffix}')")
    
    if files_without_ext and len(files_without_ext) <= 5:
        for f in files_without_ext[:5]:
            logger.info(f"   📄 Ohne Endung: {f.name}")
    
    files_to_check = files_without_ext
    
    if not files_to_check:
        logger.info("\n✅ Keine Dateien ohne Dateiendung gefunden.")
    else:
        logger.info(f"{len(files_to_check)} Datei(en) ohne Endung gefunden...\n" + "-" * 40)
        renamed_count = 0
        unidentified_count = 0
        deleted_count = 0

        for filepath in files_to_check:
            # --- System-Müll erkennen und löschen ---
            if filepath.name in SYSTEM_JUNK_FILES:
                prefix = "[SIMULATION]" if DRY_RUN else "🗑️ Gelöscht"
                logger.info(f"{prefix}: '{filepath.name}' (Windows-Systemdatei ohne archivischen Wert)")
                if not DRY_RUN:
                    try: 
                        filepath.unlink()
                        deleted_count += 1
                    except OSError as e: 
                        logger.error(f"    ❌ FEHLER beim Löschen: {e}")
                else:
                    deleted_count += 1
                continue
            
            # Siegfried-Analyse
            siegfried_result = run_command_with_json_output([config["siegfried_exec"], "-json", str(filepath)], logger)
            new_ext, source = None, None
            
            if siegfried_result and siegfried_result.get("files") and siegfried_result["files"][0].get("matches"):
                best_match = siegfried_result["files"][0]["matches"][0]
                new_ext, source = determine_extension_siegfried(filepath, best_match, ffprobe_path, logger)

            # Fallback-Logik
            if not new_ext:
                new_ext, source = determine_extension_fallback(filepath, logger)
            
            if new_ext:
                new_path = filepath.with_suffix(new_ext)
                counter = 1
                while new_path.exists():
                    new_path = filepath.parent / f"{filepath.stem}_{counter}{new_ext}"
                    counter += 1
                
                prefix = "[SIMULATION]" if DRY_RUN else "✅ Umbenannt"
                logger.info(f"{prefix}: '{filepath.name}' -> '{new_path.name}' [via {source}]")
                
                if not DRY_RUN:
                    try: 
                        filepath.rename(new_path)
                        renamed_count += 1
                    except OSError as e: 
                        logger.error(f"    ❌ FEHLER beim Umbenennen: {e}")
                else: 
                    renamed_count += 1
            else:
                fmt_name, p_id = "Unbekannt", "UNKNOWN"
                if siegfried_result and siegfried_result.get("files") and siegfried_result["files"][0].get("matches"):
                    m = siegfried_result["files"][0]["matches"][0]
                    fmt_name = m.get("format", fmt_name)
                    p_id = m.get("id", p_id)
                
                logger.warning(f"❓ Nicht zugeordnet: '{filepath.name}' (Siegfried: {fmt_name}, PRONOM: {p_id})")
                unidentified_count += 1

        logger.info("-" * 40)
        logger.info("Analyse abgeschlossen.")
        logger.info(f"Dateien {'simuliert' if DRY_RUN else 'umbenannt'}: {renamed_count}")
        logger.info(f"System-Müll {'simuliert' if DRY_RUN else 'gelöscht'}: {deleted_count}")
        logger.info(f"Nicht zugeordnet: {unidentified_count}")

    logger.info("-" * 40)
    
    # Sicheres Öffnen des Ordners am Ende
    try:
        open_q = input(f"\n{Fore.YELLOW}Analyse beendet. Zielordner öffnen? (j/n): {Style.RESET_ALL}").lower()
        if open_q == 'j':
            if sys.platform == "win32":
                os.startfile(config["analysis_folder"])
            elif sys.platform == "darwin":
                subprocess.call(["open", config["analysis_folder"]])
            else:
                subprocess.call(["xdg-open", config["analysis_folder"]])
    except Exception as e:
        logger.error(f"Konnte Ordner nicht öffnen: {e}")

if __name__ == "__main__":
    main()