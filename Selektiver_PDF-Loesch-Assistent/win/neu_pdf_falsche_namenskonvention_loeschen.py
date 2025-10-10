# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
from pathlib import Path
from datetime import datetime

# ==============================================================================
# 🔧 KONFIGURATION
# ==============================================================================

# 1. Pfad zum Arbeitsordner (bitte anpassen)
base_path = Path(r"C:\Users\digit\Desktop\ZPH1082_011_Eisendle")

# 2. Schwellenjahr für die Löschung (inklusive dieses Jahres)
min_year = 2025

# 3. SICHERHEITSMODUS:
# True  = Zeigt nur an, was gelöscht werden würde (Simulation).
# False = LÖSCHT DIE DATEIEN WIRKLICH.
DRY_RUN = True

# ==============================================================================
# --- Logik ---
# ==============================================================================

if DRY_RUN:
    print("🚨 SIMULATIONSMODUS AKTIV. Es werden keine Dateien gelöscht.")
    print("   Setzen Sie 'DRY_RUN = False' im Skript, um scharf zu schalten.\n")

if not base_path.is_dir():
    print(f"❌ FEHLER: Der Ordner '{base_path}' existiert nicht.")
    exit()

print(f"Analysiere PDFs in: {base_path}")
print(f"Kriterien: Einfache .pdf Endung UND erstellt >= {min_year}\n")

deleted_count = 0
skipped_count = 0
checked_count = 0

# Rekursiv alle PDF-Dateien suchen
# Groß-/Kleinschreibung wird durch .lower() im Vergleich ignoriert
for pdf_path in base_path.rglob("*.[pP][dD][fF]"):
    checked_count += 1
    
    # --- KRITERIUM 1: Namenskonvention prüfen ---
    # pdf_path.name      -> "Dokument.doc.pdf" oder "Rechnung.pdf"
    # pdf_path.stem      -> "Dokument.doc"     oder "Rechnung"
    # Path(stem).suffix  -> ".doc"             oder ""
    
    # Wir holen uns den Dateinamen OHNE .pdf
    stem_path = Path(pdf_path.stem)
    
    # Wenn der Rest noch eine Endung hat (z.B. .doc), behalten wir die Datei.
    if stem_path.suffix != "":
        # Datei folgt dem Schema Name.AlteEndung.pdf -> BEHALTEN
        skipped_count += 1
        continue

    # --- KRITERIUM 2: Erstellungsdatum prüfen ---
    try:
        # st_ctime ist unter Windows das Erstellungsdatum
        stats = pdf_path.stat()
        creation_time = datetime.fromtimestamp(stats.st_ctime)
        
        if creation_time.year < min_year:
            # Datei ist zu alt -> BEHALTEN
            skipped_count += 1
            continue
            
        # --- LÖSCHVORGANG ---
        # Wenn wir hier ankommen, ist es ein "Name.pdf" ab Jahr 2025
        prefix = "[SIMULATION] Würde löschen" if DRY_RUN else "🗑️  Gelöscht"
        date_str = creation_time.strftime("%Y-%m-%d")
        
        print(f"{prefix}: {pdf_path.name} (Erstellt: {date_str})")
        
        if not DRY_RUN:
            pdf_path.unlink()
            
        deleted_count += 1

    except Exception as e:
        print(f"❌ Fehler beim Zugriff auf {pdf_path.name}: {e}")

# --- Abschlussbericht ---
print("-" * 40)
status = "simuliert gelöscht" if DRY_RUN else "tatsächlich gelöscht"
print(f"Analyse abgeschlossen.")
print(f"Geprüfte PDFs: {checked_count}")
print(f"Behalten (Kriterien nicht erfüllt): {skipped_count}")
print(f"Dateien {status}: {deleted_count}")

if DRY_RUN and deleted_count > 0:
    print("\n⚠️  Wenn das Ergebnis korrekt aussieht, setzen Sie DRY_RUN = False")
    print("    im Skript und führen Sie es erneut aus.")