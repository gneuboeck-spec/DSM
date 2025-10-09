# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT


import os
import shutil
from collections import defaultdict, Counter

# Pfade bitte nach Wunsch anpassen
source_root = "/Users/gregorneuboeck/Desktop/Sicherung_ZPH1082_011_Eisendle/ZPH1082_011_Eisendle Kopie"
target_dir = os.path.join(source_root, "SAM")
log_file_path = os.path.join(source_root, "sam_file_mapping.txt")

os.makedirs(target_dir, exist_ok=True)

file_mappings = {}
existing_names = set()

# Zählt Originaldateien
original_name_counts = Counter()
file_origin_paths = defaultdict(list)

# Vorab: alle SAM-Dateien zählen (ohne SAM-Ordner)
for root, dirs, files in os.walk(source_root):
    dirs[:] = [d for d in dirs if os.path.abspath(os.path.join(root, d)) != os.path.abspath(target_dir)]
    for file in files:
        if file.lower().endswith(".sam"):
            original_name_counts[file.lower()] += 1
            file_origin_paths[file.lower()].append(os.path.join(root, file))

# Zusätzlich: mapping von Originalname → Liste von Zielnamen mit Pfad
duplicates_output_list = defaultdict(list)

# Kopieren und Zielnamen vergeben
for root, dirs, files in os.walk(source_root):
    dirs[:] = [d for d in dirs if os.path.abspath(os.path.join(root, d)) != os.path.abspath(target_dir)]
    for file in files:
        if file.lower().endswith(".sam"):
            original_path = os.path.join(root, file)
            base_name = os.path.splitext(file)[0]
            new_name = file

            counter = 1
            while new_name.lower() in existing_names or os.path.exists(os.path.join(target_dir, new_name)):
                new_name = f"{base_name}{counter:03d}.sam"
                counter += 1

            existing_names.add(new_name.lower())
            target_path = os.path.join(target_dir, new_name)
            shutil.copy2(original_path, target_path)

            file_mappings[new_name] = {
                "original_path": original_path,
                "original_name": file
            }

            # Neue Datenstruktur für saubere Dublettengruppe
            duplicates_output_list[file.lower()].append({
                "new_name": new_name,
                "original_path": original_path
            })

# Logfile schreiben
with open(log_file_path, "w", encoding="utf-8") as log_file:
    for new_name, info in file_mappings.items():
        log_file.write(f"{new_name} <-- {info['original_name']} | {info['original_path']}\n")
        
        original_name_lc = info["original_name"].lower()
        if original_name_counts[original_name_lc] > 1:
            log_file.write("    ⚠️ Dubletten-Gruppe (gleicher Ursprungsname in verschiedenen Pfaden):\n")
            for dup in duplicates_output_list[original_name_lc]:
                log_file.write(f"        - {dup['new_name']} | {dup['original_path']}\n")
        log_file.write("\n")

print(f"✅ {len(file_mappings)} SAM-Dateien wurden verarbeitet.")
print(f"📄 Mapping-Datei gespeichert unter: {log_file_path}")







































































