# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT


import subprocess
from pathlib import Path # Modernes Modul zur Pfad-Verwaltung, ideal für Windows

# ==============================================================================
# 🔧 EINZIGE NOTWENDIGE ANPASSUNG:
#    Geben Sie hier den Pfad zum Ordner an, in dem sich Ihre .ps-Dateien befinden.
#
# Beispiel:
# ps_dir = Path(r"C:\Users\digit\Desktop\ZPH1082_011_Eisendle")
# ==============================================================================
ps_dir = Path(r"C:\Users\digit\Desktop\ZPH1082_011_Eisendle")

# ==============================================================================
#    Hier ist der vollständige Pfad zur Ghostscript-Anwendung.
# ==============================================================================
gs_path = Path(r"C:\Program Files\gs\gs10.06.0\bin\gswin64c.exe")


# Überprüfung, ob der Ghostscript-Pfad korrekt ist, bevor wir anfangen.
if not gs_path.exists():
    print(f"❌ FEHLER: Ghostscript wurde nicht unter '{gs_path}' gefunden.")
    print("Bitte überprüfen Sie den Pfad in der Variable 'gs_path' im Skript.")
    exit() # Bricht das Skript ab, wenn Ghostscript nicht gefunden wird.

# Überprüfung, ob der Quellordner existiert.
if not ps_dir.exists():
    print(f"❌ FEHLER: Der Quellordner '{ps_dir}' wurde nicht gefunden.")
    print("Bitte überprüfen Sie den Pfad in der Variable 'ps_dir' im Skript.")
    exit() # Bricht das Skript ab, wenn der Quellordner nicht existiert.

print(f"🔎 Durchsuche Ordner '{ps_dir}' nach .ps-Dateien...")

# 🔁 Durchlaufe rekursiv alle Dateien im Verzeichnis, die auf .ps enden.
#    Path.rglob ist die moderne Alternative zu os.walk.
for ps_file_path in ps_dir.rglob("*.ps"):
    
    # Prüfen, ob eine zugehörige .sam-Datei existiert (z.B. datei.ps -> datei.sam)
    sam_path = ps_file_path.with_suffix(".sam")
    
    if sam_path.exists():
        # Fall 1: .sam-Datei existiert -> Zieldatei ist .sam.pdf
        pdf_path = ps_file_path.with_suffix(".sam.pdf")
        print(f"📄 Konvertiere (SAM-Version): '{ps_file_path.name}' → '{pdf_path.name}'")
    else:
        # Fall 2: Keine .sam-Datei -> Zieldatei ist wie bisher .pdf
        pdf_path = ps_file_path.with_suffix(".pdf")
        print(f"📄 Konvertiere: '{ps_file_path.name}' → '{pdf_path.name}'")

    # Der Befehl, der an die Kommandozeile übergeben wird.
    # Die Pfade werden in Strings umgewandelt, da subprocess das erwartet.
    command = [
        str(gs_path),
        "-dBATCH",
        "-dNOPAUSE",
        "-sDEVICE=pdfwrite",
        f"-sOutputFile={str(pdf_path)}",
        str(ps_file_path)
    ]

    try:
        # Vor dem Konvertieren eine eventuell existierende Zieldatei löschen
        if pdf_path.exists():
            pdf_path.unlink()
            
        # Führe den Ghostscript-Befehl aus
        subprocess.run(command, check=True, capture_output=True, text=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler bei der Konvertierung von '{ps_file_path.name}':")
        print(f"   Ghostscript-Fehlermeldung: {e.stderr}")
    except OSError as e:
        print(f"❌ Fehler beim Löschen der alten Zieldatei '{pdf_path}': {e}")

print("\n✅ Alle .ps-Dateien wurden verarbeitet.")