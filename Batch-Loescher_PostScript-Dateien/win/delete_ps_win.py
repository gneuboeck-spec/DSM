# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

from pathlib import Path

# ==============================================================================
# 🔧 BITTE ANPASSEN: Geben Sie hier den Pfad zu Ihrem Arbeitsordner an.
# ==============================================================================
base_path = Path(r"C:\Users\digit\Desktop\ZPH1082_011_Eisendle") # <-- HIER IHREN PFAD EINFÜGEN

# --- Ab hier keine Änderungen mehr notwendig ---

# Überprüfen, ob der Pfad existiert
if not base_path.is_dir():
    print(f"❌ FEHLER: Der angegebene Ordner '{base_path}' existiert nicht.")
    print("Bitte passen Sie die Variable 'base_path' im Skript an.")
else:
    print(f"Suche nach .ps-Dateien im Ordner: {base_path}\n")
    
    # Alle .ps-Dateien rekursiv finden
    # .rglob("*.ps") durchsucht rekursiv alle Unterordner
    ps_files = list(base_path.rglob("*.ps"))
    deleted_count = 0
    
    for file_path in ps_files:
        try:
            file_path.unlink() # .unlink() ist die pathlib-Methode zum Löschen
            print(f"🗑️  Gelöscht: {file_path}")
            deleted_count += 1
        except Exception as e:
            print(f"❌ Fehler beim Löschen von {file_path}: {e}")

    print(f"\n✅ Insgesamt {deleted_count} .ps-Dateien gelöscht.")