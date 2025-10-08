# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

#!/usr/bin/env python3
import os
import sys
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
import csv  # Für das Parsen von CSV-Dateien von Brunhilde

# Basispfade setzen - Hier sollten sinnvolle Windows-Standardwerte stehen oder Abfragen erfolgen
BASE_DIR = sys.argv[1] if len(sys.argv) > 1 else "C:\\Users\\digit\\Desktop\\Test_Metadaten auslesen"
OUTPUT_XML = "C:\\Users\\digit\\Desktop\\FileTrove_output.xml"
YARA_RULES_FILE = "C:\\Users\\digit\\Desktop\\Skripte\\rules.yar"

# Konfigurationspfad für Brunhilde-Ausgabe
# Wenn leer, wird ein temporäres Verzeichnis verwendet, das nach der Ausführung gelöscht wird.
# Beispiel: BRUNHILDE_OUTPUT_DIR = "C:\\Users\\digit\\Desktop\\Brunhilde"
BRUNHILDE_OUTPUT_DIR = "C:\\Users\\digit\\Desktop\\Brunhilde"

# Pfade zu externen Tools - ggf. anpassen
EXIFTOOL_PATH = "C:\\Program Files\\ExifTool\\exiftool.exe"  # Anpassen, falls nötig
FFPROBE_PATH = "C:\\Program Files\\ffmpeg\\ffprobe.exe"  # Anpassen, falls nötig
HACHOIR_METADATA_PATH = "C:\\Users\\digit\\.venv\\Scripts\\hachoir-metadata.exe"  # Anpassen, falls nötigt
SIEGFRIED_PATH = "C:\\Program Files\\Siegfried\\sf.exe"  # Anpassen, falls nötig

# Pfade als Path-Objekte definieren um einfacher mit ihnen zu arbeiten
BASE_DIR = Path(BASE_DIR)
OUTPUT_XML = Path(OUTPUT_XML)
YARA_RULES_FILE = Path(YARA_RULES_FILE)
BRUNHILDE_OUTPUT_DIR = Path(BRUNHILDE_OUTPUT_DIR)

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


def hash_sha512(filepath):
    h = hashlib.sha512()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        print(f"Fehler beim SHA512-Hashing von {filepath}: {e}")
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
        result = subprocess.run(command, stdout=stdout_target, stderr=stderr_target, text=True, check=False, env=env, encoding='utf-8', errors='replace')
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
        pdf_info = {
            "pdf_version": reader.pdf_header_version,
            "pdf_num_pages": str(len(reader.pages))
        }
        doc_info = reader.metadata
        if doc_info:
            if '/Keywords' in doc_info:
                pdf_info['document_keywords'] = str(doc_info['/Keywords'])
            if '/CreationDate' in doc_info:
                # Formatierung hier, bevor es in all_raw_metadata geht
                pdf_info['asset_created_date'] = format_date_to_iso(str(doc_info['/CreationDate']))
            if '/ModDate' in doc_info:
                # Formatierung hier, bevor es in all_raw_metadata geht
                pdf_info['asset_modified_date'] = format_date_to_iso(str(doc_info['/ModDate']))

            # Extrahiere Creator und Producer aus PDF-Metadaten
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


def list_directory_contents(path):
    """Listet rekursiv den Inhalt eines Verzeichnisses auf."""
    contents = []
    if path.exists() and path.is_dir():
        for root_dir, dirs, files in os.walk(path):
            #Hier muss file path an Windows angepasst werden
            current_level = Path(root_dir).relative_to(path)
            for d in dirs:
                contents.append(f"  - {str(Path(current_level) / d)}/") #Pfad anpassen
            for f in files:
                contents.append(f"  - {str(Path(current_level) / f)}") #Pfad anpassen
    return contents
def extract_brunhilde_info(source_path):
    """
    Führt Brunhilde für den gegebenen Quellpfad (Datei oder Verzeichnis) aus und extrahiert relevante Metadaten aus den Berichten.
    """
    brunhilde_metadata = {}
    brunhilde_output_base_dir = None
    is_temp_dir = False

    # Hier ist die Korrektur: BRUNHILDE_OUTPUT_DIR muss hier zugreifbar sein
    # Es wurde oben global definiert, daher ist es jetzt hier sichtbar.
    if BRUNHILDE_OUTPUT_DIR:
        brunhilde_output_base_dir = BRUNHILDE_OUTPUT_DIR
        try:
            brunhilde_output_base_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Fehler beim Erstellen des Brunhilde Ausgabeverzeichnisses: {e}")
            return brunhilde_metadata
    else:
        try:
            brunhilde_output_base_dir = Path(tempfile.mkdtemp(prefix="brunhilde_output_"))
        except Exception as e:
            print(f"Fehler beim Erstellen des temporären Verzeichnisses für Brunhilde: {e}")
            return brunhilde_metadata
        is_temp_dir = True

    # Identifier für den Berichtsordner basierend auf dem Namen der Quelle
    identifier = Path(source_path).name.replace('.', '_') + "_collection_report"
    # Brunhilde-Berichtsordner
    brunhilde_report_path = brunhilde_output_base_dir / identifier

    try:
        # Vorhandenen Brunhilde-Berichtsordner löschen, um ein Überschreiben zu erzwingen
        if brunhilde_report_path.exists():
            print(f"Lösche vorhandenen Brunhilde-Berichtsordner: {brunhilde_report_path}")
            shutil.rmtree(brunhilde_report_path)

        # Führen Sie Brunhilde aus.
        brunhilde_command = [
            sys.executable, "-m", "brunnhilde",
            str(source_path),  # Die zu analysierende Quelle (Verzeichnis)
            str(brunhilde_report_path)  # Das Ausgabe-Verzeichnis
        ]

        print(f"\n--- Führe Brunhilde aus für {source_path} (mit ClamAV)... ---")
        print(f"Befehl: {' '.join(brunhilde_command)}")
        print(f"Verwendeter PATH für Brunhilde: {os.environ.get('PATH', 'PATH not found')}")  # Debug-Ausgabe des PATH

        stdout, stderr, returncode = run_command(brunhilde_command, env=os.environ.copy(), stream_output=True)

        print(f"Brunhilde Exit Code: {returncode}")
        print(f"--- Brunhilde-Ausführung beendet ---")

        # Debug: Inhalt des temporären/Ausgabe-Verzeichnisses auflisten
        print(f"\n--- Debug: Contents of Brunhilde output directory ({brunhilde_output_base_dir}) ---")
        temp_dir_contents = list_directory_contents(brunhilde_output_base_dir)
        if temp_dir_contents:
            for item in temp_dir_contents:
                print(item)
        else:
            print("  (Directory is empty or does not exist)")
        print("--------------------------------------------------")

        if not brunhilde_report_path.exists():
            print(f"Fehler: Brunhilde-Berichtsordner nicht gefunden unter {brunhilde_report_path}. Brunhilde hat möglicherweise keine Berichte generiert oder ist fehlgeschlagen.")
            # Zusätzlicher Hinweis basierend auf dem Problem:
            if returncode != 0:
                print(f"Hinweis: Brunhilde beendete sich mit Exit Code {returncode}. Überprüfen Sie die Brunhilde stdout/stderr Ausgabe oben für Fehler.")
            return brunhilde_metadata

        csv_reports_dir = brunhilde_report_path / "csv_reports"
        print(f"Erwartetes CSV-Berichtsverzeichnis: {csv_reports_dir}")

        if not csv_reports_dir.exists():
            print(f"Warnung: CSV-Berichtsverzeichnis nicht gefunden unter {csv_reports_dir}. Möglicherweise keine CSV-Berichte generiert.")

        # Parsen von formats.csv
        formats_csv = csv_reports_dir / "formats.csv"
        if formats_csv.exists():
            print(f"Found {formats_csv}")
            try:
                with open(formats_csv, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    format_summary = []
                    for row in reader:
                        # Bereinigen von leeren Werten
                        cleaned_row = {k.strip(): v.strip() for k, v in row.items() if v.strip()}
                        if cleaned_row:
                            format_summary.append(cleaned_row)
                    if format_summary:
                        brunhilde_metadata['brunhilde_format_summary'] = json.dumps(format_summary)  # Als JSON-String speichern
            except Exception as e:
                print(f"Fehler beim Parsen von formats.csv: {e}")
        else:
            print(f"formats.csv not found at {formats_csv}")

        # Parsen von mimetypes.csv
        mimetypes_csv = csv_reports_dir / "mimetypes.csv"
        if mimetypes_csv.exists():
            print(f"Found {mimetypes_csv}")
            try:
                with open(mimetypes_csv, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    mime_type_summary = []
                    for row in reader:
                        cleaned_row = {k.strip(): v.strip() for k, v in row.items() if v.strip()}
                        if cleaned_row:
                            mime_type_summary.append(cleaned_row)
                    if mime_type_summary:
                        brunhilde_metadata['brunhilde_mime_type_summary'] = json.dumps(mime_type_summary)
            except Exception as e:
                print(f"Fehler beim Parsen von mimetypes.csv: {e}")
        else:
            print(f"mimetypes.csv not found at {mimetypes_csv}")

        # Parsen von siegfried_warnings.csv in eine strukturierte Form
        warnings_by_file_path = {}
        siegfried_warnings_csv = csv_reports_dir / "siegfried_warnings.csv"
        if siegfried_warnings_csv.exists():
            print(f"Found {siegfried_warnings_csv}")
            try:
                with open(siegfried_warnings_csv, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        file_path_in_csv = row.get('File', '').strip()
                        if file_path_in_csv:
                            # Remove the 'File' key as it's the dictionary key now
                            warning_details = {k.strip(): v.strip() for k, v in row.items() if
                                               k.strip() != 'File' and v.strip()}
                            if file_path_in_csv not in warnings_by_file_path:
                                warnings_by_file_path[file_path_in_csv] = []
                            warnings_by_file_path[file_path_in_csv].append(warning_details)
            except Exception as e:
                print(f"Fehler beim Parsen von siegfried_warnings.csv: {e}")
        else:
            print(f"siegfried_warnings.csv not found at {siegfried_warnings_csv}")
        brunhilde_metadata['structured_siegfried_warnings'] = warnings_by_file_path

        # Parsen von unidentified.csv in ein Set von Pfaden
        unidentified_file_paths = set()
        unidentified_csv = csv_reports_dir / "unidentified.csv"
        if unidentified_csv.exists():
            print(f"Found {unidentified_csv}")
            try:
                with open(unidentified_csv, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        file_path_in_csv = row.get('File', '').strip()
                        if file_path_in_csv:
                            unidentified_file_paths.add(file_path_in_csv)
            except Exception as e:
                print(f"Fehler beim Parsen von unidentified.csv: {e}")
        else:
            print(f"unidentified.csv not found at {unidentified_csv}")
        brunhilde_metadata['structured_unidentified_files'] = unidentified_file_paths

        # Parsen von virus_scan_log.txt für ClamAV-Ergebnisse
        virus_scan_log = brunhilde_report_path / "virus_scan_log.txt"
        if virus_scan_log.exists():
            print(f"Found {virus_scan_log}")
            try:
                with open(virus_scan_log, 'r', encoding='utf-8', errors='ignore') as f:
                    log_content = f.read()
                    # Suchen nach "Infected files: 0" oder "Infected files: X"
                    infected_match = re.search(r"Infected files: (\d+)", log_content)
                    if infected_match:
                        infected_count = int(infected_match.group(1))
                        brunhilde_metadata['brunhilde_clamav_infected_files'] = str(infected_count)
                        if infected_count > 0:
                            # Extrahiere Details zu gefundenen Viren
                            virus_details = re.findall(r"^(.*?): (.*?) FOUND$", log_content, re.MULTILINE)
                            if virus_details:
                                brunhilde_metadata['brunhilde_clamav_virus_details'] = json.dumps(virus_details)
                    else:
                        brunhilde_metadata['brunhilde_clamav_status'] = "Log gefunden, aber Infektionsstatus unklar."
            except Exception as e:
                print(f"Fehler beim Parsen von virus_scan_log.txt: {e}")
        else:
            print(f"virus_scan_log.txt not found at {virus_scan_log}")
            brunhilde_metadata['brunhilde_clamav_status'] = "Kein virus_scan_log.txt gefunden (ClamAV möglicherweise nicht ausgeführt oder keine Ausgabe)."

    except Exception as e:
        print(f"Fehler beim Ausführen oder Parsen von Brunhilde für {source_path}: {e}")
    finally:
        if is_temp_dir and brunhilde_output_base_dir and brunhilde_output_base_dir.exists():
            print(f"Cleaning up temporary directory: {brunhilde_output_base_dir}")
            try:
                shutil.rmtree(brunhilde_output_base_dir)  # Temporäres Verzeichnis bereinigen
            except Exception as e:
                print(f"Konnte temporäres Verzeichnis {brunhilde_output_base_dir} nicht löschen: {e}")

    print(f"\n--- Brunhilde Metadata collected for {Path(source_path).name} ---")
    for k, v in brunhilde_metadata.items():
        print(f"  {k}: {v}")
    print("--------------------------------------------------")
    return brunhilde_metadata
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
        # Ihre angeforderten Felder
        'copy_status_version',
        'filecreatedate',
        'isfallback', 'mediabox',
        'thumbnailclip', 'encodedby', 'titlesofparts',
        'optedin',
        'conformance', 'taggedpdf', 'pagemode', 'linearized',
        'schemasnamespaceuri', 'schemasprefix', 'schemasschema', 'schemaspropertycategory', 'schemaspropertydescription', 'schemaspropertyname', 'schemaspropertyvaluetype',
        'thumbnailimage',
        'wm_albumtitle', 'wm_year',
        'previewimage',
        'originalfilename',
        'xoffset',
        'yoffset',
        'timescale', 'handlerdescription',
        'bitspersample',
        'scalecrop', 'linksuptodate', 'shareddoc', 'hyperlinkschanged',
        'streamname',
        'delimiter', 'quoting', 'columncount', 'rowcount',
        'document_statisticobject_count',  # Verhindert <num_objects>
        'templatetype',
        'templateactuate',
        'templatehref',
        'previewpng',
        'document_titleofparts', 'titleofparts',
        'document_headingpairs', 'headingpairs',
        'audio_sample_count', 'audiosamplecount',
        'displayedunitsx', 'displayedunitsy', 'alphachannelsnames', 'photoshopthumbnail',
        'layercount', 'layerrectangles', 'layerblendmodes', 'layeropacities',
        'layervisible', 'layernames',
        'internalversionnumber',
        'encodingprocess', 'colorcomponents', 'ycbcrsubsampling',
        'document_statisticcell_count', 'document_statistictable_count',
        'byteordermark',
        'htmlelementsids', 'htmlelementsclasses', 'htmlelementstags',
        'wcom_http___www_atlantic_records_com',
        'uslt__eng',
        'comm__eng',
        'picture',
        'year',

        # NEU: Explizite Liste der zu entfernenden profiledescription-Felder
        'profiledescriptionml_hr_hr', 'profiledescriptionml_ko_kr', 'profiledescriptionml_nb_no',
        'profiledescriptionml_hu_hu', 'profiledescriptionml_cs_cz', 'profiledescriptionml_da_dk',
        'profiledescriptionml_nl_nl', 'profiledescriptionml_fi_fi', 'profiledescriptionml_it_it',
        'profiledescriptionml_ro_ro', 'profiledescriptionml_es_es', 'profiledescriptionml_uk_ua',
        'profiledescriptionml_he_il', 'profiledescriptionml_zh_tw', 'profiledescriptionml_vi_vn',
        'profiledescriptionml_sk_sk', 'profiledescriptionml_zh_cn', 'profiledescriptionml_ru_ru',
        'profiledescriptionml_fr_fr', 'profiledescriptionml_hi_in', 'profiledescriptionml_ca_es',
        'profiledescriptionml_th_th', 'profiledescriptionml_es_xl', 'profiledescriptionml_de_de',
        'profiledescriptionml', 'profiledescriptionml_pt_br', 'profiledescriptionml_pl_pl',
        'profiledescriptionml_el_gr', 'profiledescriptionml_sv_se', 'profiledescriptionml_tr_tr',
        'profiledescriptionml_pt_pt', 'profiledescriptionml_ja_jp',

        # Explizite Liste der zu entfernenden score_partwise-Felder
        'score_partwiseversion', 'score_partwiseidentificationcreatortype',
        'score_partwiseidentificationencodingsupportsattribute', 'score_partwiseidentificationencodingsupportselement',
        'score_partwiseidentificationencodingsupportstype', 'score_partwiseidentificationencodingsupportsvalue',
        'score_partwisedefaultsscalingmillimeters', 'score_partwisedefaultsscalingtenths',
        'score_partwisedefaultspage_layoutpage_height', 'score_partwisedefaultspage_layoutpage_width',
        'score_partwisedefaultspage_layoutpage_marginstype', 'score_partwisedefaultspage_layoutpage_marginsleft_margin',
        'score_partwisedefaultspage_layoutpage_marginsright_margin', 'score_partwisedefaultspage_layoutpage_marginstop_margin',
        'score_partwisedefaultspage_layoutpage_marginsbottom_margin', 'score_partwisedefaultssystem_layoutsystem_marginsleft_margin',
        'score_partwisedefaultssystem_layoutsystem_marginsright_margin', 'score_partwisedefaultssystem_layoutsystem_distance',
        'score_partwisedefaultssystem_layouttop_system_distance', 'score_partwisedefaultsappearanceline_widthtype',
        'score_partwisedefaultsappearanceline_width', 'score_partwisedefaultsappearancenote_sizetype',
        'score_partwisedefaultsappearancenote_size', 'score_partwisedefaultsappearancedistancetype',
        'score_partwisedefaultsappearancedistance', 'score_partwisedefaultsmusic_fontfont_family',
        'score_partwisedefaultsmusic_fontfont_size', 'score_partwisedefaultsword_fontfont_family',
        'score_partwisedefaultsword_fontfont_size', 'score_partwisedefaultslyric_fontfont_family',
        'score_partwisedefaultslyric_fontfont_size', 'score_partwisecreditpage', 'score_partwisecreditcredit_type',
        'score_partwisecreditcredit_wordsdefault_x', 'score_partwisecreditcredit_wordsdefault_y',
        'score_partwisecreditcredit_wordsfont_family', 'score_partwisecreditcredit_wordshalign',
        'score_partwisecreditcredit_wordsvalign', 'score_partwisecreditcredit_words',
        'score_partwisecreditcredit_wordsfont_size', 'score_partwisecreditcredit_wordsfont_weight',
        'score_partwisepart_listscore_partid', 'score_partwisepart_listscore_partpart_nameprint_object',
        'score_partwisepart_listscore_partpart_name', 'score_partwisepart_listscore_partpart_abbreviationprint_object',
        'score_partwisepart_listscore_partpart_abbreviation', 'score_partwisepart_listscore_partgroup',
        'score_partwisepart_listscore_partscore_instrumentid', 'score_partwisepart_listscore_partscore_instrumentinstrument_name',
        'score_partwisepart_listscore_partscore_instrumentinstrument_sound', 'score_partwisepart_listscore_partmidi_instrumentid',
        'score_partwisepart_listscore_partmidi_instrumentmidi_channel', 'score_partwisepart_listscore_partmidi_instrumentmidi_program',
        'score_partwisepart_listscore_partmidi_instrumentvolume', 'score_partwisepart_listscore_partmidi_instrumentpan',
        'score_partwisepartid', 'score_partwisepartmeasurenumber', 'score_partwisepartmeasurewidth',
        'score_partwisepartmeasureprintsystem_layoutsystem_marginsleft_margin', 'score_partwisepartmeasureprintsystem_layoutsystem_marginsright_margin',
        'score_partwisepartmeasureprintsystem_layouttop_system_distance', 'score_partwisepartmeasureprintmeasure_numberingmultiple_rest_always',
        'score_partwisepartmeasureprintmeasure_numberingmultiple_rest_range', 'score_partwisepartmeasureprintmeasure_numbering',
        'score_partwisepartmeasureattributesdivisions', 'score_partwisepartmeasureattributeskeyfifths',
        'score_partwisepartmeasureattributeskeymode', 'score_partwisepartmeasureattributestimebeats',
        'score_partwisepartmeasureattributestimebeat_type', 'score_partwisepartmeasureattributesclefsign',
        'score_partwisepartmeasureattributesclefline', 'score_partwisepartmeasureattributesmeasure_stylemultiple_rest',
        'score_partwisepartmeasuredirectionplacement', 'score_partwisepartmeasuredirectiondirection_typemetronomedefault_y',
        'score_partwisepartmeasuredirectiondirection_typemetronomefont_family', 'score_partwisepartmeasuredirectiondirection_typemetronomefont_size',
        'score_partwisepartmeasuredirectiondirection_typemetronomehalign', 'score_partwisepartmeasuredirectiondirection_typemetronomerelative_x',
        'score_partwisepartmeasuredirectiondirection_typemetronomebeat_unit', 'score_partwisepartmeasuredirectiondirection_typemetronomeper_minute',
        'score_partwisepartmeasuredirectionsoundtempo', 'score_partwisepartmeasuredirectiondirection_typerehearsaldefault_y',
        'score_partwisepartmeasuredirectiondirection_typerehearsalfont_size', 'score_partwisepartmeasuredirectiondirection_typerehearsalrelative_x',
        'score_partwisepartmeasuredirectiondirection_typerehearsal', 'score_partwisepartmeasurenoterestmeasure',
        'score_partwisepartmeasurenoteduration', 'score_partwisepartmeasurenotevoice',
        'score_partwisepartmeasuredirectiondirection_typedynamicsdefault_y', 'score_partwisepartmeasuredirectiondirection_typedynamicshalign',
        'score_partwisepartmeasuredirectiondirection_typedynamicsrelative_x', 'score_partwisepartmeasuredirectionsounddynamics',
        'score_partwisepartmeasurenotedefault_x', 'score_partwisepartmeasurenotepitchstep',
        'score_partwisepartmeasurenotepitchalter', 'score_partwisepartmeasurenotepitchoctave',
        'score_partwisepartmeasurenotetype', 'score_partwisepartmeasurenoteaccidental',
        'score_partwisepartmeasurenotestemdefault_y', 'score_partwisepartmeasurenotestem',
        'score_partwisepartmeasurenotebeamnumber', 'score_partwisepartmeasurenotebeam',
        'score_partwisepartmeasurenotenotationsarticulationsstaccatodefault_x', 'score_partwisepartmeasurenotenotationsarticulationsstaccatodefault_y',
        'score_partwisepartmeasurenotenotationsarticulationsstaccatoplacement', 'score_partwisepartmeasurenotenotationsslurbezier_x',
        'score_partwisepartmeasurenotenotationsslurbezier_y', 'score_partwisepartmeasurenotenotationsslurdefault_x',
        'score_partwisepartmeasurenotenotationsslurdefault_y', 'score_partwisepartmeasurenotenotationsslurnumber',
        'score_partwisepartmeasurenotenotationsslurplacement', 'score_partwisepartmeasurenotenotationsslurtype',
        'score_partwisepartmeasureprintnew_system', 'score_partwisepartmeasureprintsystem_layoutsystem_distance',
        'score_partwisepartmeasurebarlinelocation', 'score_partwisepartmeasurebarlinebar_style',
        'score_partwisepartmeasuredirectiondirection_typewordsdefault_y', 'score_partwisepartmeasuredirectiondirection_typewordsfont_size',
        'score_partwisepartmeasuredirectiondirection_typewords', 'score_partwisepartmeasurenotenotationsfermatadefault_x',
        'score_partwisepartmeasurenotenotationsfermatadefault_y', 'score_partwisepartmeasurenotenotationsfermatatype',
        'score_partwisepartmeasuredirectionoffset', 'score_partwisepartmeasuredirectiondirection_typewordsrelative_x',
        'score_partwisepartmeasurenotenotationsarticulationsaccentdefault_x', 'score_partwisepartmeasurenotenotationsarticulationsaccentdefault_y',
        'score_partwisepartmeasurenotenotationsarticulationsaccentplacement', 'score_partwisepartmeasurenotenotationsarticulationsstrong_accentdefault_x',
        'score_partwisepartmeasurenotenotationsarticulationsstrong_accentdefault_y', 'score_partwisepartmeasurenotenotationsarticulationsstrong_accentplacement',
        'score_partwisepartmeasurenotenotationsarticulationsstrong_accenttype', 'score_partwisepartmeasuredirectiondirection_typedynamicsdefault_x',

        # Bestehende Felder aus der Blockliste
        'bitsperpixel', 'filter', 'interlace', 'compobjusertypelen', 'template', 'word97', 'codepage', 'company',
        'part', 'timecreated', 'imagesize', 'hascolormap', 'exiftoolversion', 'ziprequiredversion',
        'zipbitflag', 'zipcrc', 'zipcompressedsize', 'zipuncompressedsize', 'zipfilename',
        'ffprobe_format_probe_score', 'application', 'appversion', 'numcolors', 'numimportantcolors',
        'planes', 'thumbnailoffset', 'thumbnaillength', 'quality', 'sharpness', 'whitebalance',
        'fujiflashmode', 'macro', 'focusmode', 'slowsync', 'picturemode', 'autobracketing',
        'focuswarning', 'exposurewarning', 'avgbytespersec', 'filelength', 'datapackets',
        'sendduration', 'preroll', 'flags', 'minpacketsize', 'maxpacketsize', 'timeoffset',
        'streamnumber', 'audiocodecdescription', 'wmfsdkneeded', 'wmfsdkversion', 'graphicsmode',
        'opcolor', 'vendorid', 'handlerclass', 'audiovendorid', 'version', 'channelmode',
        'colormode', 'bytes', 'currentuser', 'exifbyteorder', 'stripoffsets', 'samplesperpixel',
        'rowsperstrip', 'stripbytecounts', 'planarconfiguration', 'resolutionunit', 'fillorder',
        'orientation', 'predictor', 'sampleformat', 'id', 'xmlns', 'viewbox', 'fill',
        'primarychromaticities', 'whitepoint', 'pagenumber', 'id3size', 'intensitystereo',
        'msstereo', 'audiolayer', 'mpegaudioversion', 'fileid', 'mcdi', 'tsse', 'copyrightflag',
        'originalmedia', 'resourceforksize', 'mediadataoffset', 'trackid', 'trackvolume',
        'nexttrackid', 'matrixstructure', 'preferredrate', 'preferredvolume', 'previewtime',
        'previewduration', 'postertime', 'selectiontime', 'selectionduration', 'devicemanufacturer',
        'deviceattributes', 'renderingintent', 'connectionspaceilluminant', 'profilecreator',
        'profiledescription', 'profilecopyright', 'mediawhitepoint', 'redmatrixcolumn',
        'greenmatrixcolumn', 'bluematrixcolumn', 'chromaticadaptation', 'cmmflags', 'makeandmodel',
        'profilename', 'devicemodel', 'mediablackpoint', 'devicemfgdesc', 'devicemodeldesc',
        'viewingconddesc', 'viewingcondilluminant', 'viewingcondsurround', 'viewingcondilluminanttype',
        'luminance', 'measurementobserver', 'measurementbacking', 'measurementflare', 'measurementilluminant',
        'technology', 'image_icc_profile_description', 'videocardgamma', 'nativedisplayinfo', 'colormap',
        'profilecmmtype', 'profileversion', 'profileclass', 'profileconnectionspace', 'profiledatetime',
        'profilefilesignature', 'redtrc', 'greentrc', 'bluetrc', 'lyrics', 'artisturl', 'comment',
        'comments', 'commercialurl', 'notes', 'artist', 'minorversion', 'compatiblebrands',
        'ffprobe_format_start_time', 'minor_version', 'creation_time', 'compatible_brands',
        'major_brand', 'handler_name', 'currenttime', 'trackcreatedate', 'trackmodifydate',
        'trackduration', 'handlervendorid', 'ebmlversion', 'ebmlreadversion', 'doctypereadversion',
        'timecodescale', 'muxingapp', 'writingapp', 'tracknumber', 'trackuid', 'tracklanguage',
        'codecid', 'tracktype', 'tagtrackuid', 'handlername', 'streamcount', 'framecount',
        'videoframecount', 'videoencoding', 'aspectratiox', 'aspectratioy', 'videocodecname',
        'errorcorrectiontype', 'wm_encodingsettings', 'modeextension', 'theoraversion', 'colorspace',
        'pixelformat', 'majorbrand', 'mxfversion', 'containerlastmodifydate', 'sdkversion',
        'objectmodelversion', 'applicationsuppliername', 'applicationname', 'applicationversionnumber',
        'applicationversionstring', 'toolkitversion', 'packagelastmodifydate', 'starttimecode',
        'roundedtimecodetimebase', 'dropframe', 'sampledwidth', 'sampledheight', 'componentdepth',
        'horizontalsubsampling', 'verticalsub_sampling', 'colorsiting', 'videolinemap',
        'presentationaspectratio', 'videocodingschemeid', 'profileandlevel', 'lowdelayindicator',
        'closedgopindicator', 'maximumgopsize', 'editrate', 'origin', 'componentdatadefinition',
        'linkedtrackid', 'lockedindicator', 'blockalign', 'averagebytespersecond', 'essencestreamid',
        'indexstreamid', 'audiostreamtype', 'redcodeversion', 'startedgecode', 'serialnumber',
        'colortemperature', 'cameratype', 'reelnumber', 'take', 'firmwareversion', 'storagetype',
        'storageserialnumber', 'storageformatdate', 'storageformattime', 'croparea', 'iso',
        'videoformat', 'rgbcurves', 'originalframerate', 'focusdistance', 'model', 'brain',
        'sensor', 'focallength35efl', 'numsampleframes', 'too', '_temp_bit_depth', 'blocksizemin',
        'blocksizemax', 'framesizemin', 'framesizemax', 'totalsamples', 'md5signature', 'vendor',
        'opusversion', 'outputgain', 'nominalbitrate', 'bpmbeatsperminute', 'bpm_beats_per_minute',
        'wma_file_id', 'error_correction_type', 'streamtype', 'handlertype', 'mediatimescale',
        'doctype', 'doctypeversion', 'filesizebytes', 'aspectratio', 'track', 'picturemimetype',
        'picturetype', 'length', 'samplesize', 'wcom_http_www_atlantic_records_com',
        'comm_musicmatch_bio_eng', 'uslt_eng', 'woar_www_matchmboxtwenty_com', 'comm_eng',
        'comm_id3v1_comment_eng', 'trck', 'tlen', 'tit2', 'tcop', 'tpe1', 'talb', 'tcon', 'tdrc',
        'wm_tracknumber', 'wm_composer', 'wm_genre', 'wm_track', 'wm_lyrics', 'wm_mcdi', 'wcom', 'woar'
    }

    # Schritt 1: Standardisiere alle eingehenden Schlüssel
    standardized_metadata = {sanitize_tag(k): v for k, v in metadata.items()}

    unified_metadata = {}
    processed_standardized_keys = set()

    # Schritt 2: Markiere alle Felder aus der Blockliste als "verarbeitet", damit sie ignoriert werden.
    # Dies ist die zentrale, funktionierende Logik Ihres Skripts.
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
        ("filesize", "size"): "size",
        ("filetypeextension", "filetype", "extension"): "extension",
        ("mimetype", "mime_type", "format"): "mime_type",
        ("newlines", "lineending"): "document_line_break",
        ("createdate", "datetimeoriginal", "creationdate", "date", "mediacreatedate", "creation_date", "creationtime", "asset_created_date_combined", "datecreated", "Creation_time", "CreationDate", "Creation-date", "CreateDate", "MediaCreateDate", "CreationTime"): "asset_created_date",
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
        ("format_version", "identification", "pdf_version", "pdfversion", "jfifversion", "gifversion", "bmpversion", "doctypeversion"): "document_format_version",
        ("hostcomputer", "system", "primaryplatform"): "operating_system",
        ("note", "doctype"): "document_format_descriptive_name",
        ("duration", "ffprobe_format_duration", "mediaduration"): "duration",
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
    Diese Funktion bereinigt Werte von ungültigen XML-Zeichen UND filtert
    unerwünschte Tags an der letzten möglichen Stelle heraus.
    """
    # Blockliste der exakten standardisierten Tags, die entfernt werden sollen.
    blocklist = {'timescale', 'handlerdescription', 'audiobitspersample'}

    for k, v in metadata.items():
        tag = sanitize_tag(k)

        # FINALE UND ENDGÜLTIGE FILTERLOGIK:
        # Wenn der Tag in der Blockliste ist oder mit einem der unerwünschten
        # Präfixe beginnt, wird er übersprungen und landet NICHT in der XML-Datei.
        if (tag in blocklist or
                tag.startswith('score_partwise') or
                tag.startswith('registration') or
                tag.startswith('statemachine')):
            continue

        # Sanitize den Wert, bevor er dem XML hinzugefügt wird
        clean_v = sanitize_for_xml(v)

        # Überspringe bekannte binäre ASF/WMA-Attribute, die XML ungültig machen können
        if '[ASFByteArrayAttribute' in clean_v:
            continue

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


def process_file(file_path, relative_path, structured_warnings, structured_unidentified):
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
    all_raw_metadata["sha512"] = hash_sha512(file_path)

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
        matches = rules.match(str(file_path))
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
    known_video_suffixes = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".3gp", ".mxf", ".r3d"}

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
        # Hole den finalen, vereinheitlichten MIME-Typ
        final_mime_type = final_unified_metadata.get("mime_type", "").lower()

        # Erlaube 'duration' nur für Audio, Video und animierte GIFs.
        # Bei allen anderen Dateitypen (z.B. image/jpeg) wird es entfernt.
        if not (final_mime_type.startswith('audio/') or
                final_mime_type.startswith('video/') or
                final_mime_type == 'image/gif'):
            print(f"Info: Entferne 'duration' ({final_unified_metadata['duration']}) für unpassenden MIME-Typ: {final_mime_type}")
            del final_unified_metadata['duration']

    if 'audio_channel_count' in final_unified_metadata:
        final_mime_type = final_unified_metadata.get("mime_type", "").lower()

        # Erlaube 'audio_channel_count' nur für Audio- und Videodateien.
        if not (final_mime_type.startswith('audio/') or
                final_mime_type.startswith('video/')):
            print(f"Info: Entferne 'audio_channel_count' ({final_unified_metadata['audio_channel_count']}) für unpassenden MIME-Typ: {final_mime_type}")
            del final_unified_metadata['audio_channel_count']

    print(f"\n--- Vereinheitlichte Metadaten für {relative_path} (final) ---")
    for k, v in final_unified_metadata.items():
        print(f"  {k}: {v}")
    print("--------------------------------------------------")

    add_metadata_to_xml(file_elem, final_unified_metadata)

    file_path_str = str(file_path)
    if file_path_str in structured_warnings:
        warnings_elem = ET.SubElement(file_elem, "brunhilde_warnings")
        for warning_detail in structured_warnings[file_path_str]:
            warning_item_elem = ET.SubElement(warnings_elem, "warning_item")
            for k, v in warning_detail.items():
                ET.SubElement(warning_item_elem, sanitize_tag(k)).text = str(v)

    if file_path_str in structured_unidentified:
        ET.SubElement(file_elem, "brunhilde_unidentified_status").text = "Yes"

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
    audio_suffixes = {".mp3", ".wav", ".flac", ".ogg", ".aac", ".m4a", ".wma"}
    video_suffixes = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".mxf", ".r3d"}
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

    print(f"\n--- Starte umfassenden Brunhilde-Scan für das Verzeichnis: {BASE_DIR} ---")
    global_brunhilde_data = extract_brunhilde_info(Path(BASE_DIR))
    print(f"--- Brunhilde-Scan für das Verzeichnis abgeschlossen ---")

    structured_warnings = global_brunhilde_data.get('structured_siegfried_warnings', {})
    structured_unidentified = global_brunhilde_data.get('structured_unidentified_files', set())

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
                process_file(file_path, relative_path, structured_warnings, structured_unidentified)
                processed_count += 1
            except Exception as e:
                print(f"Ein unerwarteter Fehler ist aufgetreten beim Verarbeiten von {file_path}: {e}")
                ET.SubElement(root, "file", {"path": relative_path.as_posix(), "name": relative_path.name, "error": str(e)})

    if processed_count > 0:
        write_xml_to_file(root, OUTPUT_XML)
        print(f"\n{processed_count} Dateien verarbeitet.")
    else:
        print("\nKeine Dateien zum Verarbeiten gefunden oder alle übersprungen.")


if __name__ == "__main__":
    main()