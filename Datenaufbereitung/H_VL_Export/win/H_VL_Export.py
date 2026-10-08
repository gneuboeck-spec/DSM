# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import sys
import re
import shutil
import subprocess
from pathlib import Path

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    print("Fehler: Das benötigte Paket 'colorama' ist nicht installiert.")
    print("Bitte installieren Sie es: pip install colorama")
    class Fore:
        GREEN = RED = YELLOW = CYAN = MAGENTA = WHITE = ""
    class Style:
        RESET_ALL = ""

# ==============================================================================
# 🔧 SKRIPT-LOGIK
# ==============================================================================

def main():
    """Führt den gesamten Kopiervorgang für den VL-Export durch."""

    # <<< HIER IST DIE ANPASSUNG >>>
    # Anstatt selbst zu fragen, werden die Werte von der Kommandozeile gelesen,
    # die vom menu.py-Skript übergeben werden.
    try:
        ac_number = sys.argv[1]
        disk_archive_id = sys.argv[2]
        print(f"Werte aus der Kommandozeile erhalten: AC={ac_number}, ID={disk_archive_id}")
        
        # NEU: Datenpfad aus menu.py übernehmen (sys.argv[3] oder Umgebungsvariable DATA_PATH)
        if len(sys.argv) >= 4:
            data_path_input = Path(sys.argv[3])
        else:
            env_path = os.environ.get("DATA_PATH")
            if env_path:
                data_path_input = Path(env_path)
            else:
                data_path_input = Path.home() / "Documents" / "data" / ac_number / disk_archive_id
                
    except IndexError:
        print(Fore.RED + "FEHLER: AC-Nummer und Datenträger-ID wurden nicht übergeben.")
        print(Fore.YELLOW + "Dieses Skript sollte über die 'start.bat'-Datei und das Menü gestartet werden.")
        # Fallback auf manuelle Eingabe, wenn es direkt gestartet wird
        print("\nBitte geben Sie die Daten manuell ein:")
        ac_number = input("AC-Nummer eingeben: ")
        disk_archive_id = input("Datenträger-ID eingeben: ")
        data_path_input = Path.home() / "Documents" / "data" / ac_number / disk_archive_id

    print("")
    print(Fore.MAGENTA + "========================================")
    print(Fore.CYAN + "  DATEIEN FUER VL-EXPORT KOPIEREN")
    print(Fore.MAGENTA + "========================================")
    print("")

    # --- Pfade definieren ---
    print("\n" + Fore.CYAN + "Pfade definieren")
    
    # NEU: Der übergebene Datenpfad IST der MainFolder (der ID-Ordner)
    main_folder = data_path_input
    base_path = main_folder.parent
    destination_folder = main_folder / f"4_{disk_archive_id}_VL"
    
    print(Fore.WHITE + f"  BasePath: {base_path}")
    print(Fore.WHITE + f"  MainFolder: {main_folder}")
    print(Fore.WHITE + f"  DestinationFolder: {destination_folder}")

    # --- Pfadvalidierung ---
    print("\n" + Fore.CYAN + "Pfade validieren")
    if not base_path.is_dir():
        print(Fore.RED + f"FEHLER: BasePath existiert nicht: {base_path}"); sys.exit(1)
    if not main_folder.is_dir():
        print(Fore.RED + f"FEHLER: MainFolder existiert nicht: {main_folder}"); sys.exit(1)
    if not destination_folder.is_dir():
        print(Fore.RED + f"FEHLER: Zielordner existiert nicht: {destination_folder}"); sys.exit(1)
    
    print(Fore.GREEN + "Alle Pfade vorhanden")
    
    # --- Quelldateien und -ordner definieren ---
    source_picture_carrier = main_folder / f"0_{disk_archive_id}_picture-carrier"
    source_extracted_files = main_folder / f"2_{disk_archive_id}_extracted-files"
    source_for_transfer = main_folder / f"3_{disk_archive_id}_for-transfer"

    print("\n" + Fore.CYAN + "Kopiervorgang starten")

    # --- 1. TIF-Dateien kopieren ---
    print("\n" + Fore.CYAN + "1. TIF-Dateien kopieren")
    if source_picture_carrier.is_dir():
        tif_files = list(source_picture_carrier.glob("*.tif"))
        if tif_files:
            for tif_file in tif_files:
                dest_file = destination_folder / tif_file.name
                if dest_file.exists():
                    print(Fore.YELLOW + f"  WARNUNG: Datei existiert bereits: {tif_file.name}")
                else:
                    shutil.copy2(tif_file, dest_file)
                    print(Fore.GREEN + f"  Kopiert: {tif_file.name}")
        else:
            print(Fore.YELLOW + f"  WARNUNG: Keine TIF-Dateien gefunden in {source_picture_carrier}")
    else:
        print(Fore.YELLOW + f"  WARNUNG: Ordner nicht gefunden: {source_picture_carrier}")

    # --- 2. content-Datei kopieren ---
    print("\n" + Fore.CYAN + "2. content-Datei kopieren")
    content_file = source_extracted_files / f"2_{disk_archive_id}_extracted-files.content"
    if content_file.is_file():
        dest_file = destination_folder / content_file.name
        if dest_file.exists():
            print(Fore.YELLOW + f"  WARNUNG: Datei existiert bereits: {content_file.name}")
        else:
            shutil.copy2(content_file, dest_file)
            print(Fore.GREEN + f"  Kopiert: {content_file.name}")
    else:
        print(Fore.YELLOW + f"  WARNUNG: Datei nicht gefunden: {content_file}")

    # --- 3. Tree-Datei aus extrahierten Dateien kopieren ---
    print("\n" + Fore.CYAN + "3. Tree-Datei aus extrahierten Dateien kopieren")
    tree_file_extracted = source_extracted_files / f"2_{disk_archive_id}_extracted-files_tree.txt"
    if tree_file_extracted.is_file():
        dest_file = destination_folder / tree_file_extracted.name
        if dest_file.exists():
            print(Fore.YELLOW + f"  WARNUNG: Datei existiert bereits: {tree_file_extracted.name}")
        else:
            shutil.copy2(tree_file_extracted, dest_file)
            print(Fore.GREEN + f"  Kopiert: {tree_file_extracted.name}")
    else:
        print(Fore.YELLOW + f"  WARNUNG: Datei nicht gefunden: {tree_file_extracted}")

    # --- 4. Tree-Datei aus For-Transfer-Ordner kopieren ---
    print("\n" + Fore.CYAN + "4. Tree-Datei aus For-Transfer-Ordner kopieren")
    transfer_tree_filename = f"3_{disk_archive_id}_for-transfer_tree.txt"
    tree_file_for_transfer = source_for_transfer / transfer_tree_filename
    if tree_file_for_transfer.is_file():
        dest_file = destination_folder / tree_file_for_transfer.name
        if dest_file.exists():
            print(Fore.YELLOW + f"  WARNUNG: Datei existiert bereits: {tree_file_for_transfer.name}")
        else:
            shutil.copy2(tree_file_for_transfer, dest_file)
            print(Fore.GREEN + f"  Kopiert: {tree_file_for_transfer.name}")
    else:
        print(Fore.YELLOW + f"  WARNUNG: Datei nicht gefunden: {tree_file_for_transfer}")

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
        print(Fore.GREEN + "Zielordner geoeffnet")

    # --- Abschluss ---
    print("")
    print(Fore.MAGENTA + "========================================")
    print(Fore.GREEN + "  KOPIERVORGANG ABGESCHLOSSEN")
    print(Fore.MAGENTA + "========================================")
    print("")

if __name__ == "__main__":
    main()