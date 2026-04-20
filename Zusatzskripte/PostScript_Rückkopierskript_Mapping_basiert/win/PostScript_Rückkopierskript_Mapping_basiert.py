# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT


import shutil
from pathlib import Path # Modernes Modul zur Pfad-Verwaltung, ideal für Windows

# ==============================================================================
# 🔧 BITTE ANPASSEN: Geben Sie hier die beiden Pfade für Ihr System an.
#
# 1. Der Pfad zum Ordner, in dem die kopierten SAM- und PS-Dateien liegen.
# Beispiel: sam_dir = Path(r"C:\Users\digit\Desktop\Sicherung\SAM")
#
# 2. Der Pfad zur Log-Datei, die beim ersten Kopiervorgang erstellt wurde.
# Beispiel: log_file_path = Path(r"C:\Users\digit\Desktop\Sicherung\sam_file_mapping.txt")
# ==============================================================================
sam_dir = Path(r"C:\Users\digit\Desktop\ZPH1082_011_Eisendle\SAM")
log_file_path = Path(r"C:\Users\digit\Desktop\ZPH1082_011_Eisendle\sam_file_mapping.txt")


# --- Ab hier keine Änderungen mehr notwendig ---

# Überprüfung, ob die benötigten Dateien/Ordner existieren, bevor wir starten.
if not sam_dir.is_dir():
    print(f"❌ FEHLER: Das Quellverzeichnis '{sam_dir}' wurde nicht gefunden oder ist kein Ordner.")
    exit()

if not log_file_path.is_file():
    print(f"❌ FEHLER: Die Log-Datei '{log_file_path}' wurde nicht gefunden.")
    exit()

print(f"📖 Lese Log-Datei: '{log_file_path}'")
print(f"📁 Lese Quelldateien aus: '{sam_dir}'")
print("-" * 40)

# Öffne die Log-Datei zum Lesen.
try:
    with open(log_file_path, "r", encoding="utf-8") as log_file:
        for line in log_file:
            line = line.strip()
            # Verarbeite nur Zeilen, die eine Zuordnung enthalten
            if "<--" in line and "|" in line:
                try:
                    # Zerlege die Log-Zeile in ihre Bestandteile
                    new_name_part, original_part = line.split("<--")
                    original_name_part, original_path_str = original_part.split("|")

                    new_name = new_name_part.strip()
                    original_path = Path(original_path_str.strip()) # Wandle den String in ein Path-Objekt um

                    # 1. Den Pfad zur Quelldatei im SAM-Ordner zusammensetzen
                    #    Der Dateiname der .ps-Datei basiert auf dem neuen Namen der .sam-Datei.
                    #    Beispiel: aus "DATEI001.sam" wird "DATEI001.ps" gesucht.
                    ps_source_name = Path(new_name).with_suffix(".ps")
                    ps_source_path = sam_dir / ps_source_name

                    # 2. Den Zielpfad für die .ps-Datei zusammensetzen
                    #    Die Datei soll in ihrem Ursprungsordner mit der Endung .ps landen.
                    #    Beispiel: aus "...\ursprung\DATEI.sam" wird "...\ursprung\DATEI.ps"
                    ps_target_path = original_path.with_suffix(".ps")

                    # 3. Kopieren, wenn die Quelldatei existiert
                    if ps_source_path.exists():
                        # Sicherstellen, dass der Zielordner existiert
                        ps_target_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        shutil.copy2(ps_source_path, ps_target_path)
                        print(f"✅ Kopiert: '{ps_source_path.name}' → '{ps_target_path}'")
                    else:
                        print(f"⚠️  Datei nicht gefunden und übersprungen: {ps_source_path}")

                except ValueError:
                    # Fängt Fehler ab, wenn eine Zeile nicht korrekt aufgeteilt werden kann
                    print(f"❓ Zeile hat ein unerwartetes Format und wird ignoriert: {line}")
                except Exception as e:
                    # Fängt andere unerwartete Fehler bei der Verarbeitung einer Zeile ab
                    print(f"❌ Fehler bei der Verarbeitung von Zeile: {line}\n   → {e}")

except Exception as e:
    print(f"❌ Ein kritischer Fehler ist beim Lesen der Log-Datei aufgetreten: {e}")

print("-" * 40)
print("✅ Skript beendet.")