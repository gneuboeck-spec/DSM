#!/usr/bin/env python3
"""
PREMIS XML Validator - Final Combined Version
Validiert PREMIS-XML gegen XSD-Schema mit folgenden Features:
- GUI-Dialoge für einfache Datei-Auswahl
- 3-stufiger Schema-Fallback (Online -> User-Agent -> Lokal)
- Automatische Versionserkennung (PREMIS v3.0)
- Intelligente Filterung von FileTrove/Greaseweazle-Erweiterungen
- Ausgabe nur echter PREMIS-Fehler
- Optionaler Report-Export als Textdatei

Benötigt: pip install lxml requests
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime

# GUI-Importe
import tkinter as tk
from tkinter import filedialog, messagebox

# XML-Verarbeitung
try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    print("FEHLER: lxml nicht installiert!")
    print("Bitte installieren: pip install lxml")
    input("Drücke Enter zum Beenden...")
    sys.exit(1)

# HTTP-Requests (für Online-Schema-Fallback)
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# ==============================================================================
# KONFIGURATION
# ==============================================================================

# Namespaces die als erwartete, gültige PREMIS-Erweiterungen gelten
# Warnungen zu diesen Namespaces werden herausgefiltert
IGNORED_NAMESPACES = [
    'info:onb.ac.at/filetrove-schema/v1',
    'info:onb.ac.at/greaseweazle-format-schema/v1'
]

# Offizielle PREMIS-Schema-URL (Library of Congress)
PREMIS_XSD_URL = "https://www.loc.gov/standards/premis/v3/premis-v3-0.xsd"

# Browser-User-Agent für den zweiten Fallback-Versuch
BROWSER_USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
)


# ==============================================================================
# HILFSFUNKTIONEN
# ==============================================================================

def select_file(title, filetypes):
    """Öffnet einen Datei-Auswahl-Dialog."""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    file_path = filedialog.askopenfilename(
        title=title,
        filetypes=filetypes
    )
    
    root.destroy()
    return file_path


def detect_schema_version(xsd_path):
    """Erkennt die PREMIS-Version aus dem XSD-Schema."""
    try:
        tree = etree.parse(xsd_path)
        root = tree.getroot()
        
        # targetNamespace auslesen
        target_ns = root.get('targetNamespace', '')
        
        if target_ns == 'http://www.loc.gov/premis/v3':
            return '3.0', 'PREMIS v3.0 (2015 - Current Standard)', target_ns
        elif 'premis' in target_ns.lower():
            return 'custom', f'Custom PREMIS schema ({target_ns})', target_ns
        else:
            return 'unknown', f'Unknown schema ({target_ns})', target_ns
            
    except Exception as e:
        return 'error', f'Error reading schema: {e}', None


def load_schema_with_fallback(xsd_path):
    """
    Lädt das XSD-Schema mit 3-stufigem Fallback:
    1. Direkt aus dem Internet
    2. Mit Browser-User-Agent (gegen Bot-Schutz)
    3. Lokale Datei
    
    Gibt (schema_content, source) zurück.
    """
    if not HAS_REQUESTS:
        print("  [INFO] requests nicht verfügbar, nutze nur lokale Datei.")
        with open(xsd_path, 'rb') as f:
            return f.read(), 'local'
    
    # VERSUCH 1: Direkter Abruf
    try:
        print("  -> Versuch 1: Direkter Abruf des Schemas von loc.gov...")
        response = requests.get(PREMIS_XSD_URL, timeout=10)
        response.raise_for_status()
        print("     [OK] Schema erfolgreich online geladen.")
        return response.content, 'online'
    except Exception as e1:
        print(f"     [WARNUNG] Versuch 1 fehlgeschlagen: {e1}")
        
        # VERSUCH 2: Abruf mit Browser-User-Agent
        try:
            print("  -> Versuch 2: Abruf mit Browser-User-Agent...")
            headers = {'User-Agent': BROWSER_USER_AGENT}
            response = requests.get(PREMIS_XSD_URL, headers=headers, timeout=10)
            response.raise_for_status()
            print("     [OK] Schema erfolgreich online geladen (via User-Agent-Fallback).")
            return response.content, 'online_user_agent'
        except Exception as e2:
            print(f"     [WARNUNG] Versuch 2 fehlgeschlagen: {e2}")
            
            # VERSUCH 3: Lokale Datei
            print(f"  -> Versuch 3: Verwende lokale Schema-Datei: {xsd_path}")
            with open(xsd_path, 'rb') as f:
                return f.read(), 'local'


def validate_premis(xml_path, xsd_path):
    """
    Validiert die PREMIS-XML gegen das XSD-Schema.
    Gibt (is_valid, errors, ignored_count) zurück.
    """
    
    errors = []
    ignored_count = 0
    
    try:
        # XSD-Schema laden (mit Fallback)
        print("  Loading XSD schema...")
        schema_content, source = load_schema_with_fallback(xsd_path)
        print(f"  Schema source: {source}")
        
        schema_root = etree.XML(schema_content)
        schema = etree.XMLSchema(schema_root)
        print("  XSD schema loaded successfully.")
        
        # XML-Datei laden
        print("  Loading PREMIS XML file...")
        with open(xml_path, 'rb') as f:
            xml_doc = etree.parse(f)
        print("  PREMIS XML loaded successfully.")
        
        # Validierung durchführen
        print("  Validating...")
        is_valid = schema.validate(xml_doc)
        
        # Fehler sammeln und FileTrove-Warnungen filtern
        for error in schema.error_log:
            message = str(error.message)
            line = error.line
            
            # Prüfen ob es eine ignorierte Erweiterung ist
            is_ignored = any(ns in message for ns in IGNORED_NAMESPACES)
            
            if is_ignored:
                ignored_count += 1
            else:
                errors.append(f"ERROR (Line {line}): {message}")
        
        return is_valid, errors, ignored_count
        
    except etree.XMLSyntaxError as e:
        return False, [f"XML SYNTAX ERROR: {e}"], 0
    except etree.XMLSchemaParseError as e:
        return False, [f"XSD SCHEMA ERROR: {e}"], 0
    except Exception as e:
        return False, [f"UNEXPECTED ERROR: {e}"], 0


def save_report(output_file, premis_file, xsd_file, version_name, 
                is_valid, errors, ignored_count):
    """Speichert den Validierungsbericht in eine Textdatei."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("PREMIS XML Validation Report\n")
        f.write("=" * 50 + "\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"PREMIS file: {premis_file}\n")
        f.write(f"XSD schema: {xsd_file}\n")
        f.write(f"Schema version: {version_name}\n")
        f.write("\n")
        
        if is_valid and not errors:
            f.write("RESULT: VALIDATION SUCCESSFUL\n")
            if ignored_count > 0:
                f.write(f"\nINFO: {ignored_count} FileTrove/Greaseweazle extension\n")
                f.write("warning(s) were automatically ignored (expected behavior).\n")
        else:
            f.write(f"RESULT: VALIDATION FAILED ({len(errors)} errors)\n")
            f.write("\nERRORS:\n")
            for error in errors:
                f.write(f"  {error}\n")
            if ignored_count > 0:
                f.write(f"\nINFO: {ignored_count} additional FileTrove/Greaseweazle\n")
                f.write("extension warning(s) were ignored.\n")


# ==============================================================================
# HAUPTPROGRAMM
# ==============================================================================

def main():
    print()
    print("=" * 50)
    print("  PREMIS XML Validator (Final Combined Version)")
    print("  Supports PREMIS v3.0")
    print("  Features: GUI Dialogs + 3-Stage Schema Fallback")
    print("           + FileTrove Extension Filtering")
    print("=" * 50)
    print()
    
    # Schritt 1: PREMIS-Datei auswählen
    print("Step 1: Please select PREMIS XML file...")
    premis_file = select_file(
        title="Select PREMIS XML file",
        filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
    )
    
    if not premis_file:
        print("Aborted: No PREMIS file selected.")
        input("Press Enter to exit...")
        return
    
    print(f"  Selected: {premis_file}")
    
    # Schritt 2: XSD-Schema auswählen
    print()
    print("Step 2: Please select PREMIS XSD schema...")
    xsd_file = select_file(
        title="Select PREMIS XSD schema",
        filetypes=[("XSD files", "*.xsd"), ("All files", "*.*")]
    )
    
    if not xsd_file:
        print("Aborted: No XSD file selected.")
        input("Press Enter to exit...")
        return
    
    print(f"  Selected: {xsd_file}")
    
    # Schritt 3: Dateien prüfen
    print()
    print("Step 3: Checking files...")
    
    if not os.path.exists(premis_file):
        print("ERROR: PREMIS file not found.")
        input("Press Enter to exit...")
        return
    
    if not os.path.exists(xsd_file):
        print("ERROR: XSD file not found.")
        input("Press Enter to exit...")
        return
    
    premis_size = os.path.getsize(premis_file) / 1024
    xsd_size = os.path.getsize(xsd_file) / 1024
    print(f"  PREMIS file: {premis_size:.2f} KB")
    print(f"  XSD schema:  {xsd_size:.2f} KB")
    
    # Schritt 4: Schema-Version erkennen
    print()
    print("Step 4: Detecting schema version...")
    version, version_name, namespace = detect_schema_version(xsd_file)
    print(f"  Detected version: {version_name}")
    
    if version in ('unknown', 'custom', 'error'):
        print()
        print("  WARNING: Non-standard schema detected!")
        print(f"  Namespace: {namespace}")
        continue_validation = input("  Continue anyway? (y/n): ").lower()
        if continue_validation != 'y':
            print("Aborted by user.")
            return
    
    # Schritt 5: Validierung durchführen
    print()
    print("Step 5: Performing validation...")
    print()
    
    is_valid, errors, ignored_count = validate_premis(premis_file, xsd_file)
    
    # Schritt 6: Ergebnisse anzeigen
    print()
    print("=" * 50)
    print("  VALIDATION RESULT")
    print("=" * 50)
    print(f"  File:    {Path(premis_file).name}")
    print(f"  Schema:  {Path(xsd_file).name}")
    print(f"  Version: {version_name}")
    print()
    
    if is_valid and not errors:
        print("  " + "=" * 46)
        print("  [OK] VALIDATION SUCCESSFUL!")
        print("  The PREMIS file is fully conformant.")
        print("  " + "=" * 46)
        
        if ignored_count > 0:
            print()
            print(f"  INFO: {ignored_count} warning(s) from custom extensions")
            print("        (FileTrove/Greaseweazle namespace) were ignored.")
    else:
        print("  " + "=" * 46)
        print(f"  [FAIL] VALIDATION FAILED!")
        print(f"  {len(errors)} error(s) found.")
        print("  " + "=" * 46)
        print()
        print("  ERRORS:")
        print("  " + "-" * 43)
        for error in errors:
            print(f"  {error}")
        
        if ignored_count > 0:
            print()
            print(f"  INFO: {ignored_count} additional FileTrove/Greaseweazle")
            print("        extension warning(s) were ignored.")
    
    # Optional: Ergebnis speichern
    print()
    save_result = input("Save result to text file? (y/n): ").lower()
    
    if save_result == 'y':
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path(premis_file).parent
        output_file = output_dir / f"premis_validation_{timestamp}.txt"
        
        try:
            save_report(output_file, premis_file, xsd_file, version_name,
                       is_valid, errors, ignored_count)
            print(f"  Report saved: {output_file}")
        except Exception as e:
            print(f"  ERROR saving report: {e}")
    
    print()
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()