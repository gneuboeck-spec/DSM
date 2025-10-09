# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT


import os

# Arbeitsverzeichnis festlegen
base_path = "/Users/gregorneuboeck/Desktop/Sicherung_ZPH1082_011_Eisendle/ZPH1082_011_Eisendle Kopie"

# Alle .ps-Dateien rekursiv finden und löschen
deleted_count = 0
for root, dirs, files in os.walk(base_path):
    for filename in files:
        if filename.lower().endswith(".ps"):
            full_path = os.path.join(root, filename)
            try:
                os.remove(full_path)
                print(f"🗑️  Gelöscht: {full_path}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Fehler beim Löschen von {full_path}: {e}")

print(f"\n✅ Insgesamt {deleted_count} .ps-Dateien gelöscht.")
