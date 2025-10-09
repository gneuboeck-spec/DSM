# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT


import os
import shutil

# 🔧 Pfade anpassen
sam_dir = "/Users/gregorneuboeck/Desktop/Sicherung_ZPH1082_011_Eisendle/ZPH1082_011_Eisendle Kopie/SAM"
log_file_path = "/Users/gregorneuboeck/Desktop/Sicherung_ZPH1082_011_Eisendle/ZPH1082_011_Eisendle Kopie/sam_file_mapping.txt"

with open(log_file_path, "r", encoding="utf-8") as log_file:
    for line in log_file:
        line = line.strip()
        if "<--" in line and "|" in line:
            try:
                # Zerlege Logzeile
                new_name, original = line.split("<--")
                original_name, original_path = original.split("|")

                new_name = new_name.strip()
                original_name = original_name.strip()
                original_path = original_path.strip()

                # 🔄 Zielverzeichnis und neue Dateiendung .ps
                original_dir = os.path.dirname(original_path)
                base_name = os.path.splitext(os.path.basename(original_path))[0]
                ps_target_name = base_name + ".ps"
                ps_target_path = os.path.join(original_dir, ps_target_name)

                # 📁 Quelle im SAM-Ordner
                ps_source_name = os.path.splitext(new_name)[0] + ".ps"
                ps_source_path = os.path.join(sam_dir, ps_source_name)

                # ✅ Kopieren, wenn vorhanden
                if os.path.exists(ps_source_path):
                    shutil.copy2(ps_source_path, ps_target_path)
                    print(f"✅ Kopiert: {ps_source_path} → {ps_target_path}")
                else:
                    print(f"⚠️  Datei nicht gefunden: {ps_source_path}")

            except Exception as e:
                print(f"❌ Fehler bei Zeile: {line}\n   → {e}")






































