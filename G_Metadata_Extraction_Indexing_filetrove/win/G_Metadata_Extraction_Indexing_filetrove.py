# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT


#!/usr/bin/env python3
import os
import sys
import csv
import hashlib
import yara
import json
import subprocess
import datetime
import re  # Für Regex-Parsing von Datumsstrings
import xml.etree.ElementTree as ET
from pathlib import Path
from mutagen import File as MutagenFile
from PyPDF2 import PdfReader
from PIL import Image, ImageCms
import chardet
import xml.dom.minidom as minidom
import zipfile
import tempfile
import shutil  # Für das Entfernen temporärer Verzeichnisse

# ==============================================================================
# 🔧 KONFIGURATION
# ==============================================================================

# --- 1. System-Pfade und Listen (manuell anpassen, falls nötig) ---
# Diese Pfade sind systemweit und bleiben als manuelle Konfiguration erhalten.
YARA_RULES_FILE = "C:\\Users\\digit\\Desktop\\Skripte\\rules.yar"
EXIFTOOL_PATH = "C:\\Program Files\\ExifTool\\exiftool.exe"
FFPROBE_PATH = "C:\\Program Files\\ffmpeg\\ffprobe.exe"
HACHOIR_METADATA_PATH = "C:\\Users\\digit\\.venv\\Scripts\\hachoir-metadata.exe"
SIEGFRIED_PATH = "C:\\Program Files\\Siegfried\\sf.exe"

# --- NEU: Globaler Speicher für Referenz-Hashes ---
REFERENCE_HASHES = {}
INTEGRITY_SUCCESS = []  # Für alle bestätigten Dateien
INTEGRITY_ERRORS = []   # Für alle Abweichungen
INTEGRITY_NEW = []      # Für neue Dateien (Derivate)

def load_reference_hashes(ac_number, disk_id):
    """Lädt Hashes aus Stufe 1 (CSV) und Stufe 2 (JSON) als Vergleichswerte."""
    refs = {}
    base_path = Path.home() / "Documents/data" / ac_number / disk_id
    
    # Pfade definieren
    stage1_csv = base_path / f"1_{disk_id}_image-LZA" / "logfiles" / f"1_{disk_id}_image-log.csv"
    stage2_json = base_path / f"2_{disk_id}_extracted-files" / f"2_{disk_id}_extracted-files_brunnhilde-summary.json"

    # 1. Stufe 1 laden (Images/Logs)
    if stage1_csv.exists():
        try:
            with open(stage1_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row.get('filename') or row.get('file')
                    sha = row.get('sha256')
                    if name and sha:
                        refs[Path(name).name.lower()] = sha.lower()
        except Exception as e:
            print(f"Warnung: Fehler beim Lesen der Stufe 1 CSV: {e}")

    # 2. Stufe 2 laden (Extrahierte Dateien)
    if stage2_json.exists():
        try:
            with open(stage2_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data.get('file_fixity_sha256', []):
                    name = Path(item.get('file')).name
                    sha = item.get('sha256')
                    if name and sha:
                        refs[name.lower()] = sha.lower()
        except Exception as e:
            print(f"Warnung: Fehler beim Lesen der Stufe 2 JSON: {e}")
    return refs

# --- 2. Funktion zur dynamischen Erstellung und Validierung der Projekt-Pfade ---
def setup_and_validate_paths(ac_number, disk_archive_id):
    """
    Erstellt und validiert die Projekt-Pfade für das Metadaten-Extraktionsskript.
    - Analyse-Verzeichnis: Stufe 4 (VL)
    - Primäre Ausgabe: Stufe 5 (LZA) / logfiles
    - Sekundäre Kopie: Stufe 4 (VL)
    """
    project_base_path = Path.home() / "Documents/data" / ac_number / disk_archive_id
    
    # Pfad zum VL-Ordner (Arbeitsverzeichnis)
    vl_folder = project_base_path / f"4_{disk_archive_id}_VL"
    
    # Pfad zum LZA-Logverzeichnis (Ausgabeverzeichnis)
    lza_log_folder = project_base_path / f"5_{disk_archive_id}_LZA" / "logfiles"
    
    # WICHTIG: Erstelle den Log-Ordner in Stufe 5, falls er noch nicht existiert
    lza_log_folder.mkdir(parents=True, exist_ok=True)

    paths = {
        # Wo das Skript nach Dateien sucht (Stufe 4)
        "base_dir": vl_folder / "files",
        
        # Wo die .index Datei primär gespeichert wird (Stufe 5)
        "output_xml": lza_log_folder / f"3_{disk_archive_id}_for-transfer.index",

        # Pfad für die zusätzliche Kopie zurück in Stufe 4
        "vl_output_xml": vl_folder / f"3_{disk_archive_id}_for-transfer.index"
    }

    # Validierung der Ordner
    if not paths["base_dir"].is_dir():
        print(f"\033[91mFehler: Der Eingabe-Ordner (VL) wurde nicht gefunden:\n{paths['base_dir']}\033[0m")
        return None
    
    # Validierung der externen Tools
    tools_to_check = { 
        "YARA Rules": YARA_RULES_FILE, 
        "ExifTool": EXIFTOOL_PATH, 
        "FFprobe": FFPROBE_PATH,
        "Hachoir": HACHOIR_METADATA_PATH, 
        "Siegfried": SIEGFRIED_PATH 
    }
    for tool_name, tool_path in tools_to_check.items():
        if not Path(tool_path).exists():
            print(f"\033[91mFehler: {tool_name} wurde nicht gefunden unter:\n{tool_path}\033[0m")
            return None

    print("\033[92mAlle Pfade (Analyse in VL, Index in LZA) wurden erfolgreich validiert.\033[0m")
    return paths

# --- 3. Haupt-Ausführungsblock zur Pfad-Initialisierung ---
# Dieser Teil wird ganz am Anfang ausgeführt, um die Pfad-Variablen zu setzen.
try:
    ac_number_input = sys.argv[1]
    disk_archive_id_input = sys.argv[2]
    print(f"Pfade werden aus Kommandozeilen-Argumenten generiert: AC={ac_number_input}, ID={disk_archive_id_input}")
    validated_paths = setup_and_validate_paths(ac_number_input, disk_archive_id_input)
except IndexError:
    print("Keine Kommandozeilen-Argumente gefunden. Bitte geben Sie die Daten manuell ein:")
    ac_number_input = input("AC-Nummer eingeben: ")
    disk_archive_id_input = input("Datenträger-ID eingeben: ")
    validated_paths = setup_and_validate_paths(ac_number_input, disk_archive_id_input)

if validated_paths:
    BASE_DIR = validated_paths["base_dir"]
    OUTPUT_XML = validated_paths["output_xml"]

    print("\nLade Referenz-Hashes aus Vorstufen (Stufe 1 & 2)...")
    REFERENCE_HASHES = load_reference_hashes(ac_number_input, disk_archive_id_input)
    print(f"-> {len(REFERENCE_HASHES)} Referenz-Werte geladen.\n")
    
    print("\nSkript wird mit folgenden Pfaden ausgeführt:")
    print(f"- Eingabe-Ordner: {BASE_DIR}")
    print(f"- Ausgabe-XML: {OUTPUT_XML}\n")
else:
    print("\nSkript wird aufgrund von Konfigurationsfehlern beendet.")
    sys.exit(1)

# Die "Schwarze Liste" aller Tags, die aus der finalen XML-Ausgabe entfernt werden sollen.
TAGS_TO_REMOVE = {
    'about', 'addaspectratioinfo', 'addoriginaldecisiondata', 'aebautocancel', 'aebsequence',
    'afareamode', 'afareaheights', 'afareawidths', 'afareaxpositions', 'afareaypositions',
    'afassistbeam', 'afduringliveview', 'afimagewidth', 'afimageheight', 'afonaelockbuttonswitch',
    'afpointinfocus', 'afpointselectionmethod', 'afpointsselected', 'api_', 'aperture',
    'aperturevalue', 'app14flags0', 'app14flags1', 'autoexposurebracketing', 'autoiso',
    'averageblacklevel', 'baseiso', 'bluebalance', 'bracketmode', 'cameraorientation',
    'cameratemperature', 'canonexposuremode', 'canonfirmwareversion', 'canonflashmode', 'canonimageheight',
    'canonimagesize', 'canonimagetype', 'canonimagewidth', 'canonmodelid', 'circleofconfusion',
    'colormap', 'colordataversion', 'colortransform', 'colortempauto', 'colortempasshot',
    'colortempcloudy', 'colortempdaylight', 'colortempflash', 'colortempfluorescent', 'colortempkelvin',
    'colortempmeasured', 'colortempshade', 'colortemptungsten', 'colortone', 'componentsconfiguration',
    'conditionalfec', 'continuousdrive', 'contrast', 'contraststandard', 'controlmode',
    'croppedimageheight', 'croppedimagewidth', 'customrendered', 'dctencodeversion', 'dialdirectiontvav',
    'directoryindex', 'documentid', 'dof', 'drivemode', 'dustremovaldata',
    'easymode', 'exifversion', 'exposurelevelincrements', 'exposuremode', 'exposureprogram',
    'exposuretime', 'fileindex', 'filenumber', 'filesource', 'flash',
    'flashactivity', 'flashbits', 'flashexposurecomp', 'flashmeteringmode', 'flashpixversion',
    'flashsyncspeedav', 'flashtype', 'fnumber', 'focusdistanceupper', 'focusdistancelower',
    'focallength', 'focalplaneresolutionunit', 'focalplanexresolution', 'focalplaneyresolution', 'focalunits',
    'focusingscreen', 'focusrange', 'fov', 'globalaltitude', 'globalangle',
    'gpsversionid', 'hasrealmergeddata', 'highisonoisereduction', 'highlighttonepriority', 'hyperfocaldistance',
    'image_orientation', 'internalserialnumber', 'interopindex', 'interopversion', 'iptcdigest',
    'isoexpansion', 'isospeedincrements', 'lens', 'lens35efl', 'lensafstopbutton',
    'lensdrivenoaf', 'lensid', 'lensmodel', 'lenstype', 'lightvalue',
    'liveviewexposuresimulation', 'liveviewshooting', 'longexposurenoisereduction', 'longexposurenoisereduction2', 'macromode',
    'make', 'maxaperture', 'maxfocallength', 'md5signature', 'measuredev',
    'measuredev2', 'measuredrggb', 'megapixels', 'meteringmode', 'minaperture',
    'minfocallength', 'mirrorlockup', 'noise', 'numafpoints', 'numslices',
    'ownername', 'photoshopformat', 'photoshopquality', 'picturestyle', 'picturestylepc',
    'picturestyleuserdef', 'printposition', 'printscale', 'printstyle', 'rawjpgsize',
    'rawmeasuredrggb', 'readername', 'recordmode', 'redbalance', 'redeyereduction',
    'safetyshift', 'saturation', 'scalefactor35efl', 'scenecapturetype', 'selftimer',
    'sensorbottomborder', 'sensorheight', 'sensorleftborder', 'sensorrightborder', 'sensortopborder',
    'sensorwidth', 'serialnumberformat', 'setbuttonwhenshooting', 'sharpnesslandscape', 'sharpnessmonochrome',
    'sharpnessportrait', 'sharpnessstandard', 'sharpnessuserdef1', 'sharpnessuserdef2', 'sharpnessuserdef3',
    'shootingmode', 'shutterbuttonafonbutton', 'shuttercurtainhack', 'shuttermode', 'shutterspeed',
    'shutterspeedvalue', 'slicesgroupname', 'spatialfrequencyresponse', 'subseccreatedate', 'subsecdatetimeoriginal',
    'subsecdigitized', 'subsecmodifydate', 'subsectime', 'subsectimeoriginal', 'superimposeddisplay',
    'targetaperture', 'targetexposuretime', 'thumbnailimagevalidarea', 'tonecurve', 'url_list',
    'userdef1picturestyle', 'userdef2picturestyle', 'userdef3picturestyle', 'validafpoints', 'wb_rggblevels',
    'wb_rggblevelsauto', 'wb_rggblevelsasshot', 'wb_rggblevelscloudy', 'wb_rggblevelsdaylight', 'wb_rggblevelsflash',
    'wb_rggblevelsfluorescent', 'wb_rggblevelskelvin', 'wb_rggblevelsmeasured', 'wb_rggblevelsshade', 'wb_rggblevelstungsten',
    'wbbracketmode', 'writername', 'ycbcrpositioning',
}

# Sicherstellen, dass die YARA-Regeln existieren, bevor sie kompiliert werden
if not Path(YARA_RULES_FILE).exists():
    print(f"Fehler: YARA-Regeldatei nicht gefunden unter {YARA_RULES_FILE}")
    sys.exit(1)

try:
    rules = yara.compile(filepath=str(YARA_RULES_FILE))
except yara.Error as e:
    print(f"Fehler beim Kompilieren der YARA-Regeln: {e}")
    sys.exit(1)

root = ET.Element("filetrove")

# Hilfsfunktion zum Parsen und Formatieren von Datumsstrings
def format_date_to_iso(date_str):
    if not date_str:
        return None
    # ISO 8601 ist bereits gut
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?([Z+\-]\d{2}(:?\d{2})?)?', date_str):
        return date_str

    # ExifTool Format: YYYY:MM:DD HH:MM:SS
    match_exif = re.match(r'(\d{4}):(\d{2}):(\d{2}) (\d{2}):(\d{2}):(\d{2})', date_str)
    if match_exif:
        try:
            dt_obj = datetime.datetime(
                int(match_exif.group(1)), int(match_exif.group(2)), int(match_exif.group(3)),
                int(match_exif.group(4)), int(match_exif.group(5)), int(match_exif.group(6))
            )
            return dt_obj.isoformat()
        except ValueError:
            pass

    # PDF Format: D:YYYYMMDDHHMMSS[Z|+HH'MM'|-HH'MM']
    match_pdf = re.match(r"D:(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})([Z+-]\d{2}'?\d{2}'?)?", date_str)
    if match_pdf:
        try:
            year, month, day, hour, minute, second = map(int, match_pdf.groups()[:6])
            dt_obj = datetime.datetime(year, month, day, hour, minute, second)
            # Vereinfachte Zeitzonenbehandlung, da datetime.fromisoformat flexibler ist
            # und komplexere Zeitzonen-Strings hier kompliziert werden könnten.
            # Hier konzentrieren wir uns auf die Konvertierung des Datums selbst.
            pass  # Für jetzt ignorieren wir detailliertes Zeitzonen-Parsing
            return dt_obj.isoformat()
        except ValueError:
            pass

    # Versuche generisches Parsing als letzte Instanz
    try:
        # Ersetze Z für UTC und entferne Apostrophe für fromisoformat Kompatibilität
        dt_obj = datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00").replace("'", ""))
        return dt_obj.isoformat()
    except ValueError:
        pass

    return date_str  # Wenn alles fehlschlägt, den Originalstring zurückgeben


def hash_sha256(filepath):
    h = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        print(f"Fehler beim SHA256-Hashing von {filepath}: {e}")
        return "error_hashing"


def run_command(command, env=None, stream_output=False):
    """
    Führt einen Shell-Befehl aus und gibt stdout, stderr und den Return Code zurück.
    Akzeptiert optional ein 'env'-Dictionary für Umgebungsvariablen.
    Wenn stream_output True ist, wird stdout/stderr direkt an die Konsole gestreamt.
    """
    stdout_target = sys.stdout if stream_output else subprocess.PIPE
    stderr_target = sys.stderr if stream_output else subprocess.PIPE
    try:
        result = subprocess.run(command, stdout=stdout_target, stderr=stderr_target, text=True, check=False, env=env, encoding='utf-8', errors='replace', shell=True)
        return result.stdout, result.stderr, result.returncode
    except FileNotFoundError:
        print(f"Fehler: Befehl nicht gefunden: '{command[0]}'. Stellen Sie sicher, dass das Tool installiert und im PATH verfügbar ist.")
        return "", f"Befehl nicht gefunden: '{command[0]}'", -1
    except Exception as e:
        print(f"Unerwarteter Fehler beim Ausführen von Befehl '{' '.join(command)}': {e}")
        return "", str(e), -1


def extract_metadata_exiftool(filepath):
    if not Path(EXIFTOOL_PATH).exists():
        print(f"ExifTool nicht gefunden, Extraktion wird übersprungen.")
        return {}
    stdout, stderr, returncode = run_command([str(EXIFTOOL_PATH), "-j", str(filepath)])
    if returncode != 0:
        print(f"ExifTool Fehler (Return Code {returncode}) für {filepath}: {stderr}")
        return {}
    try:
        data = json.loads(stdout)[0]
        unwanted = {
            "SourceFile", "Directory", "FileName", "FileSize", "FileModifyDate",
            "FileAccessDate", "FileInodeChangeDate", "FilePermissions",
            "FileType", "FileTypeExtension", "MIMEType"
        }
        metadata = {}
        for k, v in data.items():
            if k not in unwanted and v not in (None, ""):
                # ExifTool-Schlüssel werden hier nicht mehr direkt in Kleinbuchstaben umgewandelt,
                # da die Standardisierung jetzt in unify_metadata_keys erfolgt.
                # 'creation-date' wird hier nicht speziell behandelt, da es in unify_metadata_keys gemappt wird.
                metadata[k] = str(v)
        return metadata
    except json.JSONDecodeError as e:
        print(f"Fehler beim Parsen der ExifTool JSON-Ausgabe für {filepath}: {e}. Output: {stdout[:200]}...")
        return {}
    except Exception as e:
        print(f"Fehler bei ExifTool für {filepath}: {e}")
        return {}


def extract_metadata_ffprobe(filepath):
    if not Path(FFPROBE_PATH).exists():
        print(f"FFprobe nicht gefunden, Extraktion wird übersprungen.")
        return {}
    stdout, stderr, returncode = run_command([str(FFPROBE_PATH), "-v", "quiet", "-print_format", "json",
                                              "-show_format", "-show_streams", str(filepath)])
    if returncode != 0:
        # FFprobe gibt oft einen Nicht-Null-Code für Nicht-Mediendateien zurück, das ist normal.
        # Wir prüfen, ob es eine Fehlermeldung gibt, die auf ein echtes Problem hindeutet.
        if "No such file or directory" in stderr or "Invalid data found when processing input" in stderr:
            print(f"FFprobe Fehler (Return Code {returncode}) für {filepath}: {stderr}")
        else:
            # Für Nicht-Mediendateien ist ein leerer Output normal
            pass
        return {}

    try:
        data = json.loads(stdout)
        fmt = data.get("format", {})
        skip_keys = {"filename", "nb_streams", "nb_programs", "format_name", "format_long_name"}
        return {
            f"ffprobe_format_{k}": str(v)
            for k, v in fmt.items()
            # 'size' von ffprobe-Ausgabe explizit ausschließen, da es redundant mit os.stat() ist
            # und bereits von 'get_file_info' für Genauigkeit und Konsistenz behandelt wird.
            if isinstance(v, (str, int, float)) and k not in skip_keys and k.lower() != 'size'
        }
    except json.JSONDecodeError as e:
        print(f"Fehler beim Parsen der FFprobe JSON-Ausgabe für {filepath}: {e}. Output: {stdout[:200]}...")
        return {}
    except Exception as e:
        print(f"Fehler bei FFprobe für {filepath}: {e}")
        return {}


def extract_metadata_hachoir(filepath):
    if not Path(HACHOIR_METADATA_PATH).exists():
        print(f"Hachoir-Metadaten nicht gefunden, Extraktion wird übersprungen.")
        return {}

    try:
        stdout, stderr, returncode = run_command([str(HACHOIR_METADATA_PATH), "--json", str(filepath)])
        if returncode != 0:
            print(f"Hachoir Fehler (Return Code {returncode}) für {filepath}: {stderr}")
            return {}
        try:
            # Alle Schlüssel in Kleinbuchstaben umwandeln
            data = json.loads(stdout)
            return {k.lower(): str(v) for k, v in data.items()}
        except json.JSONDecodeError as e:
            print(f"Fehler beim Parsen der Hachoir JSON-Ausgabe für {filepath}: {e}. Output: {stdout[:200]}...")
            return {}
        except Exception as e:
            print(f"Fehler bei Hachoir für {filepath}: {e}")
            return {}
    except FileNotFoundError:
        print(f"Hachoir-Metadaten nicht gefunden, Hachoir-Extraktion wird übersprungen.")
        return {}


def extract_pdf_info(filepath):
    try:
        reader = PdfReader(filepath)
        # Die PDF-Version ist jetzt Teil der Metadaten, nicht mehr ein separates Attribut
        pdf_info = {
            "pdf_num_pages": str(len(reader.pages))
        }
        doc_info = reader.metadata
        if doc_info:
            # Die PDF-Version wird hier aus den Metadaten geholt
            if doc_info.get('/Producer'):
                # Heuristik: Oft enthält der Producer-String die Version.
                # Eine direktere Methode gibt es in neueren Versionen nicht immer.
                # ExifTool ist hier zuverlässiger, dies ist ein Fallback.
                pass # Wir verlassen uns auf ExifTool, das zuverlässiger ist.

            if '/Keywords' in doc_info:
                pdf_info['document_keywords'] = str(doc_info['/Keywords'])
            if '/CreationDate' in doc_info:
                pdf_info['asset_created_date'] = format_date_to_iso(str(doc_info['/CreationDate']))
            if '/ModDate' in doc_info:
                pdf_info['asset_modified_date'] = format_date_to_iso(str(doc_info['/ModDate']))
            if '/Creator' in doc_info:
                pdf_info['pdf_creator'] = str(doc_info['/Creator'])
            if '/Producer' in doc_info:
                pdf_info['pdf_producer'] = str(doc_info['/Producer'])

        return pdf_info
    except Exception as e:
        print(f"Fehler beim Extrahieren von PDF-Info für {filepath}: {e}")
        return {}


def extract_mutagen_info(filepath):
    mutagen_data = {}
    try:
        # Lade die Datei ohne den 'easy'-Modus, um auf technische Metadaten (audio.info) zugreifen zu können
        audio = MutagenFile(filepath)
        if not audio:
            return {}

        # 1. Extrahiere technische Metadaten aus dem 'info'-Attribut (wichtig für WAV, AIFF etc.)
        if hasattr(audio, 'info') and audio.info:
            if hasattr(audio.info, 'sample_rate') and audio.info.sample_rate:
                mutagen_data['samplerate'] = str(audio.info.sample_rate)
            if hasattr(audio.info, 'channels') and audio.info.channels:
                mutagen_data['audio_channels'] = str(audio.info.channels)
            if hasattr(audio.info, 'bits_per_sample') and audio.info.bits_per_sample:
                mutagen_data['audio_bits_per_sample'] = str(audio.info.bits_per_sample)
            if hasattr(audio.info, 'length') and audio.info.length:
                mutagen_data['duration'] = str(audio.info.length)

        # 2. Versuche, Tag-basierte Metadaten zu extrahieren (funktioniert für MP3, FLAC etc.)
        # Dies kann auch für AIFF funktionieren, wenn es ID3-Tags enthält.
        if hasattr(audio, 'tags') and audio.tags:
            # audio.items() funktioniert für viele Tag-Formate
            for k, v in audio.items():
                # Verhindere das Überschreiben bereits extrahierter technischer Daten
                if k.lower() not in mutagen_data:
                    mutagen_data[k.lower()] = str(v)

            # Spezifische Behandlung für Keywords/Genre
            if 'genre' in audio and isinstance(audio['genre'], list):
                mutagen_data['document_keywords'] = ", ".join(str(g).strip() for g in audio['genre'] if str(g).strip())

    except Exception as e:
        # Hier einen informativeren Fehler ausgeben, anstatt ihn zu ignorieren
        print(f"Info: Fehler beim Extrahieren von Mutagen-Info für {filepath} (könnte für diesen Dateityp normal sein): {e}")
        pass  # Fehler ignorieren und mit den bisher gesammelten Daten fortfahren oder leeres Dict zurückgeben

    return mutagen_data


def extract_image_info(filepath):
    # NEU: Prüfen, ob es eine SVG-Datei ist. Wenn ja, Pillow gar nicht erst versuchen.
    if str(filepath).lower().endswith('.svg'):
        # Für SVGs verlassen wir uns auf ExifTool, das diese besser verarbeiten kann.
        # Pillow würde hier einen Fehler werfen.
        return {}
        
    try:
        with Image.open(filepath) as img:
            width, height = img.width, img.height
            info = {
                "image_mode": img.mode,
                "image_width": str(width),
                "image_height": str(height)
            }
            if hasattr(img, "_getexif") and img._getexif():
                orientation = img._getexif().get(0x0112)
                if orientation:
                    info["image_orientation"] = str(orientation)
            if "icc_profile" in img.info:
                try:
                    icc = ImageCms.ImageCmsProfile(img.info.get("icc_profile"))
                    desc = ImageCms.getProfileDescription(icc)
                    if desc:
                        info["image_icc_profile_description"] = desc
                except Exception:
                    pass
            return info
    except Exception as e:
        print(f"Fehler beim Extrahieren von Bild-Info für {filepath}: {e}")
        return {}


def run_siegfried(filepath):
    if not Path(SIEGFRIED_PATH).exists():
        print(f"Siegfried nicht gefunden, Extraktion wird übersprungen.")
        return {}

    stdout, stderr, returncode = run_command([str(SIEGFRIED_PATH), "-json", str(filepath)])  # Changed -j to -json
    if returncode != 0:
        print(f"Siegfried Fehler (Return Code {returncode}) für {filepath}: {stderr}")
        return {}
    try:
        result = json.loads(stdout)
        if result and result.get("files") and result["files"][0].get("matches"):
            match = result["files"][0]["matches"][0]
            return {
                "pronom_id": match.get("id", ""),
                "note": match.get("format", ""),  # Siegfried's Formatname (z.B. "Portable Document Format")
                "format_version": match.get("version", ""),
                "mime_type": match.get("mime", "")  # Siegfried's MIME-Typ (z.B. "Portable Document Format")
            }
    except json.JSONDecodeError as e:
        print(f"Fehler beim Parsen der Siegfried JSON-Ausgabe für {filepath}: {e}. Output: {stdout[:200]}...")
        return {}
    except Exception as e:
        print(f"Fehler bei Siegfried für {filepath}: {e}")
        pass
    return {}
def extract_sam_specific(filepath):
    try:
        with open(filepath, "rb") as f:
            raw = f.read(8192)
        encoding_result = chardet.detect(raw)
        encoding = encoding_result["encoding"] or "utf-8"

        # Um Dekodierungsfehler zu vermeiden, insbesondere bei großen Dateien
        # oder nicht-Standard-Kodierungen, lesen wir nur einen kleinen Teil
        # oder verwenden errors="replace".
        try:
            text = raw.decode(encoding, errors="replace")
            lines = text.splitlines()
            # Der Schlüssel "sam_encoding" wurde hier entfernt
            return {
                "sam_line_count": str(len(lines)),
                "sam_sample_text": "\n".join(lines[:10])
            }
        except Exception:
            # Falls Dekodierung fehlschlägt, versuchen wir es mit einer anderen Kodierung
            text = raw.decode("latin-1", errors="replace")  # Fallback
            lines = text.splitlines()
            # Der Schlüssel "sam_encoding" wurde auch hier entfernt
            return {
                "sam_line_count": str(len(lines)),
                "sam_sample_text": "\n".join(lines[:10])
            }
    except Exception as e:
        print(f"Fehler beim Extrahieren von SAM-info für {filepath}: {e}")
        return {}


def extract_musicxml_info(filepath):
    """
    Extrahiert Metadaten aus einer MusicXML (.mxl) Datei.
    .mxl Dateien sind gezippte MusicXML Dateien.
    """
    metadata = {}
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        musicxml_file = None
        # Versuche, zuerst gängige MusicXML-Dateinamen zu finden
        for common_name in ["score.xml", "part1.xml", "music.xml"]:
            if (Path(temp_dir) / common_name).exists():
                musicxml_file = Path(temp_dir) / common_name
                break

        # Falls nicht gefunden, finde die größte .xml Datei
        if not musicxml_file:
            xml_files = list(Path(temp_dir).glob('**/*.xml'))
            if xml_files:
                musicxml_file = max(xml_files, key=lambda f: f.stat().st_size)

        if musicxml_file and musicxml_file.exists():
            tree = ET.parse(musicxml_file)
            root_xml = tree.getroot()

            # Extrahiere spezifische MusicXML Tags
            # MusicXML verwendet oft einen Standard-Namespace.
            # Wir versuchen, Elemente ohne explizites Namespace-Präfix zu finden,
            # was oft mit ET.find für Standard-Namespaces funktioniert.

            # document_creator_tool (vom <software> Tag)
            software_elem = root_xml.find(".//identification/encoding/software")
            if software_elem is not None and software_elem.text:
                metadata['score_partwiseidentificationencodingsoftware'] = software_elem.text.strip()

            # document_title (vom <movement-title> Tag)
            movement_title_elem = root_xml.find(".//movement-title")
            if movement_title_elem is not None and movement_title_elem.text:
                metadata['score_partwisemovement_title'] = movement_title_elem.text.strip()

            # document_rights (vom <rights> Tag)
            rights_elem = root_xml.find(".//identification/rights")
            if rights_elem is not None and rights_elem.text:
                metadata['score_partwiseidentificationrights'] = rights_elem.text.strip()

            # document_encoding_date (vom <encoding-date> Tag)
            encoding_date_elem = root_xml.find(".//identification/encoding/encoding-date")
            if encoding_date_elem is not None and encoding_date_elem.text:
                # Formatierung hier, bevor es in all_raw_metadata geht
                metadata['document_encoding_date'] = format_date_to_iso(encoding_date_elem.text.strip())

            # document_author (vom <creator type="composer"> oder generischen <creator> Tag)
            creators = root_xml.findall(".//identification/creator")
            composer_names = []
            for creator in creators:
                if creator.text and (creator.get('type') == 'composer' or creator.get('type') is None):
                    composer_names.append(creator.text.strip())
            if composer_names:
                metadata['score_partwiseidentificationcreator'] = ", ".join(composer_names)

    except zipfile.BadZipFile:
        print(f"Fehler: {filepath} ist keine gültige ZIP-Datei (MusicXML Archiv).")
    except ET.ParseError as e:
        print(f"Fehler beim Parsen der MusicXML-Datei in {filepath}: {e}")
    except Exception as e:
        print(f"Unerwarteter Fehler beim Extrahieren der MusicXML-info für {filepath}: {e}")
    finally:
        if temp_dir and Path(temp_dir).exists():
            try:
                shutil.rmtree(temp_dir)  # Temporäres Verzeichnis bereinigen
            except Exception as e:
                print(f"Konnte temporäres Verzeichnis {temp_dir} nicht löschen: {e}")
    return metadata


def get_file_info(path):
    try:
        stat = path.stat()
        return {
            "size": str(stat.st_size),
            "filesystem_created_date": datetime.datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "filesystem_modified_date": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "filesystem_accessed_date": datetime.datetime.fromtimestamp(stat.st_atime).isoformat()
        }
    except Exception as e:
        print(f"Fehler beim Abrufen von Dateisystem-Infos für {path}: {e}")
        return {
            "size": "unknown",
            "filesystem_created": "unknown",
            "filesystem_modified": "unknown",
            "filesystem_accessed": "unknown"
        }

def sanitize_tag(tag):
    # Ersetzt Leerzeichen, Doppelpunkte, Bindestriche und Punkte durch Unterstrich
    tag = tag.replace(" ", "_").replace(":", "_").replace("-", "_").replace(".", "_").replace("/", "_")
    # Entfernt alle Zeichen, die keine alphanumerischen Zeichen oder Unterstrich sind
    return ''.join(c for c in tag if c.isalnum() or c == "_").lower()

def sanitize_for_xml(text):
    """
    Entfernt ungültige XML 1.0-Steuerzeichen aus einem String, um 'ExpatError' zu verhindern.
    Diese Version ist robuster und entfernt mehr bekannte ungültige Zeichenbereiche.
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Regex, die die meisten ungültigen XML-Steuerzeichen (C0 und C1-Blöcke) abdeckt.
    # Gültig sind: 0x09 (Tab), 0x0A (LF), 0x0D (CR).
    # Ungültig sind: 0x00-0x08, 0x0B-0x0C, 0x0E-\x1F, sowie 0x7F-\x9F.
    invalid_xml_char_pattern = re.compile(
        r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]'
    )
    
    return invalid_xml_char_pattern.sub('', text)
def is_likely_software_tool(value):
    """
    Prüft heuristisch, ob ein Wert wahrscheinlich ein Software-Tool ist und KEIN Personen- oder Institutionsname.
    Gibt True zurück, wenn es wahrscheinlich ein Tool ist, andernfalls False.
    """
    if not isinstance(value, str) or not value.strip():
        return False  # Ist kein String oder ist leer

    # REGEL 1: Starke Indikatoren für Software (sofortiges Ergebnis: JA)
    # Enthält version-ähnliche Nummern, Pfadtrenner oder technische Zeichen
    if re.search(r'\d[.-]\d', value) or any(c in value for c in ['/', '\\', '(', ')', ';', '_', '[', ']']):
        return True

    # Enthält typische Software-Schlüsselwörter (Groß-/Kleinschreibung egal)
    lower_value = value.lower()
    software_indicators = [
        'adobe', 'microsoft', 'apple', 'libreoffice', 'corel', 'version', 'macos',
        'sdk', 'api', 'toolkit', 'project', 'library', 'gimp', 'canon', 'phase one',
        'nikon', 'sony', 'exiftool', 'ffmpeg', 'framework', 'prince', 'windows',
        'scribus', 'cairo', 'writer', 'calc', 'impress', 'word', 'excel', 'inc.',
        'powerpoint', 'ltd.', 'corp.', 'gmbh', 'ag'
    ]
    if any(indicator in lower_value for indicator in software_indicators):
        return True

    # Enthält eine Ziffer (z.B. in "Word2016", "Acrobat 9")
    if re.search(r'\d', value):
        return True

    # REGEL 2: Starke Indikatoren für Namen/Institutionen (sofortiges Ergebnis: NEIN)
    # Enthält kleine Bindewörter, die in Produktnamen extrem selten sind.
    words = value.split()
    if any(word.lower() in {'im', 'in', 'der', 'die', 'das', 'the', 'of', 'at'} for word in words):
        return False

    # Wenn der String mehr als 4 Wörter hat, ist es wahrscheinlich ein Satz/eine Beschreibung.
    if len(words) > 4:
        return False

    # STANDARDANNAHME: Wenn keine Software-Merkmale gefunden wurden, ist es KEIN Tool.
    return False


def unify_metadata_keys(metadata: dict) -> dict:
    """
    Vereinheitlicht Metadaten-Schlüssel, um Redundanzen zu reduzieren und Konsistenz zu gewährleisten.
    """
    # Blockliste für standardisierte Schlüssel, die immer entfernt werden sollen.
    # Diese Liste enthält nun explizit alle von Ihnen genannten, nicht gemappten 'score_partwise'-Felder.
    always_remove_standardized_keys = {
        # Redundante und unerwünschte Tags
        '_temp_bit_depth', 'about', 'addaspectratioinfo', 'addoriginaldecisiondata', 'api_',
    'aebautocancel', 'aebsequence', 'afareamode', 'afareaheights', 'afareawidths',
    'afareaxpositions', 'afareaypositions', 'afassistbeam', 'afduringliveview',
    'afimagewidth', 'afimageheight', 'afonaelockbuttonswitch', 'afpointinfocus',
    'afpointselectionmethod', 'afpointsselected', 'alphachannelsnames', 'app14flags0',
    'app14flags1', 'application', 'applicationname', 'applicationsuppliername',
    'applicationversionnumber', 'applicationversionstring', 'appversion', 'aperture',
    'aperturevalue', 'artist', 'artisturl', 'aspectratio', 'aspectratiox',
    'aspectratioy', 'audiocodecdescription', 'audiolayer', 'audiovendorid',
    'audio_sample_count', 'audiosamplecount', 'audiostreamtype', 'autobracketing',
    'autoexposurebracketing', 'autoiso', 'averageblacklevel', 'averagebytespersecond',
    'avgbytespersec', 'baseiso', 'bitsperpixel', 'bitspersample', 'blockalign',
    'blocksizemin', 'blocksizemax', 'bluebalance', 'boundingbox', 'bpm_beats_per_minute',
    'bpmbeatsperminute', 'bracketmode', 'brain', 'byteordermark', 'bytes',
    'cameratemperature', 'cameratype', 'cameraorientation', 'canonexposuremode',
    'canonfirmwareversion', 'canonflashmode', 'canonimageheight', 'canonimagesize',
    'canonimagetype', 'canonimagewidth', 'canonmodelid', 'channelmode',
    'chromaticadaptation', 'circleofconfusion', 'closedgopindicator', 'cmmflags',
    'codecid', 'codepage', 'colordataversion', 'colormode', 'colorcomponents',
    'colorsiting', 'colorspace', 'colortempasshot', 'colortempauto', 'colortempcloudy',
    'colortempdaylight', 'colortempflash', 'colortempfluorescent', 'colortempkelvin',
    'colortempmeasured', 'colortempshade', 'colortemptungsten', 'colortemperature',
    'colortone', 'colortransform', 'columncount', 'comment', 'comments',
    'commercialurl', 'comm__eng', 'comm_eng', 'comm_id3v1_comment_eng',
    'comm_musicmatch_bio_eng', 'company', 'compatible_brands', 'compatiblebrands',
    'componentdatadefinition', 'componentdepth', 'componentsconfiguration',
    'compobjusertypelen', 'conditionalfec', 'conformance', 'connectionspaceilluminant',
    'containerlastmodifydate', 'continuousdrive', 'contrast', 'contraststandard',
    'controlmode', 'copy_status_version', 'copyrightflag', 'creation_time', 'croparea',
    'croppedimageheight', 'croppedimagewidth', 'currenttime', 'currentuser',
    'customrendered', 'datapackets', 'dctencodeversion', 'delimiter', 'derivedfromdocumentid',
    'derivedfrominstanceid', 'deviceattributes', 'devicemodel', 'devicemodeldesc',
    'devicemanufacturer', 'devicemfgdesc', 'dialdirectiontvav', 'directoryindex',
    'displayedunitsx', 'displayedunitsy', 'doctype', 'doctypereadversion',
    'doctypeversion', 'documentid', 'document_headingpairs', 'document_statisticcell_count',
    'document_statisticobject_count', 'document_statistictable_count',
    'document_titleofparts', 'dof', 'drivemode', 'dropframe', 'dustremovaldata',
    'easymode', 'ebmlreadversion', 'ebmlversion', 'editrate', 'encodedby',
    'encodingprocess', 'error_correction_type', 'errorcorrectiontype',
    'essencestreamid', 'exifbyteorder', 'exiftoolversion', 'exifversion',
    'exposurelevelincrements', 'exposuremode', 'exposureprogram', 'exposuretime',
    'exposurewarning', 'ffprobe_format_probe_score', 'ffprobe_format_start_time',
    'filecreatedate', 'fileid', 'fileindex', 'filelength', 'filenumber', 'filesfilename',
    'filesfilerelativepath', 'filesfilesha256', 'filesfiletype', 'filesfilevalid',
    'filesizebytes', 'filesource', 'fill', 'fillorder', 'filter', 'firmwareversion',
    'flags', 'flash', 'flashactivity', 'flashbits', 'flashexposurecomp',
    'flashmeteringmode', 'flashpixversion', 'flashsyncspeedav', 'flashtype', 'fnumber',
    'focaldistance', 'focusdistance', 'focallength', 'focallength35efl',
    'focalplaneresolutionunit', 'focalplanexresolution', 'focalplaneyresolution',
    'focalunits', 'focusdistanceupper', 'focusdistancelower', 'focusmode',
    'focusrange', 'focuswarning', 'focusingscreen', 'fontfamily', 'fontfamily_en_us',
    'fontname', 'fontname_en_us', 'fontsubfamily', 'fontsubfamily_da',
    'fontsubfamily_de_de', 'fontsubfamily_en_us', 'fontsubfamily_es_es',
    'fontsubfamily_fi', 'fontsubfamily_fr_ca', 'fontsubfamily_fr_fr', 'fontsubfamily_it_it',
    'fontsubfamily_nl_nl', 'fontsubfamily_no_no', 'fontsubfamily_pt_pt',
    'fontsubfamily_sv_se', 'fontsubfamilyid', 'fontsubfamilyid_en_us', 'fonttype',
    'fov', 'framecount', 'framesizemin', 'framesizemax', 'fujiflashmode', 'fullname',
    'globalaltitude', 'globalangle', 'gpsversionid', 'graphicsmode', 'greenmatrixcolumn',
    'greentrc', 'handler_name', 'handlerclass', 'handlerdescription', 'handlername',
    'handlertype', 'handlervendorid', 'hascolormap', 'hasrealmergeddata', 'headingpairs',
    'highisonoisereduction', 'highlighttonepriority', 'horizontalsubsampling',
    'htmlelementsclasses', 'htmlelementsids', 'htmlelementstags', 'hyperfocaldistance',
    'hyperlinkschanged', 'id', 'id3size', 'image_icc_profile_description',
    'image_orientation', 'imagesize', 'indexstreamid', 'instanceid', 'intensitystereo',
    'interlace', 'internalserialnumber', 'internalversionnumber', 'interopindex',
    'interopversion', 'iptcdigest', 'isfallback', 'isfixedpitch', 'iso',
    'isoexpansion', 'isospeedincrements', 'italicangle', 'layerblendmodes', 'layercount',
    'layernames', 'layeropacities', 'layerrectangles', 'layervisible', 'lens',
    'lens35efl', 'lensafstopbutton', 'lensdrivenoaf', 'lensid', 'lensmodel',
    'lenstype', 'lightvalue', 'linearized', 'linkedtrackid', 'linksuptodate',
    'liveviewexposuresimulation', 'liveviewshooting', 'localeindicator',
    'lockedindicator', 'longexposurenoisereduction', 'longexposurenoisereduction2',
    'lowdelayindicator', 'luminance', 'lyrics', 'macro', 'major_brand', 'majorbrand',
    'make', 'makeandmodel', 'manifestlinkform', 'manifestplacedxresolution',
    'manifestplacedyresolution', 'manifestplacedresolutionunit', 'manifestreferenceinstanceid',
    'manifestreferencedocumentid', 'matrixstructure', 'maxaperture', 'maxfocallength',
    'maximumgopsize', 'maxpacketsize', 'mcdi', 'measuredev', 'measuredev2',
    'measuredrggb', 'measurementbacking', 'measurementflare', 'measurementilluminant',
    'measurementobserver', 'mediablackpoint', 'mediabox', 'mediadataoffset',
    'mediatimescale', 'mediawhitepoint', 'megapixels', 'meteringmode', 'minaperture',
    'minfocallength', 'minor_version', 'minorversion', 'minpacketsize', 'mirrorlockup',
    'model', 'modeextension', 'mpegaudioversion', 'msstereo', 'muxingapp', 'mxfversion',
    'nametableversion', 'nametableversion_en_us', 'nativedisplayinfo', 'nexttrackid',
    'noise', 'nominalbitrate', 'notes', 'notice', 'numafpoints', 'numcolors',
    'numimportantcolors', 'numslices', 'numsampleframes', 'objectmodelversion',
    'opcolor', 'optedin', 'origin', 'originalfilename', 'originalframerate',
    'originalmedia', 'orientation', 'outputgain', 'ownername', 'packagelastmodifydate',
    'pagemode', 'pagenumber', 'part', 'photoshopformat', 'photoshopquality',
    'photoshopthumbnail', 'picture', 'picturemode', 'picturemimetype', 'picturestyle',
    'picturestylepc', 'picturestyleuserdef', 'picturetype', 'pixelformat',
    'planarconfiguration', 'planes', 'postertime', 'postscriptfontname',
    'postscriptfontname_en_us', 'predictor', 'preferredrate', 'preferredvolume',
    'presentationaspectratio', 'previewduration', 'previewimage', 'previewpng',
    'previewtime', 'primarychromaticities', 'printposition', 'printscale', 'printstyle',
    'profileandlevel', 'profileclass', 'profilecmmtype', 'profileconnectionspace',
    'profilecopyright', 'profilecreator', 'profiledatetime', 'profiledescription',
    'profilefilesignature', 'profilename', 'profileversion', 'preroll', 'quality',
    'quoting', 'rawjpgsize', 'rawmeasuredrggb', 'readername', 'recordmode', 'redbalance',
    'redcodeversion', 'redeyereduction', 'redmatrixcolumn', 'redtrc', 'reelnumber',
    'renditionclass', 'renderingintent', 'resourceforksize', 'resolutionunit',
    'rgbcurves', 'roundedtimecodetimebase', 'rowcount', 'rowsperstrip', 'safetyshift',
    'sampleformat', 'samplesize', 'samplesperpixel', 'sampledheight', 'sampledwidth',
    'saturation', 'scalecrop', 'scalefactor35efl', 'scenecapturetype', 'scenetype',
    'schemasnamespaceuri', 'schemasprefix', 'schemaspropertycategory',
    'schemaspropertydescription', 'schemaspropertyname', 'schemasschema',
    'schemaspropertyvaluetype', 'sdkversion', 'selectionduration', 'selectiontime',
    'selftimer', 'sendduration', 'sensor', 'sensorbottomborder', 'sensorheight',
    'sensorleftborder', 'sensorrightborder', 'sensortopborder', 'sensorwidth',
    'serialnumber', 'serialnumberformat', 'setbuttonwhenshooting', 'shareddoc',
    'sharpness', 'sharpnesslandscape', 'sharpnessmonochrome', 'sharpnessportrait',
    'sharpnessstandard', 'sharpnessuserdef1', 'sharpnessuserdef2', 'sharpnessuserdef3',
    'shootingmode', 'shutterbuttonafonbutton', 'shuttercurtainhack', 'shuttermode',
    'shutterspeed', 'shutterspeedvalue', 'slicesgroupname', 'slowsync',
    'spatialfrequencyresponse', 'startedgecode', 'starttimecode', 'storageformatdate',
    'storageformattime', 'storageserialnumber', 'storagetype', 'streamcount',
    'streamname', 'streamnumber', 'streamtype', 'stripbytecounts', 'stripoffsets',
    'subseccreatedate', 'subsecdatetimeoriginal', 'subsecmodifydate', 'subsectime',
    'subsectimedigitized', 'subsectimeoriginal', 'superimposeddisplay', 'tag_',
    'tag_pid_guid', 'taggedpdf', 'tagtrackuid', 'take', 'talb', 'targetaperture',
    'targetexposuretime', 'tcon', 'tcop', 'tdrc', 'technology', 'template',
    'templateactuate', 'templatehref', 'templatetype', 'theoraversion', 'thumbnailclip',
    'thumbnailformat', 'thumbnailheight', 'thumbnailimage', 'thumbnailimagevalidarea',
    'thumbnaillength', 'thumbnailoffset', 'thumbnailwidth', 'timecodescale',
    'timecreated', 'timeoffset', 'timescale', 'tit2', 'titlesofparts', 'titleofparts',
    'tlen', 'toolkitversion', 'tonecurve', 'too', 'totalsamples', 'tpe1', 'track',
    'trackcreatedate', 'trackduration', 'trackid', 'tracklanguage', 'trackmodifydate',
    'tracknumber', 'tracktype', 'trackuid', 'trackvolume', 'trademark', 'trademark_en_us',
    'trapped', 'trck', 'tsse', 'underlineposition', 'underlinethickness', 'url_list',
    'userdef1picturestyle', 'userdef2picturestyle', 'userdef3picturestyle', 'uslt__eng',
    'uslt_eng', 'validafpoints', 'vendor', 'vendorid', 'version', 'verticalsub_sampling',
    'videocardgamma', 'videocodecname', 'videocodingschemeid', 'videoencoding',
    'videoformat', 'videoframecount', 'videolinemap', 'viewbox', 'viewingconddesc',
    'viewingcondilluminant', 'viewingcondilluminanttype', 'viewingcondsurround',
    'wb_rggblevels', 'wb_rggblevelsauto', 'wb_rggblevelsasshot', 'wb_rggblevelscloudy',
    'wb_rggblevelsdaylight', 'wb_rggblevelsflash', 'wb_rggblevelsfluorescent',
    'wb_rggblevelskelvin', 'wb_rggblevelsmeasured', 'wb_rggblevelsshade',
    'wb_rggblevelstungsten', 'wbbracketmode', 'wcom', 'wcom_http___www_atlantic_records_com',
    'weight', 'whitebalance', 'whitepoint', 'wma_file_id', 'wm_albumtitle',
    'wm_composer', 'wm_encodingsettings', 'wm_genre', 'wm_lyrics', 'wm_mcdi',
    'wm_track', 'wm_tracknumber', 'wm_year', 'wmfsdkneeded', 'wmfsdkversion',
    'woar', 'woar_www_matchmboxtwenty_com', 'word97', 'writername', 'writingapp',
    'xoffset', 'xmlns', 'ycbcrpositioning', 'ycbcrsubsampling', 'year', 'yoffset',
    'zipbitflag', 'zipcompressedsize', 'zipcrc', 'zipfilename', 'ziprequiredversion',
    'zipuncompressedsize',

    # Eudora-Statistik-Felder
    'eudorastatsversion', 'eudorastatsstarttime', 'eudorastatsjunkstarttime',
    'eudorastatscurrenttime', 'eudorastatsreceivedmailcurrentday',
    'eudorastatsreceivedmailcurrentweek', 'eudorastatsreceivedmailcurrentmonth',
    'eudorastatsreceivedmailcurrentyear', 'eudorastatsreceivedmailpreviousday',
    'eudorastatsreceivedmailpreviousweek', 'eudorastatsreceivedmailpreviousmonth',
    'eudorastatsreceivedmailpreviousyear', 'eudorastatsreceivedmailaveragesumday',
    'eudorastatsreceivedmailaveragesumweek', 'eudorastatsreceivedmailaveragesummonth',
    'eudorastatsreceivedmailaveragesumyear', 'eudorastatssentmailcurrentday',
    'eudorastatssentmailcurrentweek', 'eudorastatssentmailcurrentmonth',
    'eudorastatssentmailcurrentyear', 'eudorastatssentmailpreviousday',
    'eudorastatssentmailpreviousweek', 'eudorastatssentmailpreviousmonth',
    'eudorastatssentmailpreviousyear', 'eudorastatssentmailaveragesumday',
    'eudorastatssentmailaveragesumweek', 'eudorastatssentmailaveragesummonth',
    'eudorastatssentmailaveragesumyear', 'eudorastatsusagesecondscurrentday',
    'eudorastatsusagesecondscurrentweek', 'eudorastatsusagesecondscurrentmonth',
    'eudorastatsusagesecondscurrentyear', 'eudorastatsusagesecondspreviousday',
    'eudorastatsusagesecondspreviousweek', 'eudorastatsusagesecondspreviousmonth',
    'eudorastatsusagesecondspreviousyear', 'eudorastatsusagesecondsaveragesumday',
    'eudorastatsusagesecondsaveragesumweek', 'eudorastatsusagesecondsaveragesummonth',
    'eudorastatsusagesecondsaveragesumyear', 'eudorastatsusagesecondstotal',
    'eudorastatsscoredjunkcurrentday', 'eudorastatsscoredjunkcurrentweek',
    'eudorastatsscoredjunkcurrentmonth', 'eudorastatsscoredjunkcurrentyear',
    'eudorastatsscoredjunkpreviousday', 'eudorastatsscoredjunkpreviousweek',
    'eudorastatsscoredjunkpreviousmonth', 'eudorastatsscoredjunkpreviousyear',
    'eudorastatsscoredjunkaveragesumday', 'eudorastatsscoredjunkaveragesumweek',
    'eudorastatsscoredjunkaveragesummonth', 'eudorastatsscoredjunkaveragesumyear',
    'eudorastatsscorednotjunkcurrentday', 'eudorastatsscorednotjunkcurrentweek',
    'eudorastatsscorednotjunkcurrentmonth', 'eudorastatsscorednotjunkcurrentyear',
    'eudorastatsscorednotjunkpreviousday', 'eudorastatsscorednotjunkpreviousweek',
    'eudorastatsscorednotjunkpreviousmonth', 'eudorastatsscorednotjunkpreviousyear',
    'eudorastatsscorednotjunkaveragesumday', 'eudorastatsscorednotjunkaveragesumweek',
    'eudorastatsscorednotjunkaveragesummonth', 'eudorastatsscorednotjunkaveragesumyear',
    'eudorastatswhitelistcurrentday', 'eudorastatswhitelistcurrentweek',
    'eudorastatswhitelistcurrentmonth', 'eudorastatswhitelistcurrentyear',
    'eudorastatswhitelistpreviousday', 'eudorastatswhitelistpreviousweek',
    'eudorastatswhitelistpreviousmonth', 'eudorastatswhitelistpreviousyear',
    'eudorastatswhitelistaveragesumday', 'eudorastatswhitelistaveragesumweek',
    'eudorastatswhitelistaveragesummonth', 'eudorastatswhitelistaveragesumyear',
    'eudorastatsfalsepositivescurrentday', 'eudorastatsfalsepositivescurrentweek',
    'eudorastatsfalsepositivescurrentmonth', 'eudorastatsfalsepositivescurrentyear',
    'eudorastatsfalsepositivespreviousday', 'eudorastatsfalsepositivespreviousmonth',
    'eudorastatsfalsepositivespreviousyear', 'eudorastatsfalsepositivesaveragesumday',
    'eudorastatsfalsepositivesaveragesumweek', 'eudorastatsfalsepositivesaveragesummonth',
    'eudorastatsfalsepositivesaveragesumyear', 'eudorastatsfalsenegativescurrentday',
    'eudorastatsfalsenegativescurrentweek', 'eudorastatsfalsenegativescurrentmonth',
    'eudorastatsfalsenegativescurrentyear', 'eudorastatsfalsenegativespreviousday',
    'eudorastatsfalsenegativespreviousweek', 'eudorastatsfalsenegativespreviousmonth',
    'eudorastatsfalsenegativespreviousyear', 'eudorastatsfalsenegativesaveragesumday',
    'eudorastatsfalsenegativesaveragesumweek', 'eudorastatsfalsenegativesaveragesummonth',
    'eudorastatsfalsenegativesaveragesumyear', 'eudorastatsfalsewhitelistcurrentday',
    'eudorastatsfalsewhitelistcurrentweek', 'eudorastatsfalsewhitelistcurrentmonth',
    'eudorastatsfalsewhitelistcurrentyear', 'eudorastatsfalsewhitelistpreviousday',
    'eudorastatsfalsewhitelistpreviousweek', 'eudorastatsfalsewhitelistpreviousmonth',
    'eudorastatsfalsewhitelistpreviousyear', 'eudorastatsfalsewhitelistaveragesumday',
    'eudorastatsfalsewhitelistaveragesumweek', 'eudorastatsfalsewhitelistaveragesummonth',
    'eudorastatsfalsewhitelistaveragesumyear', 'eudorastatsusagereadcurrentday',
    'eudorastatsusagereadcurrentweek', 'eudorastatsusagereadcurrentmonth',
    'eudorastatsusagereadcurrentyear', 'eudorastatsusagereadtotal',
    'eudorastatsusageothercurrentday', 'eudorastatsusageothercurrentweek',
    'eudorastatsusageothercurrentmonth', 'eudorastatsusageothercurrentyear',
    'eudorastatsusageothertotal',
    }

    # =======================================================
# HIER BEGINNT DER CODE, DEN SIE KOPIEREN MÜSSEN
# =======================================================

    # Schritt 1: Standardisiere alle eingehenden Schlüssel
    standardized_metadata = {sanitize_tag(k): v for k, v in metadata.items()}
    
    unified_metadata = {}
    processed_standardized_keys = set()
    
    # Schritt 2: Markiere alle Felder aus der Blockliste als "verarbeitet", damit sie ignoriert werden.
    for k_to_remove in always_remove_standardized_keys:
        processed_standardized_keys.add(k_to_remove)
    
    # Spezielle Zusammenführung von datecreated und timecreated
    if 'datecreated' in standardized_metadata and 'timecreated' in standardized_metadata:
        date_val = str(standardized_metadata['datecreated']).split(' ')[0]
        time_val = str(standardized_metadata['timecreated'])
        try:
            time_val_clean = time_val.split('+')[0].split('-')[0].split('Z')[0].strip()
            combined_str = f"{date_val}T{time_val_clean}"
            standardized_metadata['asset_created_date_combined'] = format_date_to_iso(combined_str)
        except Exception:
            pass

    # Schritt 3: KERNLOGIK: Vereinheitlichung über das key_mapping-Wörterbuch
    key_mapping = {
        ("imagewidth", "image_width", "width", "exifimagewidth"): "image_width",
        ("imageheight", "image_height", "height", "imagelength", "exifimageheight"): "image_height",
        ("bitdepth", "bits_per_pixel", "colorresolutiondepth"): "image_bit_depth",
        ("samplesize", "bitsperaudiosample"): "audio_bits_per_sample",
        ("filesize", "size", "filesfilesize"): "size",
        ("filetypeextension", "filetype", "extension"): "extension",
        ("mimetype", "mime_type", "format"): "mime_type",
        ("newlines", "lineending"): "document_line_break",
        ("createdate", "datetimeoriginal", "creationdate", "date", "mediacreatedate", "creation_date", "creationtime", "asset_created_date_combined", "datecreated", "Creation_time", "CreationDate", "Creation-date", "CreateDate", "MediaCreateDate", "CreationTime", "filesfilefirstsaveddate"): "asset_created_date",
        ("modifydate", "datemodified", "moddate", "metadatadate", "mediamodifydate", "zipmodifydate", "ModifyDate", "MediaModifyDate"): "asset_modified_date",
        ("lastprinted", "print date"): "asset_last_printed_date",
        ("keywords", "document_keywords", "tags", "genre"): "document_keywords",
        ("author", "score_partwiseidentificationcreator", "initial_creator"): "document_author",
        ("title", "documenttitle", "score_partwisemovement_title"): "document_title",
        ("subject", "documentsubject"): "document_subject",
        ("description", "documentdescription"): "document_description",
        ("producer", "software", "creatortool", "pdf_creator", "pdf_producer", "creator", "score_partwiseidentificationencodingsoftware", "xmptoolkit", "generator", "compobjusertype"): "document_creator_tool",
        ("lasteffort", "lastmodifiedby", "lastsavedby"): "document_last_saved_by",
        ("revisionnumber", "revision", "editing_cycles"): "document_revision_number",
        ("pages", "pdf_num_pages", "num_pages", "pagecount", "document_statisticpage_count"): "document_num_pages",
        ("characters", "charcount", "document_statisticcharacter_count"): "document_characters",
        ("words", "wordcount", "document_statisticword_count"): "document_words",
        ("lines", "linecount", "sam_line_count"): "document_lines",
        ("paragraphs", "paragraphcount", "document_statisticparagraph_count"): "document_paragraphs",
        ("totaledittime", "editing_duration"): "document_total_edit_time",
        ("compression", "compressiontype", "compressionmethod", "zipcompression"): "compression",
        ("colorspacedata",): "colorspacedata",
        ("format_version", "identification", "pdf_version", "pdfversion", "jfifversion", "gifversion", "bmpversion", "doctypeversion", "opusversion"): "document_format_version",
        ("hostcomputer", "system", "primaryplatform"): "operating_system",
        ("note", "doctype"): "document_format_descriptive_name",
        ("duration", "ffprobe_format_duration", "mediaduration", "length"): "duration",
        ("audiocodecname", "audiocodecid", "audioformat"): "audio_codec_id",
        ("audiochannels", "channels", "audio_channels", "numchannels", "channelcount"): "audio_channel_count",
        ("samplerate", "audiosamplerate"): "samplerate",
        ("encoder", "compressorname", "encodersettings", "encodingsettings"): "encoder",
        ("avgbitrate", "ffprobe_format_bit_rate", "maxdatarate", "maxbitrate", "audiobitrate"): "bitrate",
        ("videobitrate", "nominalvideobitrate"): "video_bitrate",
        ("compressorid", "videocodecid", "videocodec"): "video_codec_id",
        ("rights", "score_partwiseidentificationrights", "copyright"): "document_rights",
        ("document_encoding_date",): "document_encoding_date",
        ("image_mode", "colortype", "photometricinterpretation"): "image_mode",
        ("language", "languagecode", "medialanguagecode"): "language_code",
        ("mimeencoding",): "document_mime_encoding",
        ("characterswithspaces", "charcountwithspaces"): "document_characters_with_spaces",
        ("videoframerate", "framerate"): "video_frame_rate",
        ("sourceimagewidth", "displaywidth"): "video_frame_width",
        ("sourceimageheight", "displayheight"): "video_frame_height",
        ("xresolution",): "image_x_resolution",
        ("yresolution",): "image_y_resolution",
        ("pixelaspectratio", "aspectratio"): "pixel_aspect_ratio",
        ("mediadatasize",): "media_data_size",
        ("container_format_version",): "container_format_version",
        ("audio_encoding_format", "encoding"): "audio_encoding_format",
        ("audio_sample_count", "audiosamplecount"): "audio_sample_count",
        ("document_statisticobject_count",): "num_objects",
        ("templatedate",): "document_template_date",
        ("hyperlinks",): "document_hyperlinks",
        ("presentationtarget",): "document_presentationtarget",
        ("slides",): "document_slides",
        ("headingpairs",): "document_headingpairs",
        ("titleofparts",): "document_titleofparts",
        ("docflags", "doc_flags"): "document_flags",
        ("originalfilename",): "original_filename",
    }
# =======================================================
# HIER ENDET DER CODE, DEN SIE KOPIEREN MÜSSEN
# =======================================================

    # ANWENDUNG DER MAPPING-REGELN
    for group_keys, preferred_key in key_mapping.items():
        standardized_group_keys = tuple(sanitize_tag(k) for k in group_keys)
        if preferred_key in unified_metadata or all(k in processed_standardized_keys for k in standardized_group_keys):
            for k in standardized_group_keys: processed_standardized_keys.add(k)
            continue

        best_value = None
        for k in group_keys:
            std_k = sanitize_tag(k)
            if std_k in standardized_metadata:
                value = standardized_metadata[std_k]
                if value is not None and str(value).strip().lower() not in ["unknown", "n/a", "-", "none", "", "0"]:

                    # *** HIER IST DIE NEUE, INTEGRIERTE PRÜFUNG ***
                    # Wenn der Zielschlüssel 'document_creator_tool' ist, prüfen wir den Wert sofort.
                    if preferred_key == 'document_creator_tool':
                        if is_likely_software_tool(value):
                            # Wert ist gut, wir nehmen ihn und hören auf zu suchen.
                            best_value = value
                            break
                        else:
                            # Wert ist schlecht (ein Name), wir ignorieren ihn und suchen weiter
                            # nach einem besseren Wert in derselben Gruppe (z.B. aus 'Producer').
                            continue
                    else:
                        # Für alle anderen Schlüssel gilt die alte Logik: Nimm den ersten gültigen Wert.
                        best_value = value
                        break

        if best_value is not None:
            if "date" in preferred_key:
                best_value = format_date_to_iso(str(best_value))

            if best_value is not None and str(best_value).strip():
                unified_metadata[preferred_key] = str(best_value)

        for k in standardized_group_keys:
            processed_standardized_keys.add(k)

    # Schritt 4: NICHT GEMAPPTE WERTE HINZUFÜGEN
    for standardized_key, original_value in standardized_metadata.items():
        if standardized_key not in processed_standardized_keys:
            if original_value is not None and str(original_value).strip().lower() not in ["unknown", "n/a", "-", "none", "", "0"]:
                unified_metadata[standardized_key] = str(original_value)

    # SPEZIALBEHANDLUNG 'encoded_by'
    if 'encoded_by' in unified_metadata:
        encoded_by_val = unified_metadata.pop('encoded_by')
        if 'encoder' in unified_metadata:
            unified_metadata['encoder'] = f"{unified_metadata['encoder']}; Encoded by: {encoded_by_val}"
        else:
            unified_metadata['encoder'] = encoded_by_val

    if 'document_keywords' in unified_metadata:
        del unified_metadata['document_keywords']

        # Spezielle, kontextabhängige Behandlung für den mehrdeutigen Schlüssel 'bitspersample'
    if 'bitspersample' in standardized_metadata:
        # Hole den Wert direkt aus den standardisierten Roh-Metadaten
        value = standardized_metadata['bitspersample']
        mime_type = unified_metadata.get('mime_type', '').lower()

        if mime_type.startswith('image/'):
            # Bei Bildern ist es die Bittiefe des Bildes. Nur setzen, wenn noch nicht vorhanden.
            if 'image_bit_depth' not in unified_metadata:
                unified_metadata['image_bit_depth'] = value
        elif mime_type.startswith('audio/'):
            # Bei Audio ist es die Bittiefe des Audios. Nur setzen, wenn noch nicht vorhanden.
            if 'audio_bits_per_sample' not in unified_metadata:
                unified_metadata['audio_bits_per_sample'] = value

        # Markiere den Schlüssel als verarbeitet, damit er nicht als ungemappter Wert auftaucht.
        processed_standardized_keys.add('bitspersample')

    return unified_metadata


def add_metadata_to_xml(file_elem, metadata):
    """
    Fügt Metadaten zu einem XML-Element hinzu.
    DIESE KORRIGIERTE VERSION ERZWINGT EINE ALPHABETISCHE SORTIERUNG DER TAGS.
    Sie bereinigt auch Werte von ungültigen XML-Zeichen und filtert unerwünschte Tags.
    """
    # Blockliste für exakte standardisierte Tags, die zusätzlich immer entfernt werden sollen.
    additional_blocklist = {'timescale', 'handlerdescription', 'audiobitspersample'}

    # --- HIER IST DIE NEUE, KORRIGIERTE LOGIK ---

    # NEU: Wir sortieren die Metadaten-Items (Schlüssel-Wert-Paare) hier, direkt vor dem Schreiben.
    # Dies garantiert die alphabetische Reihenfolge in der XML-Ausgabe, unabhängig davon,
    # wie die Daten vorher im Wörterbuch gespeichert waren.
    sorted_items = sorted(metadata.items())

    for k, v in sorted_items:
        tag = sanitize_tag(k)
        clean_v = sanitize_for_xml(v)

        # Regel 1 - Spezielle Behandlung für <colorspacedata> (aus Ihren früheren Anforderungen)
        if tag == 'colorspacedata' and clean_v.strip().upper() == 'RGB':
            continue

        # Regel 2 - Allgemeine "Schwarze Liste" (aus Ihren früheren Anforderungen)
        if tag in TAGS_TO_REMOVE:
            continue
        
        # Regel 3 - Zusätzliche, interne Blockliste
        if (tag in additional_blocklist or 
            tag.startswith('score_partwise') or
            tag.startswith('registration') or
            tag.startswith('statemachine')):
            continue

        # --- ENDE DER FILTERLOGIK ---

        # Überspringe bekannte binäre ASF/WMA-Attribute, die XML ungültig machen können
        if '[ASFByteArrayAttribute' in clean_v:
            continue

        # Der Rest der Funktion bleibt gleich, fügt die bereinigten Werte hinzu.
        existing_elem = file_elem.find(tag)

        if tag == "document_headingpairs":
            if existing_elem is None:
                heading_elem = ET.SubElement(file_elem, tag)
                if isinstance(v, list):
                    for pair in v:
                        if isinstance(pair, list) and len(pair) == 2:
                            clean_name = sanitize_for_xml(pair[0])
                            clean_level = sanitize_for_xml(pair[1])
                            ET.SubElement(heading_elem, "heading", name=clean_name, level=clean_level)
                        else:
                            clean_name = sanitize_for_xml(pair)
                            ET.SubElement(heading_elem, "heading", name=clean_name)
                else:
                    heading_elem.text = clean_v
        else:
            if existing_elem is not None:
                existing_elem.text = clean_v
            else:
                ET.SubElement(file_elem, tag).text = clean_v


def process_file(file_path, relative_path):

    global INTEGRITY_SUCCESS, INTEGRITY_ERRORS, INTEGRITY_NEW, REFERENCE_HASHES
    print(f"\n==================================================")
    print(f"Verarbeite Datei: {relative_path}")
    print(f"==================================================")
    file_elem = ET.SubElement(root, "file", {
        "path": relative_path.as_posix(),
        "name": relative_path.name,
        "extension": file_path.suffix.lower()
    })

    all_raw_metadata = {}

    file_info = get_file_info(file_path)
    all_raw_metadata.update(file_info)
    # 1. SHA256 berechnen
    current_sha = hash_sha256(file_path)
    all_raw_metadata["sha256"] = current_sha

    # 2. Integritäts-Check gegen Referenz-Hashes
    file_name_lower = file_path.name.lower()
    if file_name_lower in REFERENCE_HASHES:
        ref_sha = REFERENCE_HASHES[file_name_lower]
        if current_sha.lower() == ref_sha.lower():
            print(f"  \033[92m[MATCH] Integritaet verifiziert.\033[0m")
            all_raw_metadata["integrity_status"] = "verified"
            INTEGRITY_SUCCESS.append(str(relative_path))
        else:
            print(f"  \033[91m[ALARM] HASH-ABWEICHUNG!\033[0m")
            all_raw_metadata["integrity_status"] = "CORRUPTED_OR_MODIFIED"
            INTEGRITY_ERRORS.append({
                "file": str(relative_path),
                "expected": ref_sha,
                "found": current_sha
            })
    else:
        # Falls die Datei in den Vorstufen nicht existierte (z.B. ein PDF-Derivat)
        all_raw_metadata["integrity_status"] = "new_file"
        INTEGRITY_NEW.append(str(relative_path))

    siegfried_data = run_siegfried(file_path)
    all_raw_metadata.update(siegfried_data)

    mime_type_from_siegfried = all_raw_metadata.get("mime_type", "").lower()
    if mime_type_from_siegfried.startswith("image/"):
        image_info = extract_image_info(file_path)
        all_raw_metadata.update(image_info)

    exiftool_data = extract_metadata_exiftool(file_path)
    all_raw_metadata.update(exiftool_data)

    ffprobe_data = extract_metadata_ffprobe(file_path)
    all_raw_metadata.update(ffprobe_data)

    mutagen_data = extract_mutagen_info(file_path)
    all_raw_metadata.update(mutagen_data)

    if file_path.suffix.lower() == '.pdf':
        pdf_info = extract_pdf_info(file_path)
        all_raw_metadata.update(pdf_info)

    if file_path.suffix.lower() == ".sam":
        sam_data = extract_sam_specific(file_path)
        all_raw_metadata.update(sam_data)

    if file_path.suffix.lower() == ".mxl":
        musicxml_info = extract_musicxml_info(file_path)
        all_raw_metadata.update(musicxml_info)

    print(f"\n--- Roh-Metadaten für {relative_path} (nach allen Extraktoren) ---")
    for k, v in all_raw_metadata.items():
        print(f"  {k}: {v}")
    print("--------------------------------------------------")

    try:
        # Schritt 1: Datei mit Python im Binärmodus öffnen.
        # Dies ist robust gegen Sonderzeichen im Pfad und geschieht innerhalb des try-Blocks.
        with open(file_path, "rb") as f:
            file_data = f.read()
    
        # Schritt 2: Den Inhalt (data=) an YARA übergeben, nicht mehr den Pfad.
        matches = rules.match(data=file_data)

        # Schritt 3: Die gefundenen Matches wie zuvor verarbeiten.
        # Diese Logik ist jetzt ebenfalls sicher innerhalb des try-Blocks.
        detailed_match_info = []
        all_match_rules = [{"rule": m.rule, "meta": m.meta} for m in matches]
        lower_rule_names = {m_info['rule'].lower() for m_info in all_match_rules}

        for m_info in all_match_rules:
            rule_name_lower = m_info['rule'].lower()
            keep_rule = True
            if rule_name_lower == "csv":
                if "sam" in lower_rule_names or "eml" in lower_rule_names or "tiff" in lower_rule_names:
                    keep_rule = False

            if keep_rule:
                detailed_match_info.append(m_info)

    except Exception as e:
        print(f"Fehler bei YARA-Matches für {file_path}: {e}")
        matches = []

    final_unified_metadata = unify_metadata_keys(all_raw_metadata)

    # --- KONSISTENZ-LOGIK FÜR VIDEO-DIMENSIONEN (VERSION 3 - ROBUST) ---
    final_mime_type_for_cleanup = final_unified_metadata.get("mime_type", "").lower()
    known_video_suffixes = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".3gp", ".mxf", ".r3d", ".m4v"}

    is_video_file = (final_mime_type_for_cleanup.startswith('video/') or
                     file_path.suffix.lower() in known_video_suffixes)

    if is_video_file:
        # Behandelt die Breite
        if 'image_width' in final_unified_metadata:
            if 'video_frame_width' not in final_unified_metadata:
                final_unified_metadata['video_frame_width'] = final_unified_metadata['image_width']
            del final_unified_metadata['image_width']

        # Behandelt die Höhe
        if 'image_height' in final_unified_metadata:
            if 'video_frame_height' not in final_unified_metadata:
                final_unified_metadata['video_frame_height'] = final_unified_metadata['image_height']
            del final_unified_metadata['image_height']

    if 'duration' in final_unified_metadata:
        final_mime_type = final_unified_metadata.get("mime_type", "").lower()
        file_type_group = get_file_type_group(file_path)

        is_media_file = (final_mime_type.startswith('audio/') or
                        final_mime_type.startswith('video/') or
                        final_mime_type == 'image/gif' or
                        file_type_group in ['audio', 'video'])

        if not is_media_file:
            print(f"Info: Entferne 'duration' ({final_unified_metadata['duration']}) für unpassenden MIME-Typ: {final_mime_type} und Dateityp: {file_type_group}")
            del final_unified_metadata['duration']

    if 'audio_channel_count' in final_unified_metadata:
        final_mime_type = final_unified_metadata.get("mime_type", "").lower()
        file_type_group = get_file_type_group(file_path)

        is_media_file = (final_mime_type.startswith('audio/') or
                        final_mime_type.startswith('video/') or
                        file_type_group in ['audio', 'video'])

        if not is_media_file:
            print(f"Info: Entferne 'audio_channel_count' ({final_unified_metadata['audio_channel_count']}) für unpassenden MIME-Typ: {final_mime_type} und Dateityp: {file_type_group}")
            del final_unified_metadata['audio_channel_count']


    print(f"\n--- Vereinheitlichte Metadaten für {relative_path} (final) ---")
    for k, v in sorted(final_unified_metadata.items()):
        print(f"  {k}: {v}")
    print("--------------------------------------------------")

    add_metadata_to_xml(file_elem, final_unified_metadata)

    valid_elem = ET.SubElement(file_elem, "validity")
    suffix = file_path.suffix.lower()
    mime_type = final_unified_metadata.get("mime_type", "").lower()

    yara_match_rules_simple_names = []
    if 'matches' in locals() and matches:
        all_yara_rule_names = {m.rule for m in matches}
        for m in matches:
            rule_name_lower = m.rule.lower()
            keep_rule = True
            if rule_name_lower == "csv":
                if "sam" in all_yara_rule_names or "eml" in all_yara_rule_names or "tiff" in all_yara_rule_names:
                    keep_rule = False
            if keep_rule:
                yara_match_rules_simple_names.append(m.rule)

    is_valid = False
    try:
        if suffix == ".pdf":
            try:
                PdfReader(file_path)
                is_valid = True
            except Exception as e:
                print(f"PDF-Validierung fehlgeschlagen für {relative_path}: {e}")
                is_valid = False
        elif suffix in [".docx", ".xlsx", ".pptx", ".odt", ".ods", ".odp"]:
            with open(file_path, "rb") as f:
                magic = f.read(4)
                if magic in [b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"]:
                    try:
                        with zipfile.ZipFile(file_path, 'r') as zip_ref:
                            if zip_ref.testzip() is None:
                                is_valid = True
                            else:
                                print(f"ZIP-Validierung fehlgeschlagen für {relative_path}: fehlerhafte Datei im ZIP.")
                    except zipfile.BadZipFile:
                        print(f"ZIP-Validierung fehlgeschlagen für {relative_path}: Keine gültige ZIP-Datei.")
                else:
                    print(f"ZIP-Validierung fehlgeschlagen für {relative_path}: Kein ZIP-Magic-Header.")
        elif mime_type.startswith("image/"):
            try:
                Image.open(file_path).verify()
                is_valid = True
            except Exception as e:
                print(f"Bild-Validierung fehlgeschlagen für {relative_path}: {e}")
                is_valid = False
        elif mime_type.startswith("audio/") or mime_type.startswith("video/"):
            if final_unified_metadata.get("duration") or final_unified_metadata.get("ffprobe_format_duration"):
                is_valid = True
        elif suffix == ".mxl":
            if final_unified_metadata.get("document_title") or final_unified_metadata.get("document_creator_tool"):
                is_valid = True
        elif any(rule in yara_match_rules_simple_names for rule in ["SAM", "EML", "CSV", "HTML", "XHTML", "TXT", "ZIP_ARCHIVE"]):
            is_valid = True

        if not is_valid and len(final_unified_metadata) > 5:
            is_valid = True

        valid_elem.text = "Yes" if is_valid else "No"
    except Exception as e:
        valid_elem.text = "No"
        print(f"Validierung fehlgeschlagen für {relative_path}: {e}")


def write_xml_to_file(element_tree_root, output_file_path):
    """
    Schreibt den XML-Baum direkt in eine Datei und verwendet die sichere
    ET.indent() Methode zur Formatierung, um minidom und dessen Parser-Fehler zu umgehen.
    """
    try:
        # Fügt Einrückungen direkt und sicher hinzu (verfügbar ab Python 3.9)
        ET.indent(element_tree_root)
    except AttributeError:
        # Fallback für ältere Python-Versionen (erzeugt unformatiertes, aber gültiges XML)
        pass

    tree = ET.ElementTree(element_tree_root)
    tree.write(output_file_path, encoding='utf-8', xml_declaration=True)
    print(f"Metadaten erfolgreich nach {output_file_path} geschrieben.")


def get_file_type_group(filepath):
    suffix = filepath.suffix.lower()
    image_suffixes = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp", ".psd"}
    audio_suffixes = {".mp3", ".wav", ".flac", ".ogg", ".aac", ".m4a", ".wma", ".alac", ".aiff", ".aif", ".voc"}
    video_suffixes = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".mxf", ".r3d", ".m4v"}
    document_suffixes = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt", ".ods", ".odp", ".rtf", ".txt", ".csv", ".eml", ".sam", ".mxl", ".html", ".htm", ".xhtml"}
    archive_suffixes = {".zip", ".rar", ".7z", ".tar", ".gz"}

    if suffix in image_suffixes:
        return "image"
    if suffix in audio_suffixes:
        return "audio"
    if suffix in video_suffixes:
        return "video"
    if suffix in document_suffixes:
        return "document"
    if suffix in archive_suffixes:
        return "archive"
    return "other"


def main():
    if not os.path.isdir(BASE_DIR):
        print(f"Fehler: Das angegebene Verzeichnis '{BASE_DIR}' existiert nicht.")
        sys.exit(1)

    processed_count = 0
    for dirpath, _, filenames in os.walk(BASE_DIR):
        for filename in filenames:
            file_path = Path(dirpath) / filename
            relative_path = file_path.relative_to(BASE_DIR)

            if filename.startswith("._") or filename.startswith("~"):
                continue

            try:
                if not file_path.is_file():
                    continue

                print(f"\n--- Verarbeite Metadaten für einzelne Datei: {relative_path} ---")
                process_file(file_path, relative_path)
                processed_count += 1
            except Exception as e:
                print(f"Ein unerwarteter Fehler ist aufgetreten beim Verarbeiten von {file_path}: {e}")
                ET.SubElement(root, "file", {"path": relative_path.as_posix(), "name": relative_path.name, "error": str(e)})

    if processed_count > 0:
        write_xml_to_file(root, OUTPUT_XML)

        integrity_log_path = Path(OUTPUT_XML).parent / f"{Path(OUTPUT_XML).stem}_integrity.log"
        
        try:
            with open(integrity_log_path, 'w', encoding='utf-8') as f:
                f.write(f"INTEGRITY CHECK REPORT - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*80 + "\n\n")
                
                if not INTEGRITY_ERRORS:
                    f.write("ERGEBNIS: Alle vorhandenen Referenz-Hashes wurden erfolgreich verifiziert.\n")
                    f.write(f"Keine Manipulationen oder Kopierfehler erkannt.\n\n")
                else:
                    f.write(f"ALARM: {len(INTEGRITY_ERRORS)} DATEIEN WURDEN SEIT DER VORSTUFE VERAENDERT!\n")
                    f.write("="*80 + "\n")
                    for err in INTEGRITY_ERRORS:
                        f.write(f"DATEI:    {err['file']}\n")
                        f.write(f"Soll-Hash: {err['expected']}\n")
                        f.write(f"Ist-Hash:  {err['found']}\n")
                        f.write("-"*80 + "\n")
                    f.write("\n")

                f.write(f"STATISTIK:\n")
                f.write(f"- Verifizierte Dateien: {len(INTEGRITY_SUCCESS)}\n")
                f.write(f"- Neue Dateien (ohne Referenz): {len(INTEGRITY_NEW)}\n")
                f.write(f"- Fehlerhafte Dateien: {len(INTEGRITY_ERRORS)}\n\n")

                f.write("DETAILS DER VERIFIZIERTEN DATEIEN:\n")
                for item in sorted(INTEGRITY_SUCCESS):
                    f.write(f"[OK] {item}\n")

            print(f"\033[94mIntegritaets-Protokoll erstellt: {integrity_log_path.name}\033[0m")
        except Exception as e:
            print(f"\033[91mFehler beim Schreiben des Integritaets-Logs: {e}\033[0m")
        
    
        try:
            shutil.copy2(OUTPUT_XML, validated_paths["vl_output_xml"])
            print(f"\033[92mIndex-Datei zusätzlich erfolgreich nach Stufe 4 kopiert:\033[0m")
            print(f" -> {validated_paths['vl_output_xml']}")
        except Exception as e:
            print(f"\033[91mFehler beim Kopieren der Index-Datei nach Stufe 4: {e}\033[0m")
            
        print(f"\n{processed_count} Dateien verarbeitet.")
    else:
        print("\nKeine Dateien zum Verarbeiten gefunden oder alle übersprungen.")


if __name__ == "__main__":
    main()

    # --- ANFANG: HINZUGEFÜGTER CODE-BLOCK (MIT KORREKTER FUNKTION) ---
    if validated_paths:
        destination_folder = validated_paths["output_xml"].parent
        
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
    # --- ENDE: HINZUGEFÜGTER CODE-BLOCK ---