# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT


# J_generate_premis_win.py
# ==============================================================================
# Skript zur automatischen Generierung einer PREMIS v3 XML-Datei.
#
# Autor: Ihr Name / Ihre Abteilung
# Datum: 2025-12-15
# Version: 22.0 - MULTI-FORMAT SUPPORT (FTK IMAGER + GREASEWEAZLE + REDUMPER)
#                 1. AUTO-WEICHE: Erkennt nun auch Optical Discs (Redumper Logs).
#                 2. FTK-PARSER: Extrahiert Metadaten (Tableau, Hashes, SN) aus FTK Logs.
#                 3. REDUMPER-PARSER: Extrahiert Metadaten aus Audio-CD Rips.
#
# Benötigt: lxml (pip install lxml), requests (pip install requests)
# ==============================================================================

import sys
import re
import os
import csv
import subprocess
import hashlib
import requests
import glob
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from lxml import etree

# --- UTF-8 für Windows-Konsole ---
if sys.platform == "win32":
    try:
        sys.stdin.reconfigure(encoding='utf-8')
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# --- NAMESPACES ---
NSMAP = {
    'premis': "http://www.loc.gov/premis/v3",
    'xsi': "http://www.w3.org/2001/XMLSchema-instance",
    'ft': "info:onb.ac.at/filetrove-schema/v1",
    'gwf': "info:onb.ac.at/greaseweazle-format-schema/v1"
}
PREMIS = '{' + NSMAP['premis'] + '}'
XSI = '{' + NSMAP['xsi'] + '}'
FT = '{' + NSMAP['ft'] + '}'
GWF = '{' + NSMAP['gwf'] + '}'

SCHEMA_LOCATION = "http://www.loc.gov/premis/v3 https://www.loc.gov/standards/premis/v3/premis-v3-0.xsd"

# ==============================================================================
# NEU: MEDIA CONTEXT & PARSER (Die "Weiche")
# ==============================================================================

class MediaContext:
    def __init__(self):
        self.media_type = "unknown"
        self.carrier_label = "Physical Medium"
        self.image_type_label = "Disk Image"
        self.tool_agent = None
        self.user_agent = None
        self.hardware_agent = None  # Neu für Tableau/Hardware
        self.original_hardware = None # Neu für Stick Modell/SN
        self.creation_date = datetime.now().isoformat()
        self.has_flux_stream = False
        self.metadata = {}
        self.image_hashes = {}
        self.log_content = ""

def parse_date_robust(date_str):
    """
    Versucht englische Datumsstrings von FTK (Wed Nov 26...) robust zu parsen,
    unabhängig von der System-Locale.
    """
    # Mapping für englische Monatsnamen
    months = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    try:
        # Entferne Wochentage und bereinige Spaces
        # Format erwartet: "Nov 26 07:24:09 2025" (nach Entfernung von Wed)
        parts = date_str.split()
        # FTK Format: DayName Month Day Time Year -> Teile: 0=DayName, 1=Month, 2=Day, 3=Time, 4=Year
        if len(parts) >= 5:
            mon_str = parts[1]
            day_str = parts[2]
            time_str = parts[3]
            year_str = parts[4]
            
            mon = months.get(mon_str, 1)
            dt = datetime(int(year_str), mon, int(day_str), 
                          int(time_str[:2]), int(time_str[3:5]), int(time_str[6:8]))
            return dt.isoformat()
    except Exception:
        pass
    # Fallback: Versuche Standard-Parsing
    try:
        return datetime.strptime(date_str, "%c").isoformat()
    except:
        return datetime.now().isoformat()

def parse_ftk_log(log_path):
    ctx = MediaContext()
    ctx.media_type = "usb_stick"
    ctx.carrier_label = "Physical USB Mass Storage Device"
    ctx.image_type_label = "Forensic Disk Image (Raw)"
    ctx.has_flux_stream = False
    
    content = ""
    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"WARNUNG: Konnte Log nicht lesen: {e}")
        return ctx

    ctx.log_content = content

    # 1. Software Agent (Header)
    if m := re.search(r"Created By (Exterro.*?Imager [\d\.]+)", content):
        ver = m.group(1)
        ctx.tool_agent = (f"SW_{ver.replace(' ','_')}", ver, "software")
    else:
        ctx.tool_agent = ("SW_FTK_Imager", "Exterro FTK Imager", "software")

    # 2. Hardware Agent (Write Blocker aus Notes)
    # Sucht nach "Tableau" in den Notes
    if m := re.search(r"Notes:.*?(Tableau Forensic Bridge.*?)(\.|\n|$)", content, re.IGNORECASE):
        hw_name = m.group(1).strip()
        ctx.hardware_agent = ("HW_Tableau_WriteBlocker", hw_name, "hardware")
    
    # 3. Original Hardware (Stick Modell & Serial)
    model = "Unknown Model"
    serial = "Unknown SN"
    if m := re.search(r"Drive Model:\s*(.*)", content):
        model = m.group(1).strip()
    if m := re.search(r"Drive Serial Number:\s*(.*)", content):
        serial = m.group(1).strip()
    
    if model != "Unknown Model":
        ctx.original_hardware = f"{model} (SN: {serial})"

    # 4. User Agent (Examiner)
    if m := re.search(r"Examiner:\s*(.*)", content):
        ex = m.group(1).strip()
        if ex:
            ctx.user_agent = (ex.replace(' ', '_'), ex, 'person')

    # 5. Datum (Acquisition finished)
    if m := re.search(r"Acquisition finished:\s*(.*)", content):
        ctx.creation_date = parse_date_robust(m.group(1).strip())

    # 6. Hashes (Nur aus Verification Results!)
    # Wir schneiden den Teil ab "Image Verification Results" aus
    if "Image Verification Results:" in content:
        verify_block = content.split("Image Verification Results:")[1]
        
        if m := re.search(r"MD5 checksum:\s*([a-fA-F0-9]+)", verify_block):
            ctx.image_hashes['MD5'] = m.group(1)
        if m := re.search(r"SHA1 checksum:\s*([a-fA-F0-9]+)", verify_block):
            ctx.image_hashes['SHA1'] = m.group(1)

    return ctx

def parse_redumper_log(log_path):
    """
    Parst Logs von Redumper (Audio CD / Optical Media).
    Erwartet Header format: === YYYY-MM-DD HH:MM:SS ===
    """
    ctx = MediaContext()
    ctx.media_type = "optical_disc"
    ctx.carrier_label = "Optical Disc (CD/DVD)"
    ctx.image_type_label = "Disk Image (Binary/Cue)"
    ctx.has_flux_stream = False
    
    content = ""
    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"WARNUNG: Konnte Redumper Log nicht lesen: {e}")
        return ctx

    ctx.log_content = content

    # 1. Datum (Erste Zeile: === 2025-12-10 10:03:22 ===)
    if m := re.search(r"^===\s+(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", content, re.MULTILINE):
        try:
            dt = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
            ctx.creation_date = dt.isoformat()
        except:
            pass

    # 2. Software Agent
    if m := re.search(r"(redumper\s+\(build:\s+.*?\))", content):
        ver = m.group(1).strip()
        # Clean Version String (Leerzeichen durch Underscore für ID)
        ver_clean = re.sub(r'[^\w\s\.\-]', '', ver).replace(' ', '_')
        ctx.tool_agent = (f"SW_{ver_clean}", ver, "software")
    else:
        ctx.tool_agent = ("SW_Redumper", "Redumper", "software")

    # 3. Hardware Agent (Laufwerk)
    if m := re.search(r"drive:\s+(.*)", content):
        hw = m.group(1).strip()
        ctx.hardware_agent = ("HW_OpticalDrive", hw, "hardware")

    # 4. Hashes (XML Style Tag <rom ... />)
    # Suche nach: <rom name="AudioCD.bin" size="..." crc="..." md5="..." sha1="..." />
    if m := re.search(r'<rom\s+name=".*?"\s+.*?>', content):
        tag_content = m.group(0)
        
        # MD5
        if match_md5 := re.search(r'md5="([a-fA-F0-9]+)"', tag_content, re.IGNORECASE):
            ctx.image_hashes['MD5'] = match_md5.group(1)
        
        # SHA1
        if match_sha1 := re.search(r'sha1="([a-fA-F0-9]+)"', tag_content, re.IGNORECASE):
            ctx.image_hashes['SHA1'] = match_sha1.group(1)

    return ctx

def parse_greaseweazle_log(log_path):
    ctx = MediaContext()
    ctx.media_type = "floppy"
    ctx.carrier_label = "Physical 3.5 inch Floppy Disk"
    ctx.image_type_label = "Disk Image (Sector copy)"
    ctx.has_flux_stream = True 
    
    content = ""
    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"WARNUNG: Konnte Log nicht lesen: {e}")
        return ctx

    ctx.log_content = content
    m = re.search(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", content)
    if m:
        ctx.creation_date = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S").isoformat()

    if m := re.search(r"User: (.*)", content):
        aid = m.group(1).strip()
        ctx.user_agent = (aid, aid, 'person')

    if m := re.search(r"Host Tools: ([\d\.]+)", content):
        ver = m.group(1)
        ctx.tool_agent = (f"SW_Greaseweazle_Host_Tools_{ver}", f"Greaseweazle Tools {ver}", "software")
    else:
        ctx.tool_agent = ("SW_Greaseweazle_Unknown", "Greaseweazle Tools", "software")

    if m := re.search(r"SHA-512-Hashes:\s*\n(.*?)(?:\n\n|\Z)", content, re.DOTALL):
        for l in m.group(1).split('\n'):
            if ':' in l:
                p = l.split(':', 1)
                ctx.image_hashes[p[0].strip()] = p[1].strip()

    if m := re.search(r"Cylinders: (\d+)", content):
        ctx.metadata["Cylinders"] = m.group(1)
    if m := re.search(r"Heads: (\d+)", content):
        ctx.metadata["Heads"] = m.group(1)

    return ctx

def analyze_source_media(step1_path):
    if not step1_path.exists():
        print("WARNUNG: Step 1 Ordner nicht gefunden. Nutze leeren Context.")
        return MediaContext()

    # Suche nach Log-Dateien
    log_candidates = list(step1_path.glob("*image-log.txt"))
    
    if log_candidates:
        log_file = log_candidates[0]
        # Datei anlesen, um Typ zu bestimmen
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                head = f.read(1024) # Lese ersten KB
                
            if "Exterro" in head or "FTK" in head:
                print(f"   [INFO] Modus erkannt: USB-STICK (FTK Imager Log gefunden)")
                return parse_ftk_log(log_file)
            elif "redumper" in head.lower():
                print(f"   [INFO] Modus erkannt: OPTICAL DISC (Redumper Log gefunden)")
                return parse_redumper_log(log_file)
            else:
                print(f"   [INFO] Modus erkannt: DISKETTE (Greaseweazle/Standard Log)")
                return parse_greaseweazle_log(log_file)
        except Exception as e:
            print(f"WARNUNG: Fehler bei der Log-Erkennung: {e}")
            return MediaContext()

    dd_map = list(step1_path.glob("*.map"))
    if dd_map:
        print(f"   [INFO] Modus erkannt: FESTPLATTE (ddrescue Mapfile gefunden)")
        ctx = MediaContext()
        ctx.media_type = "hdd"
        ctx.carrier_label = "Physical Mass Storage Device"
        ctx.has_flux_stream = False
        return ctx

    print("   [WARNUNG] Kein bekanntes Imaging-Log gefunden. Standard-Modus.")
    return MediaContext()


# ==============================================================================
# HAUPTKLASSE
# ==============================================================================

class PremisGenerator:
    def __init__(self, ac_number, disk_id):
        self.ac_number = ac_number
        self.disk_id = disk_id
        
        self.path_root = Path.home() / "Documents/data" / self.ac_number / self.disk_id
        self.path_step0 = self.path_root / f"0_{self.disk_id}_picture-carrier"
        self.path_step1 = self.path_root / f"1_{self.disk_id}_image-LZA"
        self.path_step2 = self.path_root / f"2_{self.disk_id}_extracted-files"
        self.path_step3 = self.path_root / f"3_{self.disk_id}_for-transfer"
        self.path_step5_lza = self.path_root / f"5_{self.disk_id}_LZA"
        
        self.source_image_id = f"01_{self.disk_id}.img"

        self.ctx = analyze_source_media(self.path_step1)

        self.agent_ids = set()
        self.xml_objects = []
        self.xml_events = []
        self.xml_agents = []
        self.xml_rights = []
        
        self.archived_file_ids = []
        self.original_extracted_files = []

        self.AGENT_DEFS = {
            "PYTHON_CONVERSION": ("SW_InternalPythonScripts_Conversion", "Internal Python Conversion Scripts", "software"),
            "BRUNNHILDE": ("SW_Brunnhilde", "Brunnhilde File Characterization Tool", "software"),
            "INSTITUTION": ("WBR", "Wienbibliothek im Rathaus", "organization"),
            "METADATA_EXTRACTOR": ("SW_InternalPythonScripts_Metadata", "Internal Python Metadata Extraction Scripts", "software")
        }

        self.root = etree.Element(PREMIS + 'premis', nsmap=NSMAP, version="3.0")
        self.root.set(XSI + 'schemaLocation', SCHEMA_LOCATION)

        print(f"INFO: PREMIS Generator (Universal V22.0) für '{self.disk_id}' initialisiert.")
        if not self.path_root.exists():
            print(f"FATALER FEHLER: Hauptverzeichnis nicht gefunden: {self.path_root}")
            sys.exit(1)

        # --- URHEBER AUSWAHL ---
        print("\n--- URHEBER AUSWAHL ---")
        raw_input_name = input("Bitte Namen des Urhebers eingeben (z.B. 'Brigitte Hamann'): ")
        
        gnd_data = self._search_and_select_gnd_agent(raw_input_name)
        
        if gnd_data:
            self.creator_gnd_id = gnd_data['id']
            self.creator_name = gnd_data['name']
            self.creator_agent_id = f"creator_{self.creator_gnd_id}"
            print(f"\033[92m -> Urheber '{self.creator_name}' mit GND-ID {self.creator_gnd_id} ausgewählt.\033[0m")
        else:
            if not raw_input_name:
                raw_input_name = "Unknown Creator"
            
            self.creator_name = raw_input_name.strip()
            clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', self.creator_name.replace(' ', '_'))
            self.creator_agent_id = f"creator_{clean_name}"
            print(f"\033[93m -> WARNUNG: Kein GND-Eintrag gewählt. Lokal: {self.creator_agent_id}\033[0m")

    def _get_sha512(self, path):
        if not path.exists(): return None
        h = hashlib.sha512()
        with open(path, 'rb') as f:
            while c := f.read(8192): h.update(c)
        return h.hexdigest()

    def _add_simple(self, parent, tag, value, ns=PREMIS):
        if parent is None: return None
        if value:
            elem = etree.SubElement(parent, ns + tag)
            elem.text = str(value)
            return elem
        return None

    # --- VERBESSERTE GND SUCHE (V20.5 DETAIL ANSICHT) ---
    def _search_and_select_gnd_agent(self, initial_name):
        current_search_term = initial_name
        
        while True:
            if not current_search_term.strip():
                return None

            try:
                parts = current_search_term.split()
                if not parts:
                    query_str = f'PER = "{current_search_term}"'
                else:
                    query_parts = [f'PER = "{p}"' for p in parts]
                    query_str = " and ".join(query_parts)

                print(f"Suche bei DNB nach: {query_str} ...")

                r = requests.get("https://services.dnb.de/sru/authorities", 
                                 params={"version": "1.1", 
                                         "operation": "searchRetrieve", 
                                         "query": query_str, 
                                         "maximumRecords": "10", 
                                         "recordSchema": "MARC21-xml"}, 
                                 timeout=10)
                r.raise_for_status()
                root = ET.fromstring(r.content)
                ns = {'marc': 'http://www.loc.gov/MARC21/slim'}
                recs = root.findall('.//marc:record', ns)
                
                results = []
                if recs:
                    print("\nGefundene GND-Einträge:")
                    for i, rec in enumerate(recs):
                        try:
                            # 1. Basis-Daten (ID, Name)
                            id_node = rec.find('./marc:controlfield[@tag="001"]', ns)
                            if id_node is None: continue 
                            gid = id_node.text
                            
                            name_node = rec.find('./marc:datafield[@tag="100"]/marc:subfield[@code="a"]', ns)
                            if name_node is None: continue
                            n = name_node.text
                            
                            # Lebensdaten
                            d = rec.find('./marc:datafield[@tag="100"]/marc:subfield[@code="d"]', ns)
                            ds = f"({d.text})" if (d is not None and d.text) else ""

                            # 2. Entitäts-Typ (Feld 075 $b) - WICHTIG ZUR UNTERSCHEIDUNG
                            type_label = "Unbekannt"
                            f075 = rec.find('./marc:datafield[@tag="075"]/marc:subfield[@code="b"]', ns)
                            if f075 is not None:
                                c = f075.text
                                if c == 'p': type_label = "Person"
                                elif c == 'b': type_label = "Körperschaft"
                                elif c == 'f': type_label = "Kongress"
                                elif c == 'g': type_label = "Ort"
                                elif c == 's': type_label = "Sachbegriff"
                                elif c == 'w': type_label = "Werk"

                            # 3. Check auf Werktitel im Namensfeld (100 $t) - Indikator für Werk
                            title_part = rec.find('./marc:datafield[@tag="100"]/marc:subfield[@code="t"]', ns)
                            if title_part is not None:
                                type_label = "Werk/Titel"
                                n = f"{n} : {title_part.text}"

                            # 4. Zusatz-Infos (Beruf/Funktion aus Feld 550 $a)
                            infos = []
                            for f550 in rec.findall('./marc:datafield[@tag="550"]', ns):
                                sub_a = f550.find('./marc:subfield[@code="a"]', ns)
                                if sub_a is not None and sub_a.text:
                                    infos.append(sub_a.text)
                            
                            # Nur die ersten 2 Berufe anzeigen, um Konsole nicht zu sprengen
                            info_str = ", ".join(infos[:2])
                            if info_str: info_str = f" | Info: {info_str}"

                            # Ausgabe formatieren
                            print(f"  {len(results)+1}: {n} {ds} | [Typ: {type_label}]{info_str} [ID: {gid}]")
                            results.append({'id': gid, 'name': n})

                        except Exception:
                            continue 
                            
                else:
                    print(f"\033[91mKeine Treffer für '{current_search_term}'.\033[0m")

                print("\nOptionen:")
                if results:
                    print("  1-N: Eintrag auswählen")
                print("  s:   Neue Suche (Tippfehler korrigieren)")
                print("  x:   Ohne GND fortfahren (Lokal)")
                
                choice = input("Deine Wahl: ").strip().lower()

                if choice == 's':
                    current_search_term = input("\nNeuer Suchbegriff: ")
                    continue 
                elif choice == 'x':
                    return None
                elif choice.isdigit():
                    idx = int(choice)
                    if 0 < idx <= len(results):
                        return results[idx-1]
                    else:
                        print("Ungültige Nummer.")
                else:
                    print("Ungültige Eingabe.")

            except Exception as e:
                print(f"Netzwerk/API-Fehler bei der GND-Abfrage: {e}")
                if input("Nochmal versuchen? (j/n): ").lower() != 'j':
                    return None

    # --- XML WRITER ---
    def create_xml_object(self, obj_type, identifier_val, 
                         preservation_level=None, 
                         sig_props=None, 
                         size=None, fixity_list=None, format_info=None, creating_app=None, filetrove_dict=None,
                         original_name=None, relationships=None):
        
        obj = etree.Element(PREMIS + 'object')
        obj.set(XSI + 'type', f"premis:{obj_type}")

        # 1. Identifier
        oid = etree.SubElement(obj, PREMIS + 'objectIdentifier')
        self._add_simple(oid, 'objectIdentifierType', 'local')
        self._add_simple(oid, 'objectIdentifierValue', identifier_val)

        # 2. Preservation Level
        if preservation_level:
            pl = etree.SubElement(obj, PREMIS + 'preservationLevel')
            self._add_simple(pl, 'preservationLevelType', 'long-term preservation')
            self._add_simple(pl, 'preservationLevelValue', preservation_level)
            self._add_simple(pl, 'preservationLevelRole', 'required')

        # 3. Significant Properties
        if sig_props:
            for stype, sval in sig_props:
                sp = etree.SubElement(obj, PREMIS + 'significantProperties')
                self._add_simple(sp, 'significantPropertiesType', stype)
                self._add_simple(sp, 'significantPropertiesValue', sval)

        # 4. Object Characteristics
        if obj_type in ['file', 'bitstream']:
            has_char_data = (size is not None) or (fixity_list) or (format_info) or (creating_app) or (filetrove_dict)
            
            if has_char_data:
                char = etree.SubElement(obj, PREMIS + 'objectCharacteristics')
                
                # Fixity
                if fixity_list:
                    for algo, digest in fixity_list:
                        if digest:
                            fix = etree.SubElement(char, PREMIS + 'fixity')
                            self._add_simple(fix, 'messageDigestAlgorithm', algo)
                            self._add_simple(fix, 'messageDigest', digest)

                # Size
                if size is not None:
                    self._add_simple(char, 'size', size)

                # Format
                if format_info:
                    fmt = etree.SubElement(char, PREMIS + 'format')
                    if format_info[0]:
                        des = etree.SubElement(fmt, PREMIS + 'formatDesignation')
                        self._add_simple(des, 'formatName', format_info[0])
                    if format_info[2]: 
                        reg = etree.SubElement(fmt, PREMIS + 'formatRegistry')
                        self._add_simple(reg, 'formatRegistryName', format_info[1] or 'PRONOM')
                        self._add_simple(reg, 'formatRegistryKey', format_info[2])

                # Creating Application
                if creating_app:
                    ca = etree.SubElement(char, PREMIS + 'creatingApplication')
                    if creating_app[0]: self._add_simple(ca, 'creatingApplicationName', creating_app[0])
                    if creating_app[1]: self._add_simple(ca, 'dateCreatedByApplication', creating_app[1])

                # Extension
                if filetrove_dict:
                    ext = etree.SubElement(char, PREMIS + 'objectCharacteristicsExtension')
                    ft = etree.SubElement(ext, FT + 'filetrove_metadata', nsmap={'ft': NSMAP['ft']})
                    for k, v in filetrove_dict.items():
                        if k not in ['sha512', 'size', 'pronom_id', 'document_creator_tool', 'asset_created_date']:
                            elem = etree.SubElement(ft, FT + k)
                            elem.text = str(v)

        # 5. Original Name
        if original_name:
            self._add_simple(obj, 'originalName', original_name)

        # 6. Relationships
        if relationships:
            for rel_type, rel_subtype, rel_obj_id, rel_evt_id in relationships:
                rel = etree.SubElement(obj, PREMIS + 'relationship')
                self._add_simple(rel, 'relationshipType', rel_type)
                if rel_subtype: self._add_simple(rel, 'relationshipSubType', rel_subtype)
                
                if rel_obj_id:
                    roi = etree.SubElement(rel, PREMIS + 'relatedObjectIdentifier')
                    self._add_simple(roi, 'relatedObjectIdentifierType', 'local')
                    self._add_simple(roi, 'relatedObjectIdentifierValue', rel_obj_id)
                
                if rel_evt_id:
                    rei = etree.SubElement(rel, PREMIS + 'relatedEventIdentifier')
                    self._add_simple(rei, 'relatedEventIdentifierType', 'local')
                    self._add_simple(rei, 'relatedEventIdentifierValue', rel_evt_id)

        self.xml_objects.append(obj)

    def create_xml_event(self, eid, etype, outcome, detail, date, agents, objects):
        evt = etree.Element(PREMIS + 'event')
        
        i = etree.SubElement(evt, PREMIS + 'eventIdentifier')
        self._add_simple(i, 'eventIdentifierType', 'local')
        self._add_simple(i, 'eventIdentifierValue', eid)
        
        self._add_simple(evt, 'eventType', etype)
        self._add_simple(evt, 'eventDateTime', date)
        
        oi = etree.SubElement(evt, PREMIS + 'eventOutcomeInformation')
        self._add_simple(oi, 'eventOutcome', outcome)
        od = etree.SubElement(oi, PREMIS + 'eventOutcomeDetail')
        self._add_simple(od, 'eventOutcomeDetailNote', detail)
        
        for aid in agents:
            lai = etree.SubElement(evt, PREMIS + 'linkingAgentIdentifier')
            self._add_simple(lai, 'linkingAgentIdentifierType', 'local')
            self._add_simple(lai, 'linkingAgentIdentifierValue', aid)
            
        for oid, role in objects:
            loi = etree.SubElement(evt, PREMIS + 'linkingObjectIdentifier')
            self._add_simple(loi, 'linkingObjectIdentifierType', 'local')
            self._add_simple(loi, 'linkingObjectIdentifierValue', oid)
            if role: self._add_simple(loi, 'linkingObjectRole', role)
            
        self.xml_events.append(evt)

    def create_xml_agent(self, aid, name, atype, gnd=None):
        if aid in self.agent_ids: return
        agt = etree.Element(PREMIS + 'agent')
        
        i = etree.SubElement(agt, PREMIS + 'agentIdentifier')
        self._add_simple(i, 'agentIdentifierType', 'local')
        self._add_simple(i, 'agentIdentifierValue', aid)
        
        if gnd:
            ig = etree.SubElement(agt, PREMIS + 'agentIdentifier')
            self._add_simple(ig, 'agentIdentifierType', 'gnd')
            self._add_simple(ig, 'agentIdentifierValue', gnd)
            
        self._add_simple(agt, 'agentName', name)
        self._add_simple(agt, 'agentType', atype)
        
        self.xml_agents.append(agt)
        self.agent_ids.add(aid)

    # --- STEPS (MODULARIZED) ---

    def step_agents(self):
        print("\n[1/7] Definiere Agenten...")
        i_id, i_name, i_type = self.AGENT_DEFS["INSTITUTION"]
        self.create_xml_agent(i_id, i_name, i_type)
        if self.creator_name:
            self.create_xml_agent(self.creator_agent_id, self.creator_name, 'person', self.creator_gnd_id)

    def step0_carrier(self):
        print("\n[2/7] Verarbeite Träger...")
        if not self.path_step0.exists(): return
        
        cid = f"{self.disk_id}_carrier"
        rels = []
        if self.creator_agent_id:
            rels.append(('creator', 'is created by', self.creator_agent_id, None))
            
        # Sammle Eigenschaften für den Träger
        props = [("physical form", self.ctx.carrier_label)]
        if self.ctx.original_hardware:
            props.append(("hardware model", self.ctx.original_hardware))

        self.create_xml_object(
            obj_type="representation",
            identifier_val=cid,
            preservation_level="full",
            sig_props=props,
            relationships=rels
        )

        for f in self.path_step0.glob('*.tif'):
            sha = self._get_sha512(f)
            self.create_xml_object(
                obj_type="file",
                identifier_val=f.name,
                size=f.stat().st_size,
                fixity_list=[("SHA-512", sha)],
                format_info=("Tagged Image File Format", "PRONOM", "fmt/353"),
                relationships=[("structural", "is part of", cid, None)]
            )
            print(f"  -> Foto: {f.name}")

    def step1_imaging(self):
        print("\n[3/7] Verarbeite Disk-Image...")
        if not self.path_step1.exists(): return
        
        eid = f"evt_imaging_{self.disk_id}"
        cid = f"{self.disk_id}_carrier"
        
        agents = []
        # User Agent
        if self.ctx.user_agent:
            aid, name, atype = self.ctx.user_agent
            self.create_xml_agent(aid, name, atype)
            agents.append(aid)
            
        # Software Tool Agent
        if self.ctx.tool_agent:
            aid, name, atype = self.ctx.tool_agent
            self.create_xml_agent(aid, name, atype)
            agents.append(aid)

        # Hardware Tool Agent (Write Blocker)
        if self.ctx.hardware_agent:
            aid, name, atype = self.ctx.hardware_agent
            self.create_xml_agent(aid, name, atype)
            agents.append(aid)
            
        self.create_xml_event(eid, "creation", "Success", "Disk Imaging", self.ctx.creation_date, agents, [])

        # Image suchen (kann .img, .001, .dd sein, oder NEU: .bin)
        image_files = list(self.path_step1.glob('*.img')) + \
                      list(self.path_step1.glob('*.001')) + \
                      list(self.path_step1.glob('*.dd')) + \
                      list(self.path_step1.glob('*.bin'))
        
        for f in image_files:
            # Hashes: Erst aus Log, sonst berechnen
            sha512 = self._get_sha512(f)
            
            # Zusatzhashes aus FTK Log (MD5/SHA1)
            fixity = [("SHA-512", sha512)]
            if 'MD5' in self.ctx.image_hashes:
                fixity.append(("MD5", self.ctx.image_hashes['MD5']))
            if 'SHA1' in self.ctx.image_hashes:
                fixity.append(("SHA-1", self.ctx.image_hashes['SHA1']))
            
            self.create_xml_object(
                obj_type="file",
                identifier_val=f.name,
                size=f.stat().st_size,
                fixity_list=fixity,
                format_info=(self.ctx.image_type_label, "PRONOM", "x-fmt/263"), # oder fmt/93 für Raw, hier generisch
                relationships=[("derivation", "is derived from", cid, eid)]
            )
            print(f"  -> Image: {f.name}")
            self.source_img_name = f.name
            self.source_image_id = f.name # Update ID falls .001

        # Raw Flux Streams (Nur bei Greaseweazle relevant)
        raws = sorted(list(self.path_step1.glob('*.raw')))
        if raws and self.ctx.has_flux_stream:
            fs_id = f"{self.disk_id}_flux-stream-set"
            
            s_props = [("logical structure", "Logical Set of Flux Streams")]
            for k, v in self.ctx.metadata.items():
                s_props.append((k, v))

            self.create_xml_object(
                obj_type="representation",
                identifier_val=fs_id,
                preservation_level="full",
                sig_props=s_props,
                relationships=[("derivation", "is derived from", cid, eid)]
            )
            
            for r in raws:
                sha = self.ctx.image_hashes.get(r.name) or self._get_sha512(r)
                self.create_xml_object(
                    obj_type="file",
                    identifier_val=r.name,
                    size=r.stat().st_size,
                    fixity_list=[("SHA-512", sha)],
                    format_info=("Greaseweazle Raw Flux Stream", None, None),
                    relationships=[("structural", "is part of", fs_id, None)]
                )
        elif raws and not self.ctx.has_flux_stream:
            print("  -> [INFO] .raw Dateien gefunden, aber im aktuellen Modus ignoriert.")

    def step2_and_3_extraction(self):
        print("\n[4/7] Verarbeite Extraktion & Forensik...")
        if not self.path_step2.exists(): return
        
        aid_br = self.AGENT_DEFS["BRUNNHILDE"][0]
        self.create_xml_agent(*self.AGENT_DEFS["BRUNNHILDE"])
        
        evt_ext_id = f"evt_extraction_{self.disk_id}"
        self.create_xml_event(evt_ext_id, "extraction", "Success", "Brunnhilde Extraction", 
                              datetime.now().isoformat(), [aid_br], [(self.source_image_id, "source")])
        
        idx_file = self.path_step3 / f"3_{self.disk_id}_for-transfer.index"
        csv_file = self.path_step2 / f"2_{self.disk_id}_extracted-files_brunnhilde" / "files_collection_report" / "siegfried.csv"
        real_files_dir = self.path_step2 / f"2_{self.disk_id}_extracted-files_brunnhilde" / "files"
        
        idx_data = {}
        if idx_file.exists():
            t = etree.parse(str(idx_file))
            for f in t.findall('file'):
                p = f.get('path')
                idx_data[p] = {c.tag: c.text for c in f}
                is_orig = True
                for o in t.findall('file'):
                    if p.startswith(o.get('path')) and len(p) > len(o.get('path')): is_orig = False
                if is_orig: self.original_extracted_files.append(p)
        
        files_list = []
        if csv_file.exists():
            with open(csv_file, 'r', encoding='utf-8') as f:
                files_list = list(csv.DictReader(f))
        else:
            for p in self.original_extracted_files:
                files_list.append({'filename': p, 'filesize': '0', 'id': 'fmt/0'})
                
        if idx_file.exists():
            aid_meta = self.AGENT_DEFS["METADATA_EXTRACTOR"][0]
            self.create_xml_agent(*self.AGENT_DEFS["METADATA_EXTRACTOR"])
            evt_meta_id = f"evt_metadata_extraction_{self.disk_id}"
            self.create_xml_event(evt_meta_id, "metadata extraction", "Success", "Extraction from Siegfried/Index", 
                                  datetime.now().isoformat(), [aid_meta], [])

        count = 0
        for row in files_list:
            full_path = row.get('filename', 'unknown')
            fname = os.path.basename(full_path)
            
            meta = idx_data.get(full_path) or idx_data.get(fname)
            final_id = fname if meta else full_path
            
            if meta:
                self.archived_file_ids.append(final_id)
                
                sha = meta.get('sha512')
                sz = meta.get('size')
                pron = meta.get('pronom_id')
                
                c_app = None
                if meta.get('document_creator_tool'):
                    c_app = (meta.get('document_creator_tool'), meta.get('asset_created_date'))
                    
                self.create_xml_object(
                    obj_type="file",
                    identifier_val=final_id,
                    size=sz,
                    fixity_list=[("SHA-512", sha)],
                    format_info=("File Format", "PRONOM", pron),
                    creating_app=c_app,
                    filetrove_dict=meta,
                    relationships=[("derivation", "is derived from", self.source_image_id, evt_ext_id)]
                )
                
            else:
                real_p = real_files_dir / fname
                if not real_p.exists(): real_p = real_files_dir / full_path
                
                sha = self._get_sha512(real_p)
                
                self.create_xml_object(
                    obj_type="file",
                    identifier_val=full_path,
                    size=row.get('filesize'),
                    fixity_list=[("SHA-512", sha)] if sha else None,
                    format_info=("File Format", "PRONOM", row.get('id')),
                    sig_props=[("preservation_status", "Forensic Artifact (not selected)")],
                    relationships=[("derivation", "is derived from", self.source_image_id, evt_ext_id)]
                )
            count += 1
        print(f"  -> {count} Dateien verarbeitet.")

    def step3b_conversion(self):
        print("\n[5/7] Verarbeite Konvertierung...")
        idx_file = self.path_step3 / f"3_{self.disk_id}_for-transfer.index"
        if not idx_file.exists(): return
        
        aid = self.AGENT_DEFS["PYTHON_CONVERSION"][0]
        self.create_xml_agent(*self.AGENT_DEFS["PYTHON_CONVERSION"])
        
        evt_id = f"evt_conversion_{self.disk_id}"
        self.create_xml_event(evt_id, "migration", "Success", "PDF Creation", 
                              datetime.now().isoformat(), [aid], [])
        
        tree = etree.parse(str(idx_file))
        for f in tree.findall('file'):
            path = f.get('path')
            
            source = None
            for orig in self.original_extracted_files:
                if path.startswith(orig) and len(path) > len(orig):
                    source = orig
                    break
            
            if source:
                self.archived_file_ids.append(path) 
                meta = {c.tag: c.text for c in f}
                
                c_app = None
                if meta.get('document_creator_tool'):
                    c_app = (meta.get('document_creator_tool'), meta.get('asset_created_date'))
                
                self.create_xml_object(
                    obj_type="file",
                    identifier_val=path,
                    size=meta.get('size'),
                    fixity_list=[("SHA-512", meta.get('sha512'))],
                    format_info=("PDF Derivative", "PRONOM", meta.get('pronom_id')),
                    creating_app=c_app,
                    filetrove_dict=meta,
                    relationships=[("derivation", "is derived from", source, evt_id)]
                )

    def step5_package(self):
        print("\n[6/7] Verarbeite Archiv-Paket...")
        if not self.path_step5_lza.exists(): return
        
        imgs = list(self.path_step5_lza.glob("*_LZA_derivation-image.img"))
        if not imgs: imgs = list(self.path_step5_lza.glob("*.img"))
        if not imgs: return
        
        final_img = imgs[0]
        log = final_img.with_suffix('.log')
        
        evt_id = f"evt_packaging_{self.disk_id}"
        
        sha = None; pronom = "x-fmt/263"; agent_str = "Unknown"
        if log.exists():
            with open(log, 'r', encoding='utf-8', errors='ignore') as f: c = f.read()
            if m := re.search(r"fixity-sha512: ([a-f0-9]{128})", c, re.I): sha = m.group(1)
            if m := re.search(r"pronomId: (.*)", c): pronom = m.group(1).strip()
            if m := re.search(r"executingAgent: (.*)", c): agent_str = m.group(1).strip()
        
        if not sha: 
            print("  -> Berechne Live-Hash für Archiv-Image...")
            sha = self._get_sha512(final_img)
            
        aid = "SW_Packager"
        self.create_xml_agent(aid, agent_str, "software")
        
        links = [(fid, "source") for fid in self.archived_file_ids]
        self.create_xml_event(evt_id, "creation", "Success", "Final Packaging", 
                              datetime.now().isoformat(), [aid], links)
        
        rels = []
        for fid in self.archived_file_ids:
            rels.append(("structural", "is included in", fid, None))
        
        rels.append(("derivation", "is derived from", self.source_image_id, evt_id))
            
        self.create_xml_object(
            obj_type="file",
            identifier_val=final_img.name,
            size=final_img.stat().st_size,
            fixity_list=[("SHA-512", sha)],
            format_info=("Archival Disk Image", "PRONOM", pronom),
            relationships=rels
        )
        print(f"  -> Archiv-Image '{final_img.name}' erstellt.")

    def step_rights(self):
        print("\n[7/7] Schreibe Rechte...")
        cid = f"{self.disk_id}_carrier"
        
        rb = etree.Element(PREMIS + 'rights')
        rs = etree.SubElement(rb, PREMIS + 'rightsStatement')
        
        rsi = etree.SubElement(rs, PREMIS + 'rightsStatementIdentifier')
        self._add_simple(rsi, 'rightsStatementIdentifierType', 'local')
        self._add_simple(rsi, 'rightsStatementIdentifierValue', f"rights_{self.disk_id}")
        
        self._add_simple(rs, 'rightsBasis', 'Copyright')
        
        ci = etree.SubElement(rs, PREMIS + 'copyrightInformation')
        self._add_simple(ci, 'copyrightStatus', 'copyrighted')
        self._add_simple(ci, 'copyrightJurisdiction', 'AT')
        
        txt = "Urheberrechtlich geschützt."
        if self.creator_name: txt += f" Rechte bei {self.creator_name}."
        self._add_simple(ci, 'copyrightNote', txt)
        
        loi = etree.SubElement(rs, PREMIS + 'linkingObjectIdentifier')
        self._add_simple(loi, 'linkingObjectIdentifierType', 'local')
        self._add_simple(loi, 'linkingObjectIdentifierValue', cid)
        
        self.xml_rights.append(rb)

    # --- SORTING (CONTEXT AWARE) ---
    def _enforce_xsd_order(self, element):
        """Sortiert Elemente basierend auf ihrem Parent-Kontext."""
        
        object_order = {
            'objectIdentifier': 1,
            'preservationLevel': 2,
            'significantProperties': 3,
            'objectCharacteristics': 4,
            'originalName': 5,
            'relationship': 8
        }
        
        event_order = {
            'eventIdentifier': 1,
            'eventType': 2,
            'eventDateTime': 3,
            'eventOutcomeInformation': 5,
            'linkingAgentIdentifier': 6, 
            'linkingObjectIdentifier': 7
        }
        
        rights_order = {
            'rightsStatementIdentifier': 1,
            'rightsBasis': 2,
            'copyrightInformation': 3,
            'linkingObjectIdentifier': 7,
            'linkingAgentIdentifier': 8
        }
        
        char_order = {
            'fixity': 1,
            'size': 2,
            'format': 3,
            'creatingApplication': 4,
            'objectCharacteristicsExtension': 6
        }

        for child in element:
            self._enforce_xsd_order(child)
            
        tag_name = element.tag.replace(PREMIS, '')
        
        current_map = {}
        if tag_name == 'object': current_map = object_order
        elif tag_name == 'event': current_map = event_order
        elif tag_name == 'rightsStatement': current_map = rights_order
        elif tag_name == 'objectCharacteristics': current_map = char_order
        
        if current_map:
            def get_order(e):
                t = e.tag.replace(PREMIS, '')
                return current_map.get(t, 999)
            element[:] = sorted(element, key=get_order)

    def run(self):
        self.step_agents()
        self.step0_carrier()
        self.step1_imaging()
        self.step2_and_3_extraction() 
        self.step3b_conversion()
        self.step5_package()
        self.step_rights()
        
        for l in [self.xml_objects, self.xml_events, self.xml_agents, self.xml_rights]:
            for e in l: 
                self._enforce_xsd_order(e)
                self.root.append(e)
            
        self.write_premis_file()

    def write_premis_file(self):
        output_path = self.path_step5_lza / f"5_{self.disk_id}_LZA_premis.xml"
        xml_string = etree.tostring(self.root, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        with open(output_path, 'wb') as f:
            f.write(xml_string)
        print(f"\nERFOLG: {output_path}")

if __name__ == "__main__":
    try:
        if len(sys.argv) < 3:
            print("FEHLER: Zu wenig Argumente! Nutzung: script.py <AC-Nummer> <Disk-ID>")
            sys.exit(1)

        ac = sys.argv[1]
        did = sys.argv[2]
        
        gen = PremisGenerator(ac, did)
        gen.run()
        
        antwort = input("\nOrdner öffnen? (j/n): ").strip().lower()
        if antwort.startswith('j') or antwort == 'y':
            target_path = gen.path_step5_lza
            print(f"Versuche Explorer zu öffnen für: {target_path}")
            
            if target_path.exists():
                if sys.platform == "win32":
                    subprocess.Popen(['explorer', str(target_path)])
                elif sys.platform == "darwin":
                    subprocess.run(["open", str(target_path)])
                else:
                    subprocess.run(["xdg-open", str(target_path)])
            else:
                print(f"FEHLER: Der Ordner wurde nicht gefunden: {target_path}")

    except IndexError:
        print("FEHLER: Bitte AC-Nummer und Disk-ID übergeben!")
    except Exception as e:
        print(f"KRITISCHER FEHLER: {e}")
        import traceback
        traceback.print_exc()