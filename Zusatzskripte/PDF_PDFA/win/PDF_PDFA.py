# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT


import subprocess
from datetime import datetime
import sys
from pathlib import Path

# ==============================================================================
# 🔧 BITTE ANPASSEN: Geben Sie hier die beiden Pfade für Ihr System an.
#
# 1. Der Pfad zu LibreOffice (soffice.exe)
#
# 2. Der Pfad zum Arbeitsordner, der die .sam.pdf-Dateien enthält.
# ==============================================================================
libreoffice_path = Path(r"C:\Program Files\LibreOffice\program\soffice.exe")
input_folder = Path(r"C:\Users\digit\Desktop\ZPH1082_011_Eisendle\ALLES\BANK")


# --- Ab hier keine Änderungen mehr notwendig ---

log_path = input_folder / "konvertierungslog.txt"

def log(msg):
    """Schreibt eine Nachricht mit Zeitstempel in die Log-Datei und auf die Konsole."""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
    # Sorge dafür, dass die Nachricht immer mit einem Zeilenumbruch endet
    log_message = timestamp + msg.strip() + "\n"
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_message)
        # Gib die Nachricht ohne Zeitstempel auf der Konsole aus
        print(msg.strip())
    except Exception as e:
        print(f"!! Kritischer Fehler beim Schreiben der Log-Datei: {e}")

def print_progress(current, total, filename):
    """Zeigt eine Fortschrittsanzeige in der Konsole an."""
    bar_length = 30
    filled_length = int(bar_length * current / total) if total > 0 else 0
    bar = "#" * filled_length + "." * (bar_length - filled_length)
    percent = (current / total) * 100 if total > 0 else 0
    # Kürzt lange Dateinamen für eine saubere Anzeige
    display_name = (filename[:47] + '...') if len(filename) > 50 else filename
    sys.stdout.write(f"\r[{bar}] {percent:5.1f}% ({current}/{total}) {display_name:50}")
    sys.stdout.flush()

# System-Voraussetzungen prüfen
if not libreoffice_path.exists():
    log(f"FEHLER: LibreOffice wurde nicht unter '{libreoffice_path}' gefunden. Bitte passen Sie den Pfad im Skript an.")
    sys.exit()

if not input_folder.is_dir():
    log(f"FEHLER: Der Eingabeordner '{input_folder}' existiert nicht. Bitte passen Sie den Pfad an.")
    sys.exit()

# Nur PDF-Dateien sammeln, die aus dem vorherigen Schritt stammen
all_files = list(input_folder.rglob("*.sam.pdf"))
total_files = len(all_files)

log(f"Insgesamt {total_files} .sam.pdf-Dateien zur Konvertierung gefunden.")

if total_files == 0:
    log("Keine .sam.pdf-Dateien gefunden. Skript wird beendet.")
    sys.exit()

# Jede PDF als ODG öffnen, daraus PDF/A erzeugen
for i, pdf_path in enumerate(all_files):
    print_progress(i + 1, total_files, pdf_path.name)
    
    # Pfade für Zwischen- und Zieldateien definieren
    # Aus "NAME.sam.pdf" wird "NAME.sam.odg"
    odg_path = pdf_path.with_suffix(".odg")
    
    # Der Ziel-Dateiname für das PDF/A ist derselbe wie der der Quelldatei
    pdfa_path = pdf_path 
    
    # LibreOffice erzeugt aus "NAME.sam.odg" eine Datei namens "NAME.sam.pdf".
    # Wir müssen diesen temporären Namen kennen, um ihn später umzubenennen/zu verschieben.
    temp_pdf_by_lo = odg_path.with_suffix(".pdf")

    try:
        # 1. Beende alle laufenden LibreOffice-Prozesse (Windows-Version)
        # Wir ignorieren Fehler, falls kein Prozess läuft.
        subprocess.run(
            ["taskkill", "/F", "/IM", "soffice.bin"],
            capture_output=True, text=True
        )

        # 2. Alte Zwischendateien löschen
        if odg_path.exists():
            odg_path.unlink()

        # 3. PDF in ODG umwandeln
        log(f"\n({i+1}/{total_files}) Erzeuge ODG aus: {pdf_path.name}")
        subprocess.run([
            str(libreoffice_path),
            "--headless", "--convert-to", "odg",
            "--outdir", str(pdf_path.parent),
            str(pdf_path)
        ], capture_output=True, check=True)

        if not odg_path.exists():
            log(f"[FEHLER] Konnte ODG nicht erzeugen für: {pdf_path.name}")
            log(f"         Erwartete Datei: {odg_path}")
            continue

        # 4. Alte Zieldatei löschen, um sie sicher zu überschreiben
        if pdfa_path.exists():
            pdfa_path.unlink()

        # 5. ODG nach PDF/A-2b exportieren
        log(f"Exportiere PDF/A-2b nach: {pdfa_path.name}")
        pdfa2_filter = "pdf:writer_pdf_Export:SelectPdfVersion=2"
        subprocess.run([
            str(libreoffice_path),
            "--headless", "--convert-to", pdfa2_filter,
            "--outdir", str(pdf_path.parent),
            str(odg_path)
        ], capture_output=True, check=True)

        # 6. Überprüfen und Aufräumen
        if temp_pdf_by_lo.exists():
            # LibreOffice hat die temporäre PDF erstellt.
            # Wenn der Zielname anders ist, benennen wir sie um.
            if temp_pdf_by_lo != pdfa_path:
                temp_pdf_by_lo.replace(pdfa_path)
            log(f"[OK] PDF/A-2b gespeichert: {pdfa_path.name}")
        else:
            log(f"[FEHLER] PDF/A-2b Export fehlgeschlagen für: {odg_path.name}")
            log(f"         Erwartete temporäre PDF: {temp_pdf_by_lo}")

    except subprocess.CalledProcessError as e:
        log(f"\n[FEHLER] Ein LibreOffice-Befehl ist fehlgeschlagen für: {pdf_path.name}")
        log(f"         Fehlermeldung: {e.stderr.strip()}")
    except Exception as e:
        log(f"\n[FEHLER] Unerwarteter Fehler bei der Verarbeitung von {pdf_path.name}: {e}")
    finally:
        # 7. ODG-Zwischendatei immer löschen
        if odg_path.exists():
            odg_path.unlink()

print() # Neue Zeile nach der Fortschrittsanzeige
log("Alle Konvertierungen abgeschlossen.")