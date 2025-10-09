import os
import subprocess

# 🔧 Verzeichnis mit den PS-Dateien
ps_dir = "/Users/gregorneuboeck/Desktop/Sicherung_ZPH1082_011_Eisendle/ZPH1082_011_Eisendle Kopie/ALLES/ANSUCHEN"

# 🔧 Ghostscript-Binärpfad
gs_path = "/usr/local/bin/gs"

# 🔁 Durchlaufe rekursiv alle PS-Dateien
for root, dirs, files in os.walk(ps_dir):
    for filename in files:
        if filename.lower().endswith(".ps"):
            ps_path = os.path.join(root, filename)
            base_name, _ = os.path.splitext(ps_path) # NEU: Basenamen ohne Endung extrahieren

            # NEU: Prüfen, ob eine zugehörige .sam-Datei existiert
            sam_path = base_name + ".sam"
            if os.path.exists(sam_path):
                # Fall 1: .sam-Datei existiert -> Zieldatei ist .sam.pdf
                pdf_path = base_name + ".sam.pdf"
                print(f"📄 Konvertiere (SAM-Version): {ps_path} → {pdf_path}")
            else:
                # Fall 2: Keine .sam-Datei -> Zieldatei ist wie bisher .pdf
                pdf_path = base_name + ".pdf"
                print(f"📄 Konvertiere: {ps_path} → {pdf_path}")

            command = [
                gs_path,
                "-dBATCH",
                "-dNOPAUSE",
                "-sDEVICE=pdfwrite",
                f"-sOutputFile={pdf_path}",
                ps_path
            ]

            try:
                # NEU: Vor dem Konvertieren eine eventuell existierende Zieldatei löschen
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                subprocess.run(command, check=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ Fehler bei {filename}: {e}")
            except OSError as e: # NEU: Fehler beim Löschen abfangen
                print(f"❌ Fehler beim Löschen der alten Zieldatei {pdf_path}: {e}")

print("✅ Alle PS-Dateien wurden in PDFs konvertiert.")