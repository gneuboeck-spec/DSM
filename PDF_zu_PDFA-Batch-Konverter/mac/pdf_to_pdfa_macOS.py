import os
import subprocess
from datetime import datetime
import shutil
import sys

# Pfad zu LibreOffice
libreoffice_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"

# Arbeitsverzeichnis und Log-Datei
input_folder = "/Users/gregorneuboeck/Desktop/Sicherung_ZPH1082_011_Eisendle/ZPH1082_011_Eisendle Kopie/ALLES/ANSUCHEN"
log_path = os.path.join(input_folder, "konvertierungslog.txt")

pdfa2_filter = "pdf:writer_pdf_Export:SelectPdfVersion=2"

def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(timestamp + msg + "\n")
    print(msg)

def print_progress(current, total, filename):
    bar_length = 30
    filled_length = int(bar_length * current // total)
    bar = "#" * filled_length + "." * (bar_length - filled_length)
    percent = (current / total) * 100
    sys.stdout.write(f"\r[{bar}] {percent:5.1f}% ({current}/{total}) {filename[:50]:50}")
    sys.stdout.flush()

# Nur PDF-Dateien sammeln, die aus dem vorherigen Schritt stammen
all_files = []
for root, _, files in os.walk(input_folder):
    for filename in files:
        if filename.lower().endswith(".sam.pdf"):
            all_files.append((root, filename))

total_files = len(all_files)
log(f"Insgesamt {total_files} .sam.pdf-Dateien zur Konvertierung gefunden.")

if total_files == 0:
    log("Keine .sam.pdf-Dateien gefunden. Skript wird beendet.")
    sys.exit()

# Jede PDF als ODG öffnen, daraus PDF/A erzeugen
for i, (root, filename) in enumerate(all_files):
    print_progress(i + 1, total_files, filename)

    pdf_path = os.path.join(root, filename)
    
    # KORREKTUR 1: Wir leiten den Namen für die ODG-Datei jetzt anders ab.
    # LibreOffice wird aus "NAME.sam.pdf" eine Datei "NAME.sam.odg" machen.
    base_name_for_odg = os.path.splitext(filename)[0] # Ergibt "NAME.sam"
    odg_path = os.path.join(root, f"{base_name_for_odg}.odg") # Ergibt den Pfad zu "NAME.sam.odg"
    
    # Der Zielpfad für die finale PDF/A-Datei bleibt der gleiche wie die Quelldatei.
    pdfa_path = pdf_path 

    try:
        subprocess.call(["pkill", "-f", "soffice"])

        if os.path.exists(odg_path):
            os.remove(odg_path)

        log(f"\nErzeuge ODG aus: {filename}")
        subprocess.run([
            libreoffice_path,
            "--headless", "--convert-to", "odg",
            "--outdir", root,
            pdf_path
        ], capture_output=True)

        # Die Überprüfung bleibt gleich, da wir odg_path oben korrekt berechnet haben.
        if not os.path.exists(odg_path):
            log(f"\n[FEHLER] Konnte ODG nicht erzeugen: {filename}")
            # Debug-Info: Zeige an, welche Datei erwartet wurde
            log(f"         Erwartete Datei: {odg_path}")
            continue

        if os.path.exists(pdfa_path):
            os.remove(pdfa_path)

        log(f"Exportiere PDF/A-2b nach: {os.path.basename(pdfa_path)}")
        subprocess.run([
            libreoffice_path,
            "--headless", "--convert-to", pdfa2_filter,
            "--outdir", root,
            odg_path # Wir verwenden die .odg-Datei als Quelle
        ], capture_output=True)
        
        # KORREKTUR 2: Der Name der von LibreOffice erstellten PDF basiert auf dem Namen der ODG-Datei.
        # Aus "NAME.sam.odg" wird "NAME.sam.pdf".
        temp_pdf_name_by_lo = os.path.join(root, f"{base_name_for_odg}.pdf")

        # KORREKTUR 3: Der Zielpfad ist bereits korrekt, wir müssen nur die temporäre Datei verschieben.
        # Die Überprüfung muss auf den Namen der temporären PDF-Datei lauten.
        if os.path.exists(temp_pdf_name_by_lo):
            # Da pdfa_path bereits der korrekte Zielname ist, ist diese `os.replace` korrekt.
            os.replace(temp_pdf_name_by_lo, pdfa_path)
            log(f"\n[OK] PDF/A-2b gespeichert: {os.path.basename(pdfa_path)}")
        else:
            log(f"\n[FEHLER] PDF/A-2b Export fehlgeschlagen für: {filename}")
            # Debug-Info: Zeige an, welche Datei erwartet wurde
            log(f"         Erwartete temporäre PDF: {temp_pdf_name_by_lo}")

        if os.path.exists(odg_path):
            os.remove(odg_path)

    except Exception as e:
        log(f"\n[FEHLER] Unerwarteter Fehler bei der Verarbeitung von {filename}: {e}")

print()
log("Alle Konvertierungen abgeschlossen.")