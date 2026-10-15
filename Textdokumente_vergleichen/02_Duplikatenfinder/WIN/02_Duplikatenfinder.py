# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import sys
import hashlib
import csv
import stat
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import re
import logging
import tempfile
import unicodedata
import shutil

# Versuch, openpyxl zu importieren. Wird für die korrekte Hyperlink-Erstellung benötigt.
try:
    import openpyxl
    from openpyxl.styles import Font
except ImportError:
    print("❌ FEHLER: Die Bibliothek 'openpyxl' ist nicht installiert.")
    print("Bitte öffne dein Terminal / deine Eingabeaufforderung und führe aus:")
    print("pip install openpyxl")
    input("Drücken Sie die Eingabetaste, um dieses Fenster zu schließen...")
    sys.exit(1)

# ==============================================================================
# 🔧 KONFIGURATION
# ==============================================================================

DRY_RUN = False  
CHUNK_SIZE = 8 * 1024 * 1024

logging.getLogger('pypdf').setLevel(logging.ERROR)


# ==============================================================================
# 📌 BEVORZUGTES ORIGINAL-FORMAT
# ==============================================================================
# Priorität für das Behalten des Originals innerhalb einer Dubletten-Gruppe:
# Der erste Listeneintrag, der auf eine Datei zutrifft, gewinnt.
# Formate, die hier NICHT stehen (z. B. .html, .xml, .fodt, .csv), landen zuletzt.
FORMAT_PRIORITAET = [
    {'.pdf', '.pdfa'},   # 1: PDF wird immer bevorzugt behalten
    {'.docx', '.doc'},   # 2: Word-Dokumente
    {'.odt'},            # 3: OpenDocument
    {'.rtf'},            # 4: Rich Text
    {'.txt'},            # 5: Reiner Text
    {'.md'},             # 6: Markdown
]

def sort_files_by_priority(files):
    """Sortiert eine Dateiliste so, dass das bevorzugte Original an erster Stelle steht."""
    def rank(path):
        suffix = path.suffix.lower()
        for i, gruppe in enumerate(FORMAT_PRIORITAET):
            if suffix in gruppe:
                return i
        return len(FORMAT_PRIORITAET)  # unbekannte/exotische Formate ans Ende
    # sorted() ist stabil: Dateien mit gleichem Rang behalten ihre bisherige Reihenfolge
    return sorted(files, key=rank)


# ==============================================================================
# === HILFSFUNKTIONEN ==========================================================
# ==============================================================================

def calculate_sha256(file_path: Path) -> str:
    """Berechnet den SHA-256 Hash einer Datei in Chunks."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(CHUNK_SIZE), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except PermissionError as e:
        return f"ERROR_PERMISSION_DENIED: {e}"
    except Exception as e:
        return f"ERROR_{str(e)}"


def format_size(size_bytes):
    """Formatiert Bytes in ein lesbares Format (KB, MB, GB)."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0


def write_xlsx_log_file(log_path: Path, mode: str, log_data: list, base_dir: Path):
    """Schreibt die Zusammenfassung in eine echte .xlsx-Datei mit klickbaren Hyperlinks."""
    print(f"\nErstelle {mode}-Log-Datei (Excel-Format mit Hyperlinks): {log_path}")
    try:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"Dubletten_{mode}"
        
        headers = ['Gruppe_ID', 'Typ', 'Dateiname', 'Relativer_Pfad', 'Dateigröße', 'SHA256', 'Aktion']
        ws.append(headers)
        
        # Überschrift fett machen
        for cell in ws[1]:
            cell.font = Font(bold=True)
            
        for data in log_data:
            row_num = ws.max_row + 1
            
            ws.cell(row=row_num, column=1, value=data['Gruppe_ID'])
            ws.cell(row=row_num, column=2, value=data['Typ'])
            ws.cell(row=row_num, column=3, value=data['Dateiname'])
            
            # === HIER PASSIERT DIE HYPERLINK-MAGIE ===
            rel_path = data['Relativer_Pfad']
            # Wir bauen den absoluten Pfad für das Link-Ziel, zeigen aber den relativen Pfad an
            abs_path = str((base_dir / rel_path).resolve())
            
            cell_link = ws.cell(row=row_num, column=4, value=rel_path)
            cell_link.hyperlink = abs_path
            cell_link.style = 'Hyperlink'  # Macht den Text blau und unterstrichen
            # =========================================
            
            ws.cell(row=row_num, column=5, value=data['Dateigröße'])
            ws.cell(row=row_num, column=6, value=data['SHA256'])
            ws.cell(row=row_num, column=7, value=data['Aktion'])
            
        # Spaltenbreiten automatisch anpassen für bessere Lesbarkeit
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except Exception:
                    pass
            adjusted_width = min(max_length + 2, 50) # Maximal 50 Zeichen breit
            ws.column_dimensions[column_letter].width = adjusted_width
            
        wb.save(log_path)
        print(f"[OK] {mode.capitalize()}-Log-Datei erfolgreich erstellt.")
        return True
    except Exception as e:
        print(f"[FEHLER] {mode.capitalize()}-Log-Datei konnte nicht erstellt werden: {e}")
        return False


def write_csv_log_file(log_path: Path, mode: str, log_data: list):
    """Schreibt zusätzlich eine reine CSV-Datei als Rohdaten-Backup."""
    try:
        with open(log_path, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ['Gruppe_ID', 'Typ', 'Dateiname', 'Relativer_Pfad', 'Dateigröße', 'SHA256', 'Aktion']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(log_data)
    except Exception as e:
        print(f"[FEHLER] CSV-Backup konnte nicht erstellt werden: {e}")


# ==============================================================================
# 📖 INHALTS-BASIERTE DUBLLETTEN-ERKENNUNG (FÜR DOKUMENTE)
# ==============================================================================

def extract_text_direct(file_path: Path) -> str:
    """Extrahiert Text direkt mit Python-Bibliotheken (schneller, für gängige Formate)."""
    suffix = file_path.suffix.lower()
    text = ""

    if suffix in ['.pdf', '.pdfa']:
        import pypdf
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            pages = []
            for page in reader.pages:
                raw = page.extract_text() or ""
                lines = []
                for line in raw.splitlines():
                    s = line.strip()
                    if s.isdigit() and len(s) <= 4:
                        continue
                    lines.append(line)
                pages.append("\n".join(lines))
            text = "\n".join(pages)

    elif suffix in ['.docx']:
        import docx
        doc = docx.Document(file_path)
        text = "\n".join(para.text for para in doc.paragraphs)

    elif suffix in ['.odt']:
        from odf.opendocument import load
        from odf import text as odf_text
        doc = load(str(file_path))
        paragraphs = doc.getElementsByType(odf_text.P)
        text = "\n".join(str(p) for p in paragraphs)

    elif suffix in ['.uot']:
        raw = file_path.read_bytes()
        text = ""
        # Versuch 1: ODF (zip-basiert)
        try:
            from odf.opendocument import load
            from odf import text as odf_text
            doc = load(str(file_path))
            paragraphs = doc.getElementsByType(odf_text.P)
            text = "\n".join(str(p) for p in paragraphs)
        except Exception:
            text = ""
        # Versuch 2: gzip-komprimiertes XML
        if not text.strip():
            try:
                import gzip
                import xml.etree.ElementTree as ET
                root = ET.fromstring(gzip.decompress(raw))
                text = ''.join(root.itertext())
            except Exception:
                text = ""
        # Versuch 3: unkomprimiertes UOF-XML -> nur <字:文本串> (Textstrings) extrahieren
        if not text.strip():
            try:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(raw)  # WICHTIG: BYTES, nicht str!
                parts = []
                for elem in root.iter():
                    tag_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                    if tag_name == '文本串':
                        teil = ''.join(elem.itertext())  # liest ALLES inkl. Kind-Tags
                        teil = re.sub(r'^(page|seite)\d+\s*', '', teil, flags=re.IGNORECASE)
                        if teil:
                            parts.append(teil)
                text = '\n'.join(parts)
            except Exception as e:
                print(f"   ⚠️ UOF-XML-Parsing fehlgeschlagen für {file_path.name}: {e}")
                text = ""
        # Versuch 4: DOCX-Container (zip mit word/document.xml)
        if not text.strip():
            try:
                import docx
                doc = docx.Document(str(file_path))
                text = "\n".join(p.text for p in doc.paragraphs)
            except Exception:
                text = ""
        # Bewusst kein Reintext-Fallback: XML-Brühe würde nur falsche Hashes erzeugen

    elif suffix in ['.rtf']:
        from striprtf.striprtf import rtf_to_text
        with open(file_path, 'r', encoding='latin-1', errors='ignore') as f:
            rtf_content = f.read()
        text = rtf_to_text(rtf_content)

    elif suffix in ['.html', '.htm']:
        from html.parser import HTMLParser

        class HTMLTextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.result = []
                self.skip = False

            def handle_starttag(self, tag, attrs):
                if tag in ('script', 'style', 'head', 'title', 'meta'):
                    self.skip = True

            def handle_endtag(self, tag):
                if tag in ('script', 'style', 'head', 'title', 'meta'):
                    self.skip = False

            def handle_data(self, data):
                if not self.skip:
                    self.result.append(data)

            def get_text(self):
                return ''.join(self.result)

        raw_bytes = file_path.read_bytes()
        html_content = ""
        for encoding in ['utf-8', 'utf-8-sig', 'cp1252', 'latin-1']:
            try:
                html_content = raw_bytes.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

        extractor = HTMLTextExtractor()
        extractor.feed(html_content)
        text = extractor.get_text()

    elif suffix in ['.xml', '.xhtml', '.fodt']:
        import xml.etree.ElementTree as ET
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            ns_odf_new = '{urn:oasis:names:tc:opendocument:xmlns:office:1.0}'
            ns_odf_old = '{http://openoffice.org/2000/office}'
            ns_w       = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

            text = ''
            body = None
            for ns in (ns_odf_new, ns_odf_old):
                body = root.find(f'.//{ns}body')
                if body is not None:
                    break

            if body is not None:
                text = ''.join(body.itertext())
            else:
                wbody = root.find(f'.//{ns_w}body')
                if wbody is not None:
                    text = ''.join(t.text or '' for t in wbody.iter(f'{ns_w}t'))
                else:
                    for elem in list(root.iter()):
                        local = elem.tag.split('}')[-1].lower()
                        if local in ('meta', 'metadata', 'settings', 'styles',
                                     'scripts', 'font-face-decls', 'document-meta'):
                            elem.clear()
                    text = ''.join(root.itertext())
        except ET.ParseError:
            text = ""

    elif suffix in ['.txt', '.md', '.csv']:
        raw_bytes = file_path.read_bytes()
        text = ""
        for encoding in ['utf-8', 'utf-8-sig', 'cp1252', 'latin-1', 'iso-8859-1']:
            try:
                text = raw_bytes.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        if not text:
            text = raw_bytes.decode('utf-8', errors='replace')

    return text


def extract_text_via_libreoffice(file_path: Path) -> str:
    """Konvertiert das Dokument mit LibreOffice in eine TXT-Datei und extrahiert den Text."""
    libreoffice_path = None
    
    # 1. Versuche: LibreOffice im System-PATH finden (beste Portabilität)
    libreoffice_path = shutil.which("soffice") or shutil.which("libreoffice")
    
    # 2. Fallback: Bekannte Standardpfade prüfen, falls es nicht im PATH ist
    if not libreoffice_path:
        possible_paths = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            "/usr/bin/libreoffice",
            "/usr/bin/soffice",
            "/Applications/LibreOffice.app/Contents/MacOS/soffice"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                libreoffice_path = path
                break
    
    if not libreoffice_path:
        raise Exception("LibreOffice nicht gefunden. Bitte installieren oder zum System-PATH hinzufügen.")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        cmd = [
            libreoffice_path,
            '--headless',
            '--norestore',
            '--convert-to', 'txt:Text',
            '--outdir', temp_dir,
            str(file_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            raise Exception(f"LibreOffice-Konvertierung fehlgeschlagen: {result.stderr}")
        
        txt_files = list(Path(temp_dir).glob('*.txt'))
        if not txt_files:
            raise Exception("Keine TXT-Datei nach Konvertierung gefunden.")
        
        raw_bytes = txt_files[0].read_bytes()
        text = ""
        
        for encoding in ['utf-8', 'utf-8-sig', 'cp1252', 'latin-1', 'iso-8859-1']:
            try:
                text = raw_bytes.decode(encoding)
                if text and any(c.isalpha() for c in text):
                    break
            except UnicodeDecodeError:
                continue
        else:
            text = raw_bytes.decode('utf-8', errors='replace')
        
    return text


def extract_text_from_document(file_path: Path) -> str:
    """
    Extrahiert den reinen Text aus ALLEN Dokumentenformaten.
    Verwendet zuerst direkte Python-Bibliotheken (schnell),
    dann LibreOffice als Fallback (für alte/komplexe Formate).
    """
    suffix = file_path.suffix.lower()
    text = ""
    
    direct_formats = {
        '.pdf', '.pdfa', '.docx', '.fodt', '.txt', '.md', '.csv',
        '.odt', '.uot', '.rtf', '.html', '.htm', '.xml', '.xhtml'
    }
    
    libreoffice_formats = {
        '.doc', '.xls', '.xlsx', '.ppt', '.pptx',
        '.pages', '.numbers', '.key',
        '.ods', '.odp',
        '.wpd',
        '.epub', '.mobi',
        '.tex', '.latex',
        '.wps',
        '.sxw', '.sxc', '.sxi'
    }
    
    try:
        if suffix in direct_formats:
            text = extract_text_direct(file_path)
            if not text.strip():
                text = extract_text_via_libreoffice(file_path)
        elif suffix in libreoffice_formats:
            text = extract_text_via_libreoffice(file_path)
        else:
            print(f"   ℹ️ Unbekanntes Format '{suffix}' bei {file_path.name}, versuche LibreOffice...")
            text = extract_text_via_libreoffice(file_path)
            
    except Exception as e:
        print(f"   ⚠️ Textextraktion fehlgeschlagen für {file_path.name}: {e}")
        return ""
        
    return text


def normalize_text_for_comparison(text: str) -> str:
    """Maximale Normalisierung: Trennstriche reparieren, nur Buchstaben+Zahlen behalten."""
    if not text:
        return ""
    
    # Unicode normalisieren (Ligaturen wie 'ﬀ' -> 'ff', kombinierte Akzente)
    text = unicodedata.normalize('NFKC', text)
    
    text = text.lower()
    
    # Zeilenumbruch-Trennstriche reparieren
    text = re.sub(r'([a-zäöüßàâáéèêíìîóòôúùûñç])-\s+', r'\1', text)
    
    # NUR Buchstaben+Zahlen behalten (unsichtbare Zeichen, Leerzeichen, Satzzeichen weg)
    text = re.sub(r'[^\w]', '', text, flags=re.UNICODE)
    text = text.replace('_', '')
    
    # Alle Zeichen über Codepoint 255 entfernen (cp1252-Verluste ausgleichen)
    text = re.sub(r'[^\x00-\xff]', '', text)
    
    # JETZT (nach der Bereinigung!) führende Seitenkennungen entfernen:
    # Hier steht "page273" garantiert an Position 0, der ^-Anker trifft sicher.
    text = re.sub(r'^(page|seite)\d+', '', text)
    
    # Ziffern am Ende entfernen (LibreOffice-Statistiken)
    text = re.sub(r'\d+$', '', text)
    
    return text


def get_content_hash_for_document(file_path: Path) -> str:
    """Gibt einen Hash zurück, der auf dem INHALT des Dokuments basiert."""
    raw_text = extract_text_from_document(file_path)
    
    if not raw_text or len(raw_text.strip()) < 50:
        return "NO_MEANINGFUL_TEXT"
    
    normalized_text = normalize_text_for_comparison(raw_text)
    return hashlib.sha256(normalized_text.encode('utf-8')).hexdigest()


# ==============================================================================
# === DUBLLETTEN-SUCHE =========================================================
# ==============================================================================

def find_duplicate_groups(base_dir):
    """Durchsucht ein Verzeichnis und gibt Gruppen von Duplikaten zurück."""
    print("--- Starte Analyse: Suche nach Prüfsummendubletten... ---")
    
    size_groups = defaultdict(list)
    total_files = 0
    
    for file_path in base_dir.rglob('*'):
        if file_path.is_file():
            try:
                size = file_path.stat().st_size
                size_groups[size].append(file_path)
                total_files += 1
            except Exception:
                continue

    print(f"   ✅ {total_files} Dateien gescannt.")
    
    potential_duplicates = {size: files for size, files in size_groups.items() if len(files) > 1}
    print(f"   ℹ️  {len(potential_duplicates)} Größen-Kategorien mit potenziellen Duplikaten gefunden.")

    print("   Berechne SHA-256 Prüfsummen für potenzielle Duplikaten...")
    hash_groups = defaultdict(list)
    files_to_hash = sum(len(files) for files in potential_duplicates.values())
    hashed_count = 0

    for size, files in potential_duplicates.items():
        for file_path in files:
            file_hash = calculate_sha256(file_path)
            if file_hash and not file_hash.startswith("ERROR"):
                unique_key = f"{size}_{file_hash}"
                hash_groups[unique_key].append(file_path)
            
            hashed_count += 1
            if hashed_count % 100 == 0:
                print(f"   ⏳ Fortschritt: {hashed_count}/{files_to_hash} Dateien gehasht...", end='\r')
    
    print(f"\n   ✅ {hashed_count} Prüfsummen berechnet.")

    actual_duplicates = {key: files for key, files in hash_groups.items() if len(files) > 1}
    
    print("\n--- Starte zusätzliche Analyse: Suche nach inhaltlichen Dubletten (verschiedene Formate)... ---")
    
    document_extensions = {
        '.pdf', '.pdfa', '.docx', '.txt', '.md', '.csv',
        '.odt', '.uot', '.fodt', '.rtf', '.html', '.htm', '.xml', '.xhtml',
        '.doc', '.xls', '.xlsx', '.ppt', '.pptx',
        '.pages', '.numbers', '.key',
        '.ods', '.odp',
        '.wpd',
        '.epub', '.mobi',
        '.tex', '.latex',
        '.wps',
        '.sxw', '.sxc', '.sxi'
    }
    
    binary_group_of_file = {}
    for key, files in actual_duplicates.items():
        for f in files:
            binary_group_of_file[f] = key
    
    candidate_documents = []
    processed_binary_keys = set()
    
    for file_path in base_dir.rglob('*'):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in document_extensions:
            continue
        
        binary_key = binary_group_of_file.get(file_path)
        if binary_key is not None:
            if binary_key in processed_binary_keys:
                continue
            processed_binary_keys.add(binary_key)
            candidate_documents.append(actual_duplicates[binary_key][0])
        else:
            candidate_documents.append(file_path)
    
    print(f"   ℹ️  {len(candidate_documents)} Dokumente für Inhalts-Vergleich gefunden.")
    
    if candidate_documents:
        print("   Extrahiere und vergleiche Textinhalte...")
        content_hash_groups = defaultdict(list)
        
        for idx, file_path in enumerate(candidate_documents, 1):
            content_hash = get_content_hash_for_document(file_path)
            
            if content_hash and content_hash not in ["NOT_A_DOCUMENT", "NO_MEANINGFUL_TEXT"]:
                content_hash_groups[content_hash].append(file_path)
            
            if idx % 10 == 0:
                print(f"   ⏳ Fortschritt: {idx}/{len(candidate_documents)} Dokumente verarbeitet...", end='\r')
        
        print(f"\n   ✅ {len(candidate_documents)} Dokumente verarbeitet.")
        
        content_duplicates = {key: files for key, files in content_hash_groups.items() if len(files) > 1}
        
        if content_duplicates:
            print(f"   🎯 {len(content_duplicates)} Gruppen mit inhaltlich identischen Dokumenten gefunden!")
            
            for content_hash, representatives in content_duplicates.items():
                merged_files = []
                merged_binary_keys = set()
                
                for rep in representatives:
                    bkey = binary_group_of_file.get(rep)
                    if bkey is not None:
                        merged_files.extend(actual_duplicates[bkey])
                        merged_binary_keys.add(bkey)
                    else:
                        merged_files.append(rep)
                
                special_key = f"CONTENT_{content_hash}"
                actual_duplicates[special_key] = merged_files
                
                for bkey in merged_binary_keys:
                    if bkey in actual_duplicates:
                        del actual_duplicates[bkey]
        else:
            print("   ℹ️  Keine zusätzlichen inhaltlichen Dubletten gefunden.")
    else:
        print("   ℹ️  Keine Dokumente für Inhalts-Vergleich gefunden.")

    # Bevorzugtes Original an den Anfang jeder Gruppe stellen
    for key in actual_duplicates:
        actual_duplicates[key] = sort_files_by_priority(actual_duplicates[key])
    
    return actual_duplicates, total_files


def perform_deletion(duplicate_groups, base_dir, log_dir):
    """Führt den eigentlichen Löschvorgang durch und erstellt das finale Log."""
    print("\n--- Starte Löschvorgang ---")
    
    final_log_data = []
    deleted_count = 0
    saved_space_bytes = 0

    for group_id, (unique_key, files) in enumerate(duplicate_groups.items(), 1):
        if unique_key.startswith("CONTENT_"):
            file_hash = unique_key.replace("CONTENT_", "")
            try:
                size_bytes = files[0].stat().st_size
            except Exception:
                size_bytes = 0
            dubletten_typ = "Inhaltliche Dublette"
        else:
            size_str, file_hash = unique_key.split('_', 1)
            size_bytes = int(size_str)
            dubletten_typ = "Binäre Dublette"
        
        original_file = files[0]
        final_log_data.append({
            'Gruppe_ID': f"GRUPPE_{group_id:03d}",
            'Typ': dubletten_typ,
            'Dateiname': original_file.name,
            'Relativer_Pfad': str(original_file.relative_to(base_dir)), # Reiner relativer Pfad
            'Dateigröße': format_size(size_bytes),
            'SHA256': file_hash,
            'Aktion': 'BEHALTEN (Original)'
        })

        for dup_file in files[1:]:
            if DRY_RUN:
                action_str = "GELÖSCHT (Simulation)"
                deleted_count += 1
                saved_space_bytes += size_bytes
            else:
                try:
                    dup_file.unlink()
                    action_str = "GELÖSCHT (Duplikat)"
                    deleted_count += 1
                    saved_space_bytes += size_bytes
                    print(f"[OK] Datei gelöscht: {dup_file.name}")
                    
                except PermissionError:
                    try:
                        os.chmod(dup_file, stat.S_IWRITE)
                        dup_file.unlink()
                        action_str = "GELÖSCHT (Schreibschutz entfernt)"
                        deleted_count += 1
                        saved_space_bytes += size_bytes
                        print(f"[OK] Datei gelöscht (Schreibschutz entfernt): {dup_file.name}")
                    except Exception as e2:
                        action_str = f"FEHLER: {e2}"
                        print(f"[FEHLER] Kein Zugriff auf: {dup_file.name} ({e2})")
                except Exception as e:
                    action_str = f"FEHLER: {e}"
                    print(f"[FEHLER] Unerwarteter Fehler beim Löschen von {dup_file.name}: {e}")

            final_log_data.append({
                'Gruppe_ID': f"GRUPPE_{group_id:03d}",
                'Typ': dubletten_typ,
                'Dateiname': dup_file.name,
                'Relativer_Pfad': str(dup_file.relative_to(base_dir)), # Reiner relativer Pfad
                'Dateigröße': format_size(size_bytes),
                'SHA256': file_hash,
                'Aktion': action_str
            })

    return final_log_data, deleted_count, saved_space_bytes


# ==============================================================================
# --- HAUPT-AUSFÜHRUNGSBLOCK ===================================================
# ==============================================================================
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("❌ Fehler: Quellverzeichnis und Log-Verzeichnis fehlen.")
        print("Verwendung: python 01_Duplikatenfinder.py <quellverzeichnis> <log_verzeichnis>")
        input("Drücken Sie die Eingabetaste, um dieses Fenster zu schließen...")
        sys.exit(1)

    source_dir = sys.argv[1]
    log_dir = sys.argv[2]

    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    root.update()

    try:
        base_path = Path(source_dir).resolve()
        log_path = Path(log_dir).resolve()

        if not base_path.is_dir():
            messagebox.showerror("Fehler", f"Das ausgewählte Quellverzeichnis existiert nicht:\n{base_path}")
            sys.exit(1)
            
        if not log_path.is_dir():
            messagebox.showerror("Fehler", f"Das ausgewählte Log-Verzeichnis existiert nicht:\n{log_path}")
            sys.exit(1)

        print(f"\nSkript wird mit folgenden Pfaden ausgeführt:")
        print(f"- Zu prüfender Ordner: {base_path}")
        print(f"- Log-Ausgabeverzeichnis: {log_path}\n")

        if DRY_RUN:
            print("\n\033[93m=== TESTLAUF (DRY_RUN) AKTIV ===\033[0m")
            print("Es werden keine Dateien wirklich gelöscht.\n")

        duplicate_groups, total_files = find_duplicate_groups(base_path)

        if not duplicate_groups:
            print("\nAnalyse abgeschlossen: Keine Prüfsummendubletten gefunden.")
            messagebox.showinfo("Analyse abgeschlossen", "Es wurden keine Prüfsummendubletten gefunden.\nAlle Dateien sind einzigartig.")
            sys.exit(0)

        preview_log_data = []
        preview_deleted_count = 0
        preview_saved_bytes = 0

        for group_id, (unique_key, files) in enumerate(duplicate_groups.items(), 1):
            if unique_key.startswith("CONTENT_"):
                file_hash = unique_key.replace("CONTENT_", "")
                try:
                    size_bytes = files[0].stat().st_size
                except Exception:
                    size_bytes = 0
                dubletten_typ = "Inhaltliche Dublette"
            else:
                size_str, file_hash = unique_key.split('_', 1)
                size_bytes = int(size_str)
                dubletten_typ = "Binäre Dublette"
            
            preview_log_data.append({
                'Gruppe_ID': f"GRUPPE_{group_id:03d}",
                'Typ': dubletten_typ,
                'Dateiname': files[0].name,
                'Relativer_Pfad': str(files[0].relative_to(base_path)), # Reiner relativer Pfad
                'Dateigröße': format_size(size_bytes),
                'SHA256': file_hash,
                'Aktion': 'BEHALTEN (Original)'
            })
            
            for dup_file in files[1:]:
                preview_log_data.append({
                    'Gruppe_ID': f"GRUPPE_{group_id:03d}",
                    'Typ': dubletten_typ,
                    'Dateiname': dup_file.name,
                    'Relativer_Pfad': str(dup_file.relative_to(base_path)), # Reiner relativer Pfad
                    'Dateigröße': format_size(size_bytes),
                    'SHA256': file_hash,
                    'Aktion': 'ZUM LÖSCHEN VORGEMERKT'
                })
                preview_deleted_count += 1
                preview_saved_bytes += size_bytes

        # 1. Hauptausgabe: XLSX mit klickbaren Links
        preview_log_name_xlsx = f"dublikaten_VORSCHAU_{base_path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        preview_log_file_xlsx = log_path / preview_log_name_xlsx
        write_xlsx_log_file(preview_log_file_xlsx, 'preview', preview_log_data, base_path)

        # 2. Backup: Reine CSV-Datei (ohne Formeln, nur Rohdaten)
        preview_log_name_csv = f"dublikaten_VORSCHAU_{base_path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        preview_log_file_csv = log_path / preview_log_name_csv
        write_csv_log_file(preview_log_file_csv, 'preview', preview_log_data)

        # Öffne die XLSX-Datei, da diese die klickbaren Links enthält
        try:
            if sys.platform == "win32":
                os.startfile(str(preview_log_file_xlsx))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(preview_log_file_xlsx)])
            else:
                subprocess.run(["xdg-open", str(preview_log_file_xlsx)])
        except Exception:
            pass

        confirm_msg = (
            f"Es wurden {len(duplicate_groups)} Gruppen mit insgesamt {preview_deleted_count} Duplikaten gefunden.\n"
            f"Potenziell freigegebener Speicher: {format_size(preview_saved_bytes)}\n\n"
            f"Eine Vorschau-Liste (Excel-Format mit klickbaren Links) wurde erstellt und geöffnet unter:\n{preview_log_file_xlsx}\n\n"
            f"Möchten Sie die als 'VORGEMERKT' markierten Dateien jetzt wirklich löschen?"
        )
        
        if not messagebox.askyesno("Löschvorgang bestätigen", confirm_msg):
            print("Löschvorgang vom Benutzer abgebrochen.")
            sys.exit(0)

        final_log_data, actual_deleted_count, actual_saved_bytes = perform_deletion(
            duplicate_groups, base_path, log_path
        )

        if actual_deleted_count > 0 or DRY_RUN:
            # 1. Hauptausgabe: XLSX mit klickbaren Links
            final_log_name_xlsx = f"dublikaten_GELÖSCHT_{base_path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            final_log_file_xlsx = log_path / final_log_name_xlsx
            write_xlsx_log_file(final_log_file_xlsx, 'final', final_log_data, base_path)
            
            # 2. Backup: Reine CSV-Datei
            final_log_name_csv = f"dublikaten_GELÖSCHT_{base_path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            final_log_file_csv = log_path / final_log_name_csv
            write_csv_log_file(final_log_file_csv, 'final', final_log_data)
            
            print(f"\n\033[92mBereinigung erfolgreich abgeschlossen!\033[0m")
            messagebox.showinfo(
                "Erfolg", 
                f"Bereinigung abgeschlossen.\n\n"
                f"Gelöschte Duplikate: {actual_deleted_count}\n"
                f"Freigegebener Speicher: {format_size(actual_saved_bytes)}\n\n"
                f"Das finale Log (mit klickbaren Links) wurde gespeichert unter:\n{final_log_file_xlsx}"
            )
        else:
            messagebox.showinfo("Info", "Keine Dateien wurden tatsächlich gelöscht (möglicherweise aufgrund von Zugriffsfehlern).")

        if messagebox.askyesno("Analyse abgeschlossen", f"Die Bereinigung ist fertig.\n\nMöchten Sie das bereinigte Verzeichnis öffnen?\n{source_dir}"):
            if sys.platform == "win32":
                os.startfile(str(base_path))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(base_path)])
            else:
                subprocess.run(["xdg-open", str(base_path)])

    except Exception as e:
        messagebox.showerror("Unerwarteter Fehler", f"Ein Fehler ist aufgetreten:\n{str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        print("\n" + "="*50)
        input("Drücken Sie die Eingabetaste, um dieses Fenster zu schließen...")