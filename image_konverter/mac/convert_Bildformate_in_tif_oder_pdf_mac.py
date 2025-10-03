# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import subprocess
from datetime import datetime
import sys

# --- KONFIGURATION ---
input_folder = "/Users/gregorneuboeck/Desktop/Bildformate_konvertieren"
logfile_path = "/Users/gregorneuboeck/Desktop/konvertierungs_log.txt"

# Pfade zu den Kommandozeilen-Tools
# 'magick' sollte im System-PATH sein. Bei Inkscape ist der volle Pfad oft stabiler.
imagemagick_path = "magick"
inkscape_path = "/Applications/Inkscape.app/Contents/MacOS/inkscape"

# Listen der unterstützten Formate, getrennt nach Typ
raster_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".heic", ".tga", ".gif", ".jfif"}
vector_extensions = {".svg", ".eps", ".ai", ".pdf", ".wmf"}

# Zieldateiendungen (zur einfachen Anpassung)
raster_target_ext = ".tiff"
vector_target_ext = ".pdf"
# --- ENDE DER KONFIGURATION ---


# --- Sicherheits-Check ---
print("="*60)
print(f"INFO: Das Skript wird den folgenden Ordner durchsuchen:")
print(f"-> {input_folder}")
if not os.path.isdir(input_folder):
    print("\nFEHLER: Der oben angegebene Ordner existiert nicht.")
    print("Bitte korrigieren Sie die Variable 'input_folder' im Skript.")
    sys.exit(1)
print("="*60)
# --- Ende des Sicherheits-Checks ---


# --- Globale Variablen ---
converted_count = 0
skipped_count = 0
error_count = 0
log_lines = []
all_files = []


# --- Dateisuche ---
print("Suche nach unterstützten Grafikdateien...")
supported_extensions = tuple(raster_extensions | vector_extensions)

for root, _, files in os.walk(input_folder):
    for filename in files:
        # Ignoriere versteckte Dateien und temporäre Dateien
        if filename.startswith('.') or filename.startswith('~'):
            continue
        if filename.lower().endswith(supported_extensions):
            all_files.append(os.path.join(root, filename))

total = len(all_files)
print(f"{total} relevante Grafikdateien im angegebenen Ordner gefunden.")
if total == 0:
    sys.exit()

# --- Hauptverarbeitung ---
print("\nStarte universelle Grafik-Konvertierung...")

for idx, abs_path in enumerate(all_files, 1):
    rel_path = os.path.relpath(abs_path, input_folder)
    root, filename = os.path.split(abs_path)
    base, ext = os.path.splitext(filename)
    ext = ext.lower()

    # Fortschrittsanzeige
    percent = (idx / total) * 100
    print(f"[{idx}/{total}] {percent:6.2f}% → {rel_path}")
    log_lines.append(f"\n--- Verarbeite: {filename} ---")

    # --- Intelligente Weiche: Wähle Werkzeug und Zielformat ---
    if ext in raster_extensions:
        tool_name = "ImageMagick"
        tool_path = imagemagick_path
        target_ext = raster_target_ext
        output_filename = f"{base}{ext}{target_ext}"
        output_path = os.path.join(root, output_filename)
        cmd = [tool_path, abs_path, output_path]

    elif ext in vector_extensions:
        tool_name = "Inkscape"
        tool_path = inkscape_path
        target_ext = vector_target_ext
        output_filename = f"{base}{ext}{target_ext}"
        output_path = os.path.join(root, output_filename)
        # ROBUSTER BEFEHL: Konvertiert Text in Pfade, um Schriftart-Probleme zu vermeiden.
        # Dies ist kein offizielles PDF/A, aber eine sehr stabile Archivierungsform.
        cmd = [tool_path, abs_path, f"--export-filename={output_path}", "--export-text-to-path", "--export-pdf-version=1.5"]
    
    else:
        log_lines.append(f"[INFO] Unbekannter Dateityp '{ext}', wird übersprungen.")
        continue

    # Prüfen, ob Zieldatei bereits existiert
    if os.path.exists(output_path):
        log_lines.append(f"[ÜBERSPRUNGEN] Zieldatei existiert bereits: {output_filename}")
        skipped_count += 1
        continue

    # Den passenden Befehl ausführen
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            converted_count += 1
            log_lines.append(f"[OK] Konvertiert mit {tool_name}: {filename} → {output_filename}")
        else:
            # Fehlerfall: Das Tool lief, aber meldete einen Fehler
            error_count += 1
            log_lines.append(f"[FEHLER] {tool_name} hat einen Fehler gemeldet für: {filename}")
            log_lines.append(f"       Befehl: {' '.join(cmd)}")
            log_lines.append(f"       Fehlermeldung: {result.stderr.strip()}")

    except FileNotFoundError:
        # Fehlerfall: Das Tool selbst wurde nicht gefunden
        error_count += 1
        log_lines.append(f"[KRITISCHER FEHLER] Befehl '{tool_path}' nicht gefunden.")
        log_lines.append(f"                  Ist {tool_name} installiert und der Pfad in der Konfiguration korrekt?")
    except Exception as e:
        # Allgemeiner Fehler
        error_count += 1
        log_lines.append(f"[FEHLER] Ein unerwartetes Problem ist aufgetreten bei: {filename} ({e})")

# --- Logfile schreiben ---
with open(logfile_path, "w", encoding="utf-8") as log_file:
    log_file.write(f"LOG VOM {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    log_file.write("--- ZUSAMMENFASSUNG ---\n")
    log_file.write(f"Verarbeitete Dateien insgesamt: {total}\n")
    log_file.write(f"Erfolgreich konvertiert: {converted_count}\n")
    log_file.write(f"Übersprungen (existierten bereits): {skipped_count}\n")
    log_file.write(f"Fehler bei Konvertierung: {error_count}\n")
    log_file.write("\n--- DETAILLIERTES PROTOKOLL ---\n")
    log_file.write("".join(log_lines))

print(f"\nFertig. {converted_count} Dateien konvertiert, {skipped_count} übersprungen, {error_count} Fehler.")
print(f"Log gespeichert unter: {logfile_path}")
