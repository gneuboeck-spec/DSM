# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT


import os
import shutil
from collections import defaultdict, Counter
from pathlib import Path # Importiert das moderne Path-Modul

# ==============================================================================
# BITTE ANPASSEN: Geben Sie hier den Pfad zu Ihrem Quellordner an.

source_root = "C:\\Users\\digit\\Desktop\\ZPH1082_011_Eisendle"
# ==============================================================================
source_root = Path(r"C:\\Users\\digit\\Desktop\\ZPH1082_011_Eisendle")

# Ab hier werden Pfade mit dem pathlib-Modul verwaltet, was sie OS-unabhängig macht.
target_dir = source_root / "SAM"
log_file_path = source_root / "sam_file_mapping.txt"

# Erstellt das Zielverzeichnis, falls es nicht existiert.
target_dir.mkdir(exist_ok=True)

file_mappings = {}
existing_names = set()

# Zählt Originaldateien
original_name_counts = Counter()
file_origin_paths = defaultdict(list)

# Schritt 1: Alle SAM-Dateien im Quellverzeichnis (außer im Zielordner "SAM") finden und zählen.
print("🔎 Suche und zähle SAM-Dateien...")
for current_path in source_root.rglob('*.sam'):
    # Sicherstellen, dass die gefundene Datei nicht bereits im Zielordner liegt
    if not current_path.resolve().is_relative_to(target_dir.resolve()):
        original_name_counts[current_path.name.lower()] += 1
        file_origin_paths[current_path.name.lower()].append(current_path)

# Diese Struktur hilft, später die Dubletten-Gruppen sauber im Logfile auszugeben.
duplicates_output_list = defaultdict(list)

print(f"⚙️  Verarbeite {sum(original_name_counts.values())} gefundene Dateien...")
# Schritt 2: Dateien kopieren, bei Bedarf umbenennen und die Zuordnung speichern.
for original_name_lc, origin_paths in file_origin_paths.items():
    for original_path in origin_paths:
        base_name = original_path.stem  # Dateiname ohne Endung
        suffix = original_path.suffix # Dateiendung (z.B. ".sam")
        new_name = original_path.name

        counter = 1
        # Prüfen, ob eine Datei mit dem neuen Namen bereits im Zielordner existiert
        # oder der Name bereits für eine andere Datei in diesem Durchlauf vergeben wurde.
        while new_name.lower() in existing_names or (target_dir / new_name).exists():
            new_name = f"{base_name}{counter:03d}{suffix}"
            counter += 1

        existing_names.add(new_name.lower())
        target_path = target_dir / new_name
        shutil.copy2(original_path, target_path)

        # Informationen für das Logfile speichern
        file_mappings[new_name] = {
            "original_path": original_path,
            "original_name": original_path.name
        }
        
        # Informationen für die Dubletten-Ausgabe im Logfile speichern
        duplicates_output_list[original_path.name.lower()].append({
            "new_name": new_name,
            "original_path": original_path
        })

print("✍️  Schreibe Log-Datei...")
# Schritt 3: Logfile mit allen Zuordnungen schreiben.
with open(log_file_path, "w", encoding="utf-8") as log_file:
    # Sortiert die Einträge im Logfile nach dem neuen Dateinamen
    for new_name in sorted(file_mappings.keys()):
        info = file_mappings[new_name]
        original_name = info['original_name']
        original_path = info['original_path']
        
        log_file.write(f"{new_name} <-- {original_name} | {original_path}\n")
        
        original_name_lc = original_name.lower()
        # Wenn der ursprüngliche Dateiname mehr als einmal vorkam, ist es eine Dublette.
        if original_name_counts[original_name_lc] > 1:
            log_file.write("    ⚠️ Dubletten-Gruppe (gleicher Ursprungsname in verschiedenen Pfaden):\n")
            # Alle zugehörigen Kopien (Original und Duplikate) auflisten
            for dup_info in duplicates_output_list[original_name_lc]:
                log_file.write(f"        - {dup_info['new_name']} | {dup_info['original_path']}\n")
        log_file.write("\n")

print(f"✅ {len(file_mappings)} SAM-Dateien wurden erfolgreich verarbeitet.")
print(f"📄 Mapping-Datei gespeichert unter: {log_file_path}")