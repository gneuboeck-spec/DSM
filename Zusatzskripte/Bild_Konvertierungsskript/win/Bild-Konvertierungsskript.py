# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import shutil

# ==============================================================================
# 🔧 KONFIGURATION
# ==============================================================================

# --- 1. System-Pfade und Listen (manuell anpassen, falls nötig) ---

# Pfade zu den Kommandozeilen-Tools
IMAGEMAGICK_PATH = "magick.exe"
INKSCAPE_PATH = r"C:\Program Files\Inkscape\bin\inkscape.exe" # Beispielpfad, ggf. anpassen
GHOSTSCRIPT_PATH = "gswin64c.exe"

# Listen der unterstützten Formate
# KORREKTUR: .tif und .tiff wurden aus den Quellformaten entfernt, da sie das Zielformat sind.
RASTER_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".heic", ".tga", ".gif", ".jfif"}
# Formate, für die Ghostscript direkt zuständig ist
GHOSTSCRIPT_FORMATS = {".eps", ".ai"}
# Restliche Vektorformate, für die Inkscape zuständig ist
VECTOR_EXTENSIONS = {".svg", ".wmf"}

# Zieldateiendungen
RASTER_TARGET_EXT = ".tiff"
VECTOR_TARGET_EXT = ".pdf"

# --- 2. Funktion zur dynamischen Erstellung und Validierung der Projekt-Pfade ---
def setup_and_validate_paths(ac_number, disk_archive_id):
    """
    Erstellt und validiert die Projekt-Pfade für das Bildkonvertierungsskript
    und prüft die Verfügbarkeit der externen Tools.

    Args:
        ac_number (str): Die AC-Nummer.
        disk_archive_id (str): Die Datenträger-ID.

    Returns:
        dict: Ein Dictionary mit den validierten Pfaden oder None bei einem Fehler.
    """
    project_base_path = Path.home() / "Documents/data" / ac_number / disk_archive_id
    transfer_folder = project_base_path / f"3_{disk_archive_id}_for-transfer"

    paths = {
        "input_folder": transfer_folder / "files",
        "logfile_path": transfer_folder / f"3_{disk_archive_id}_for-transfer_image-conversion.log"
    }

    if not paths["input_folder"].is_dir():
        print(f"\033[91mFehler: Der Eingabe-Ordner wurde nicht gefunden:\n{paths['input_folder']}\033[0m")
        return None
        
    if not paths["logfile_path"].parent.is_dir():
        print(f"\033[91mFehler: Der Ordner für die Log-Datei existiert nicht:\n{paths['logfile_path'].parent}\033[0m")
        return None

    tools_to_check = {
        "ImageMagick": IMAGEMAGICK_PATH,
        "Inkscape": INKSCAPE_PATH,
        "Ghostscript": GHOSTSCRIPT_PATH
    }
    for tool_name, tool_path in tools_to_check.items():
        if not shutil.which(tool_path):
            print(f"\033[91mFehler: '{tool_path}' ({tool_name}) wurde nicht gefunden.\033[0m")
            print("\033[93mStellen Sie sicher, dass das Programm installiert und zum System-PATH hinzugefügt wurde, oder geben Sie den vollen Pfad in der Konfiguration an.\033[0m")
            return None

    print("\033[92mAlle Pfade und Programme wurden erfolgreich gefunden und validiert.\033[0m")
    return paths

# ==============================================================================
# --- HAUPT-AUSFÜHRUNGSBLOCK ---
# ==============================================================================
if __name__ == "__main__":
    # NEU: Liest die Werte von der Kommandozeile
    try:
        ac_number_input = sys.argv[1]
        disk_archive_id_input = sys.argv[2]
        print(f"Werte aus der Kommandozeile erhalten: AC={ac_number_input}, ID={disk_archive_id_input}")
    except IndexError:
        print("FEHLER: AC-Nummer und Datenträger-ID wurden nicht übergeben.")
        print("Dieses Skript sollte über 'start.bat' gestartet werden.")
        sys.exit(1)

    validated_paths = setup_and_validate_paths(ac_number_input, disk_archive_id_input)

    if validated_paths:
        input_folder = validated_paths["input_folder"]
        logfile_path = validated_paths["logfile_path"]

        print("\nSkript wird mit folgenden Pfaden ausgeführt:")
        print(f"- Eingabe-Ordner: {input_folder}")
        print(f"- Log-Datei: {logfile_path}\n")

        converted_count = 0
        error_count = 0
        log_lines = []
        all_files = []

        print("Suche nach zu verarbeitenden Quelldateien...")
        valid_source_extensions = RASTER_EXTENSIONS.union(VECTOR_EXTENSIONS).union(GHOSTSCRIPT_FORMATS)

        for root, _, files in os.walk(input_folder):
            for filename in files:
                if filename.startswith('.') or filename.startswith('~'):
                    continue

                parts = os.path.splitext(filename.lower())[0].split('.')
                if len(parts) >= 2:
                    original_ext = f".{parts[-1]}"
                    current_ext = os.path.splitext(filename)[1].lower()
                    if original_ext in valid_source_extensions and (current_ext == RASTER_TARGET_EXT or current_ext == VECTOR_TARGET_EXT):
                        continue
                
                ext = os.path.splitext(filename)[1].lower()
                if ext in valid_source_extensions:
                    all_files.append(os.path.join(root, filename))

        total = len(all_files)
        print(f"{total} relevante Grafikdateien im angegebenen Ordner gefunden.")
        
        if total > 0:
            print("\nStarte universelle Grafik-Konvertierung...")

            for idx, abs_path in enumerate(all_files, 1):
                rel_path = os.path.relpath(abs_path, input_folder)
                root, filename = os.path.split(abs_path)
                base, ext = os.path.splitext(filename)
                ext = ext.lower()

                percent = (idx / total) * 100
                print(f"[{idx}/{total}] {percent:6.2f}% → {rel_path}")
                log_lines.append(f"\n--- Verarbeite: {filename} ---")
                
                if ext in RASTER_EXTENSIONS:
                    tool_name = "ImageMagick"
                    target_ext = RASTER_TARGET_EXT
                    output_filename = f"{base}{ext}{target_ext}"
                    output_path = os.path.join(root, output_filename)
                    cmd = [IMAGEMAGICK_PATH, "-quiet", abs_path, output_path]

                elif ext in GHOSTSCRIPT_FORMATS:
                    tool_name = "Ghostscript"
                    target_ext = VECTOR_TARGET_EXT
                    output_filename = f"{base}{ext}{target_ext}"
                    output_path = os.path.join(root, output_filename)
                    cmd = [GHOSTSCRIPT_PATH, "-sDEVICE=pdfwrite", "-dBATCH", "-dNOPAUSE", f"-sOutputFile={output_path}", abs_path]

                elif ext in VECTOR_EXTENSIONS:
                    tool_name = "Inkscape"
                    target_ext = VECTOR_TARGET_EXT
                    output_filename = f"{base}{ext}{target_ext}"
                    output_path = os.path.join(root, output_filename)
                    cmd = [INKSCAPE_PATH, abs_path, f"--export-filename={output_path}", "--export-text-to-path", "--export-pdf-version=1.5"]
                
                else:
                    log_lines.append(f"[INFO] Unbekannter Dateityp '{ext}', wird übersprungen.")
                    continue

                if os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                        log_lines.append(f"[INFO] Alte Zieldatei wird überschrieben: {output_filename}")
                    except OSError as e:
                        log_lines.append(f"[FEHLER] Alte Zieldatei konnte nicht gelöscht werden: {output_filename} ({e})")
                        error_count += 1
                        continue

                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
                    
                    if result.returncode == 0 and os.path.exists(output_path):
                        converted_count += 1
                        log_lines.append(f"[OK] Konvertiert mit {tool_name}: {filename} → {output_filename}")
                    else:
                        error_count += 1
                        log_lines.append(f"[FEHLER] {tool_name} hat KEINE Zieldatei erstellt für: {filename}")
                        if result.stderr:
                            log_lines.append(f"       Fehlermeldung: {result.stderr.strip()}")

                except FileNotFoundError:
                    error_count += 1
                    log_lines.append(f"[KRITISCHER FEHLER] Befehl '{cmd[0]}' nicht gefunden.")
                except Exception as e:
                    error_count += 1
                    log_lines.append(f"[FEHLER] Ein unerwartetes Problem ist aufgetreten bei: {filename} ({e})")

            with open(logfile_path, "w", encoding="utf-8") as log_file:
                log_file.write(f"LOG VOM {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                log_file.write("--- ZUSAMMENFASSUNG ---\n")
                log_file.write(f"Verarbeitete Dateien insgesamt: {total}\n")
                log_file.write(f"Erfolgreich konvertiert: {converted_count}\n")
                log_file.write(f"Fehler bei Konvertierung: {error_count}\n")
                log_file.write("\n--- DETAILLIERTES PROTOKOLL ---\n")
                log_file.write("".join(log_lines))

            print(f"\nFertig. {converted_count} Dateien konvertiert, {error_count} Fehler.")
            print(f"Log gespeichert unter: {logfile_path}")

        # --- ANFANG: HINZUGEFÜGTER CODE-BLOCK ---
        # Der Zielordner ist der übergeordnete Ordner des Eingabeordners (also der "for-transfer"-Ordner)
        destination_folder = validated_paths["input_folder"].parent
        
        # --- Zielordner optional öffnen ---
        print("")
        open_folder = input("Zielordner oeffnen? (j/n): ").lower()
        if open_folder == 'j':
            if sys.platform == "win32":
                os.startfile(destination_folder)
            elif sys.platform == "darwin":
                subprocess.run(["open", destination_folder])
            else:
                subprocess.run(["xdg-open", destination_folder])
            # Angepasst an den Stil des bestehenden Skripts
            print("\033[92mZielordner geoeffnet\033[0m")
        # --- ENDE: HINZUGEFÜGTER CODE-BLOCK ---

    else:
        print("\nSkript wird aufgrund von Konfigurationsfehlern beendet.")

    print("\nSkript beendet.")