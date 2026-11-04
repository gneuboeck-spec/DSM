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

# ==============================================================================
# 🔧 FARB-INITIALISIERUNG (Konsistenz mit allen anderen Skripten)
# ==============================================================================
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class Fore: GREEN = RED = YELLOW = CYAN = MAGENTA = WHITE = ""
    class Style: RESET_ALL = ""

# GUI-Importe
import tkinter as tk
from tkinter import filedialog, messagebox

# XML-Verarbeitung
try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    print(f"{Fore.RED}FEHLER: lxml nicht installiert!{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Bitte installieren: pip install lxml{Style.RESET_ALL}")
    input(f"{Fore.YELLOW}Drücke Enter zum Beenden...{Style.RESET_ALL}")
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
        print(f"  {Fore.YELLOW}[INFO] requests nicht verfügbar, nutze nur lokale Datei.{Style.RESET_ALL}")
        with open(xsd_path, 'rb') as f:
            return f.read(), 'local'
    
    # VERSUCH 1: Direkter Abruf
    try:
        print(f"  {Fore.CYAN}-> Versuch 1: Direkter Abruf des Schemas von loc.gov...{Style.RESET_ALL}")
        response = requests.get(PREMIS_XSD_URL, timeout=10)
        response.raise_for_status()
        print(f"     {Fore.GREEN}[OK] Schema erfolgreich online geladen.{Style.RESET_ALL}")
        return response.content, 'online'
    except Exception as e1:
        print(f"     {Fore.YELLOW}[WARNUNG] Versuch 1 fehlgeschlagen: {e1}{Style.RESET_ALL}")
        
        # VERSUCH 2: Abruf mit Browser-User-Agent
        try:
            print(f"  {Fore.CYAN}-> Versuch 2: Abruf mit Browser-User-Agent...{Style.RESET_ALL}")
            headers = {'User-Agent': BROWSER_USER_AGENT}
            response = requests.get(PREMIS_XSD_URL, headers=headers, timeout=10)
            response.raise_for_status()
            print(f"     {Fore.GREEN}[OK] Schema erfolgreich online geladen (via User-Agent-Fallback).{Style.RESET_ALL}")
            return response.content, 'online_user_agent'
        except Exception as e2:
            print(f"     {Fore.YELLOW}[WARNUNG] Versuch 2 fehlgeschlagen: {e2}{Style.RESET_ALL}")
            
            # VERSUCH 3: Lokale Datei
            print(f"  {Fore.CYAN}-> Versuch 3: Verwende lokale Schema-Datei: {xsd_path}{Style.RESET_ALL}")
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
        print(f"  {Fore.CYAN}Loading XSD schema...{Style.RESET_ALL}")
        schema_content, source = load_schema_with_fallback(xsd_path)
        print(f"  {Fore.WHITE}Schema source: {source}{Style.RESET_ALL}")
        
        schema_root = etree.XML(schema_content)
        schema = etree.XMLSchema(schema_root)
        print(f"  {Fore.GREEN}XSD schema loaded successfully.{Style.RESET_ALL}")
        
        # XML-Datei laden
        print(f"  {Fore.CYAN}Loading PREMIS XML file...{Style.RESET_ALL}")
        with open(xml_path, 'rb') as f:
            xml_doc = etree.parse(f)
        print(f"  {Fore.GREEN}PREMIS XML loaded successfully.{Style.RESET_ALL}")
        
        # Validierung durchführen
        print(f"  {Fore.CYAN}Validating...{Style.RESET_ALL}")
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
    print(f"{Fore.MAGENTA}{'=' * 50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  PREMIS XML Validator (Final Combined Version){Style.RESET_ALL}")
    print(f"{Fore.CYAN}  Supports PREMIS v3.0{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  Features: GUI Dialogs + 3-Stage Schema Fallback{Style.RESET_ALL}")
    print(f"{Fore.CYAN}           + FileTrove Extension Filtering{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'=' * 50}{Style.RESET_ALL}")
    print()
    
    # Schritt 1: PREMIS-Datei auswählen
    print(f"{Fore.CYAN}Step 1: Please select PREMIS XML file...{Style.RESET_ALL}")
    premis_file = select_file(
        title="Select PREMIS XML file",
        filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
    )
    
    if not premis_file:
        print(f"{Fore.RED}Aborted: No PREMIS file selected.{Style.RESET_ALL}")
        input(f"{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")
        return
    
    print(f"  {Fore.GREEN}Selected:{Style.RESET_ALL} {Fore.WHITE}{premis_file}{Style.RESET_ALL}")
    
    # Schritt 2: XSD-Schema auswählen
    print()
    print(f"{Fore.CYAN}Step 2: Please select PREMIS XSD schema...{Style.RESET_ALL}")
    xsd_file = select_file(
        title="Select PREMIS XSD schema",
        filetypes=[("XSD files", "*.xsd"), ("All files", "*.*")]
    )
    
    if not xsd_file:
        print(f"{Fore.RED}Aborted: No XSD file selected.{Style.RESET_ALL}")
        input(f"{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")
        return
    
    print(f"  {Fore.GREEN}Selected:{Style.RESET_ALL} {Fore.WHITE}{xsd_file}{Style.RESET_ALL}")
    
    # Schritt 3: Dateien prüfen
    print()
    print(f"{Fore.CYAN}Step 3: Checking files...{Style.RESET_ALL}")
    
    if not os.path.exists(premis_file):
        print(f"{Fore.RED}ERROR: PREMIS file not found.{Style.RESET_ALL}")
        input(f"{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")
        return
    
    if not os.path.exists(xsd_file):
        print(f"{Fore.RED}ERROR: XSD file not found.{Style.RESET_ALL}")
        input(f"{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")
        return
    
    premis_size = os.path.getsize(premis_file) / 1024
    xsd_size = os.path.getsize(xsd_file) / 1024
    print(f"  {Fore.WHITE}PREMIS file: {premis_size:.2f} KB{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}XSD schema:  {xsd_size:.2f} KB{Style.RESET_ALL}")
    
    # Schritt 4: Schema-Version erkennen
    print()
    print(f"{Fore.CYAN}Step 4: Detecting schema version...{Style.RESET_ALL}")
    version, version_name, namespace = detect_schema_version(xsd_file)
    print(f"  {Fore.GREEN}Detected version: {version_name}{Style.RESET_ALL}")
    
    if version in ('unknown', 'custom', 'error'):
        print()
        print(f"  {Fore.YELLOW}WARNING: Non-standard schema detected!{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}Namespace: {namespace}{Style.RESET_ALL}")
        continue_validation = input(f"  {Fore.YELLOW}Continue anyway? (y/n): {Style.RESET_ALL}").lower()
        if continue_validation != 'y':
            print(f"{Fore.CYAN}Aborted by user.{Style.RESET_ALL}")
            return
    
    # Schritt 5: Validierung durchführen
    print()
    print(f"{Fore.CYAN}Step 5: Performing validation...{Style.RESET_ALL}")
    print()
    
    is_valid, errors, ignored_count = validate_premis(premis_file, xsd_file)
    
    # Schritt 6: Ergebnisse anzeigen
    print()
    print(f"{Fore.MAGENTA}{'=' * 50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  VALIDATION RESULT{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'=' * 50}{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}File:    {Path(premis_file).name}{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}Schema:  {Path(xsd_file).name}{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}Version: {version_name}{Style.RESET_ALL}")
    print()
    
    if is_valid and not errors:
        print(f"  {Fore.MAGENTA}{'=' * 46}{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}[OK] VALIDATION SUCCESSFUL!{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}The PREMIS file is fully conformant.{Style.RESET_ALL}")
        print(f"  {Fore.MAGENTA}{'=' * 46}{Style.RESET_ALL}")
        
        if ignored_count > 0:
            print()
            print(f"  {Fore.CYAN}INFO: {ignored_count} warning(s) from custom extensions{Style.RESET_ALL}")
            print(f"  {Fore.CYAN}      (FileTrove/Greaseweazle namespace) were ignored.{Style.RESET_ALL}")
    else:
        print(f"  {Fore.MAGENTA}{'=' * 46}{Style.RESET_ALL}")
        print(f"  {Fore.RED}[FAIL] VALIDATION FAILED!{Style.RESET_ALL}")
        print(f"  {Fore.RED}{len(errors)} error(s) found.{Style.RESET_ALL}")
        print(f"  {Fore.MAGENTA}{'=' * 46}{Style.RESET_ALL}")
        print()
        print(f"  {Fore.RED}ERRORS:{Style.RESET_ALL}")
        print(f"  {Fore.MAGENTA}{'-' * 43}{Style.RESET_ALL}")
        for error in errors:
            print(f"  {Fore.RED}{error}{Style.RESET_ALL}")
        
        if ignored_count > 0:
            print()
            print(f"  {Fore.CYAN}INFO: {ignored_count} additional FileTrove/Greaseweazle{Style.RESET_ALL}")
            print(f"  {Fore.CYAN}      extension warning(s) were ignored.{Style.RESET_ALL}")
    
    # Optional: Ergebnis speichern
    print()
    save_result = input(f"{Fore.YELLOW}Save result to text file? (y/n): {Style.RESET_ALL}").lower()
    
    if save_result == 'y':
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path(premis_file).parent
        output_file = output_dir / f"premis_validation_{timestamp}.txt"
        
        try:
            save_report(output_file, premis_file, xsd_file, version_name,
                       is_valid, errors, ignored_count)
            print(f"  {Fore.GREEN}Report saved: {output_file}{Style.RESET_ALL}")
        except Exception as e:
            print(f"  {Fore.RED}ERROR saving report: {e}{Style.RESET_ALL}")
    
    print()
    input(f"{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")


if __name__ == "__main__":
    main()