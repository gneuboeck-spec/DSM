# SPDX-FileCopyrightText: 2025 Gregor Neuböck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
from pathlib import Path
import xml.etree.ElementTree as ET
import subprocess
import platform
import sys  # HINZUGEFÜGT: sys wird für die Kommandozeilen-Argumente benötigt
from bs4 import BeautifulSoup

# ===== Konfiguration: Pfade definieren =====

# <<< HIER IST DIE ANPASSUNG >>>
# Anstatt selbst zu fragen, werden die Werte von der Kommandozeile gelesen,
# die vom menu.py-Skript übergeben werden.
try:
    AC_number = sys.argv[1]
    disk_archive_ID = sys.argv[2]
    print(f"Werte aus der Kommandozeile erhalten: AC={AC_number}, ID={disk_archive_ID}")
except IndexError:
    print("FEHLER: AC-Nummer und Datenträger-ID wurden nicht übergeben.")
    print("Dieses Skript sollte über die 'start.bat'-Datei und das Menü gestartet werden.")
    # Fallback auf manuelle Eingabe, wenn es direkt gestartet wird
    print("\nBitte geben Sie die Daten manuell ein:")
    AC_number = input("AC-Nummer eingeben:")
    disk_archive_ID = input("Datenträger-ID eingeben:")

# NEU: Datenpfad aus menu.py übernehmen (sys.argv[3] oder Umgebungsvariable DATA_PATH)
if len(sys.argv) >= 4:
    base_path = Path(sys.argv[3])
else:
    base_path = Path(os.environ.get("DATA_PATH", Path.home() / "Documents/data" / AC_number / disk_archive_ID))

input_XML_path = base_path / f"0_{disk_archive_ID}_picture-carrier/0_{disk_archive_ID}_carrier-description.xml"
input_HTML_path = base_path / f"2_{disk_archive_ID}_extracted-files/2_{disk_archive_ID}_extracted-files_brunnhilde/files_collection_report/report.html"
output_XML_path = base_path / f"2_{disk_archive_ID}_extracted-files/2_{disk_archive_ID}_extracted-files.content"

if not base_path.exists():
    print(f"\033[91mBasis-Verzeichnis nicht gefunden: {base_path}\033[0m")
    exit()
if not input_XML_path.exists():
    print(f"\033[91mXML-Input-Datei nicht gefunden: {input_XML_path}\033[0m")
    exit()
if not input_HTML_path.exists():
    print(f"\033[91mHTML-Input-Datei nicht gefunden: {input_HTML_path}\033[0m")
    exit()
transfer_folder = base_path / f"3_{disk_archive_ID}_for-transfer"
if not transfer_folder.exists():
    print(f"\033[91mfor-transfer-Ordner nicht gefunden: {transfer_folder}\033[0m")
    exit()

# ===== XML-Datei laden und parsen =====

def get_text_or_empty(root, tag):
    element = root.find(tag)
    return element.text if element is not None and element.text else ""

# XML-Datei laden und parsen mit Fehlerbehandlung
try:
    tree = ET.parse(input_XML_path)
    root = tree.getroot()
except ET.ParseError as e:
    print(f"Fehler beim Parsen der XML-Datei: {e}")
    exit(1)

# Carrier-Daten extrahieren
carrier_data = {
    'CarrierType': get_text_or_empty(root, 'CarrierType'),
    'CarrierInscription': get_text_or_empty(root, 'CarrierInscription'),
    'CarrierBranding': get_text_or_empty(root, 'CarrierBranding'),
    'CarrierCondition': get_text_or_empty(root, 'CarrierCondition'),
    'CarrierDescriptionNote': get_text_or_empty(root, 'CarrierDescriptionNote'),
}

# ===== HTML-Report laden und Daten extrahieren =====

# HTML-Datei laden
with open(input_HTML_path, 'r', encoding='utf-8') as f:
    html_content = f.read()
soup = BeautifulSoup(html_content, 'html.parser')

total_files = ""
paragraph_elements = soup.find_all('p')
for p in paragraph_elements:
    if p.strong and 'Total files:' in p.strong.text:
        total_files = p.text.replace('Total files:', '').strip()
        break

total_size = ""
for p in paragraph_elements:
    if p.strong and 'Total size:' in p.strong.text:
        total_size = p.text.replace('Total size:', '').strip()
        break

earliest_date = ""
for p in paragraph_elements:
    if p.strong and 'Earliest date:' in p.strong.text:
        earliest_date = p.text.replace('Earliest date:', '').strip()
        break

latest_date = ""
for p in paragraph_elements:
    if p.strong and 'Latest date:' in p.strong.text:
        latest_date = p.text.replace('Latest date:', '').strip()
        break

# File Format Versions Tabelle extrahieren
file_format_versions = []
unidentified_count = "0"

# Finde die Tabelle "File format versions"
tables = soup.find_all('table')
format_versions_table = None

for table in tables:
    # Suche nach der Überschrift vor der Tabelle
    prev_heading = table.find_previous('h2')
    if prev_heading and 'File format versions' in prev_heading.text:
        format_versions_table = table
        break

if format_versions_table:
    rows = format_versions_table.find('tbody').find_all('tr')
    
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 4:
            format_name = cols[0].text.strip()
            pronom_id_link = cols[1].find('a')
            
            # Wenn Format leer ist und ID "UNKNOWN", dann sind es die unidentified files
            if format_name == "" and cols[1].text.strip() == "UNKNOWN":
                unidentified_count = cols[3].text.strip()
            else:
                # Pronom ID extrahieren
                if pronom_id_link:
                    pronom_id = pronom_id_link.text.strip()
                else:
                    pronom_id = cols[1].text.strip()
                
                version = cols[2].text.strip()
                count = cols[3].text.strip()
                
                file_format_versions.append({
                    'PronomID': pronom_id,
                    'FileFormatType': format_name,
                    'FileFormatVersion': version,
                    'Number': count
                })

    # ===== XML-Ausgabedatei erstellen =====

# Root-Element erstellen
root = ET.Element('DataCarrierSummary')
root.set('ID', disk_archive_ID)

# CarrierDescription-Sektion (aus INPUT_XML_PATH)
carrier_desc_element = ET.SubElement(root, 'CarrierDescription')

ET.SubElement(carrier_desc_element, 'CarrierType').text = carrier_data['CarrierType']
ET.SubElement(carrier_desc_element, 'CarrierInscription').text = carrier_data['CarrierInscription']
ET.SubElement(carrier_desc_element, 'CarrierBranding').text = carrier_data['CarrierBranding']
ET.SubElement(carrier_desc_element, 'CarrierCondition').text = carrier_data['CarrierCondition']
ET.SubElement(carrier_desc_element, 'CarrierDescriptionNote').text = carrier_data['CarrierDescriptionNote']

# FileStatistic-Sektion (aus INPUT_HTML_PATH)
file_stat_element = ET.SubElement(root, 'FileStatistic')

# NumberOfFiles
num_files_element = ET.SubElement(file_stat_element, 'NumberOfFiles')
ET.SubElement(num_files_element, 'TotalNumber').text = total_files

# IdentifiedFileFormatVersions
identified_element = ET.SubElement(num_files_element, 'IdentifiedFileFormatVersions')

for format_entry in file_format_versions:
    format_version_element = ET.SubElement(identified_element, 'FileFormatVersion')
    ET.SubElement(format_version_element, 'PronomID').text = format_entry['PronomID']
    ET.SubElement(format_version_element, 'FileFormatType').text = format_entry['FileFormatType']
    ET.SubElement(format_version_element, 'FileFormatVersion').text = format_entry['FileFormatVersion']
    ET.SubElement(format_version_element, 'Number').text = format_entry['Number']

# UnidentifiedFileFormats
unidentified_element = ET.SubElement(num_files_element, 'UnidentifiedFileFormats')
ET.SubElement(unidentified_element, 'Number').text = unidentified_count

# FileSize
file_size_element = ET.SubElement(file_stat_element, 'FileSize')
ET.SubElement(file_size_element, 'TotalSize').text = total_size

# Datumsangaben
ET.SubElement(file_stat_element, 'DateEarliestCreated').text = earliest_date
ET.SubElement(file_stat_element, 'DateLatestModified').text = latest_date

# XML-Baum erstellen und formatieren
tree = ET.ElementTree(root)
ET.indent(tree, space="    ")

# Prüfen ob Output-Datei bereits existiert
if output_XML_path.exists():
    print(f"\033[91mAusgabe-Datei existiert bereits und wird nicht überschrieben: {output_XML_path}\033[0m")
    exit()

# XML-Datei speichern
tree.write(output_XML_path, encoding='UTF-8', xml_declaration=True)
print(f"\033[92moutput_XML_Datei erstellt: {output_XML_path}\033[0m")

# Der Zielordner ist das übergeordnete Verzeichnis der XML-Ausgabedatei
destination_folder = output_XML_path.parent

# --- Zielordner optional öffnen ---
print("")
open_folder = input("Zielordner oeffnen? (j/n): ").lower()
if open_folder == 'j':
    if sys.platform == "win32":
        # KORREKTUR: Das Path-Objekt wird explizit in einen String umgewandelt
        os.startfile(str(destination_folder))
    elif sys.platform == "darwin":
        # KORREKTUR: Das Path-Objekt wird explizit in einen String umgewandelt
        subprocess.run(["open", str(destination_folder)])
    else:
        # KORREKTUR: Das Path-Objekt wird explizit in einen String umgewandelt
        subprocess.run(["xdg-open", str(destination_folder)])
    # Die Fore-Bibliothek wird hier nicht verwendet, daher Standard-Print mit Farbcodes
    print("\033[92mZielordner geoeffnet\033[0m")