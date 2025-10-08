import os
import subprocess

# 🔧 Verzeichnis mit den PS-Dateien
ps_dir = "/Users/gregorneuboeck/Desktop/Sicherung_ZPH1082_011_Eisendle/ZPH1082_011_Eisendle Kopie/"

# 🔧 Ghostscript-Binärpfad
gs_path = "/usr/local/bin/gs"

# 🔁 Durchlaufe rekursiv alle PS-Dateien
for root, dirs, files in os.walk(ps_dir):
    for filename in files:
        if filename.lower().endswith(".ps"):
            ps_path = os.path.join(root, filename)
            pdf_path = os.path.splitext(ps_path)[0] + ".pdf"

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
                subprocess.run(command, check=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ Fehler bei {filename}: {e}")

print("✅ Alle PS-Dateien wurden in PDFs konvertiert.")