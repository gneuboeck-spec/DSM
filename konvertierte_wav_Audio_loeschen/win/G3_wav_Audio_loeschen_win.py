# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# --- KONFIGURATION ---

# Diese Liste muss mit der `source_audio_extensions`-Liste aus Ihrem Konverter übereinstimmen.
source_audio_extensions = {".aiff", ".flac", ".ogg", ".wav", ".m4a", ".wma", ".aac", ".mp3"}

# --- Pfad- und Log-Konfiguration ---
def setup_and_validate_paths(ac_number, disk_archive_id):
    """
    Erstellt und validiert die Projekt-Pfade für das WAV-Aufräumskript.
    """
    project_base_path = Path.home() / "Documents/data" / ac_number / disk_archive_id
    transfer_folder_base = project_base_path / f"3_{disk_archive_id}_for-transfer"
    
    paths = {
        "target_folder": transfer_folder_base / "files",
        "log_filepath": transfer_folder_base / f"3_{disk_archive_id}_for-transfer_delete-converted-wavs.log"
    }

    # Validierung
    if not paths["target_folder"].is_dir():
        print(f"\033[91mFehler: Der Ziel-Ordner wurde nicht gefunden:\n{paths['target_folder']}\033[0m")
        return None

    print("\033[92mAlle Pfade wurden erfolgreich gefunden und validiert.\033[0m")
    return paths
# --- ENDE DER KONFIGURATION ---


def find_and_delete_intermediate_wavs(folder, log_filepath):
    """
    Durchsucht den Ordner, löscht konvertierte WAV-Dateien und protokolliert den Vorgang.
    """
    print(f"Starte Suche nach konvertierten WAV-Dateien im Ordner: {folder}\n")
    
    files_to_delete = []
    
    # ***** HIER IST DIE KORREKTUR *****
    all_found_files = set(os.path.join(root, name) for root, _, files in os.walk(folder) for name in files)

    for filepath in all_found_files:
        path, filename = os.path.split(filepath)
        if filename.startswith('.') or filename.startswith('~'):
            continue
        if filename.lower().endswith('.wav'):
            parts = filename.split('.')
            if len(parts) >= 3:
                original_ext = f".{parts[-2].lower()}"
                if original_ext in source_audio_extensions:
                    original_filepath = os.path.join(path, ".".join(parts[:-1]))
                    if original_filepath in all_found_files:
                        files_to_delete.append(filepath)

    if not files_to_delete:
        print("Keine konvertierten WAV-Dateien zum Löschen gefunden.")
        return

    print("Die folgenden, durch Konvertierung erstellten WAV-Dateien werden gelöscht:")
    for f in sorted(files_to_delete):
        print(f"  - {os.path.basename(f)}")
    
    confirm = input("\nMöchten Sie diese Dateien wirklich löschen? (j/n): ").lower()
    if confirm != 'j':
        print("Löschvorgang abgebrochen.")
        return

    successful_deletions = []
    failed_deletions = []
    
    print() 
    for f in files_to_delete:
        try:
            os.remove(f)
            print(f"Gelöscht: {os.path.basename(f)}")
            successful_deletions.append(f)
        except Exception as e:
            error_msg = str(e)
            print(f"FEHLER beim Löschen von {os.path.basename(f)}: {error_msg}")
            failed_deletions.append((f, error_msg))
            
    try:
        with open(log_filepath, "w", encoding="utf-8") as logfile:
            logfile.write("# Protokoll des Aufräumvorgangs (konvertierte WAV-Dateien)\n")
            logfile.write(f"# Erstellt am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            logfile.write("=" * 60 + "\n\n")
            logfile.write(f"--- ERFOLGREICH GELÖSCHT ({len(successful_deletions)}) ---\n")
            for path in sorted(successful_deletions):
                logfile.write(f"{path}\n")
            
            logfile.write(f"\n--- FEHLER BEIM LÖSCHEN ({len(failed_deletions)}) ---\n")
            if failed_deletions:
                for path, error in sorted(failed_deletions):
                    logfile.write(f"Datei: {path}\nFehler: {error}\n\n")
            else:
                logfile.write("Keine Fehler aufgetreten.\n")
        print(f"\n[OK] Log-Datei wurde erfolgreich erstellt: {log_filepath}")
    except Exception as e:
        print(f"\n[FEHLER] Die Log-Datei konnte nicht geschrieben werden: {e}")
            
    print(f"\nAufräumen abgeschlossen. {len(successful_deletions)} von {len(files_to_delete)} WAV-Dateien gelöscht.")


# --- HAUPTBLOCK ---
if __name__ == "__main__":
    try:
        ac_number_input = sys.argv[1]
        disk_archive_id_input = sys.argv[2]
        print(f"Werte aus der Kommandozeile erhalten: AC={ac_number_input}, ID={disk_archive_id_input}")
    except IndexError:
        print("FEHLER: AC-Nummer und Datenträger-ID wurden nicht übergeben.")
        print("Dieses Skript sollte über die 'start.bat'-Datei und das Menü gestartet werden.")
        print("\nBitte geben Sie die Daten manuell ein:")
        ac_number_input = input("AC-Nummer eingeben: ")
        disk_archive_id_input = input("Datenträger-ID eingeben: ")

    validated_paths = setup_and_validate_paths(ac_number_input, disk_archive_id_input)

    if validated_paths:
        target_folder = validated_paths["target_folder"]
        log_filepath = validated_paths["log_filepath"]
        
        print(f"\nSkript wird mit folgenden Pfaden ausgeführt:")
        print(f"- Ziel-Ordner: {target_folder}")
        print(f"- Log-Datei:  {log_filepath}\n")
        
        if os.path.exists(log_filepath):
            os.remove(log_filepath)

        find_and_delete_intermediate_wavs(folder=target_folder, log_filepath=log_filepath)

        destination_folder = validated_paths["target_folder"].parent
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