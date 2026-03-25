# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT


import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# ==============================================================================
# 🔧 KONFIGURATION
# ==============================================================================

DRY_RUN = False

original_extensions = {
    ".doc", ".docx", ".rtf", ".wpd", ".wps", ".dot", ".dotx", ".wbk" 
}

# ==============================================================================
# --- PFAD-VALIDIERUNG ---
# ==============================================================================

def setup_and_validate_paths(ac_number, disk_archive_id):
    project_base_path = Path.home() / "Documents/data" / ac_number / disk_archive_id
    transfer_folder = project_base_path / f"3_{disk_archive_id}_for-transfer"

    paths = {
        "target_folder": transfer_folder / "files",
        "log_filepath": transfer_folder / f"3_{disk_archive_id}_for-transfer_delete-converted-odfs.log"
    }

    if not paths["target_folder"].is_dir():
        print(f"\033[91mFehler: Der Ziel-Ordner wurde nicht gefunden:\n{paths['target_folder']}\033[0m")
        return None
        
    if not paths["log_filepath"].parent.is_dir():
        print(f"\033[91mFehler: Der Ordner für die Log-Datei existiert nicht:\n{paths['log_filepath'].parent}\033[0m")
        return None

    print("\033[92mAlle Pfade wurden erfolgreich gefunden und validiert.\033[0m")
    return paths

# ==============================================================================
# --- SKRIPT-LOGIK ---
# ==============================================================================

def manage_intermediate_files(folder, log_filepath, is_dry_run):
    if is_dry_run:
        print("=== TESTLAUF AKTIV (KEINE DATEIEN WERDEN GELÖSCHT) ===")
    else:
        print("=== ECHTER LÖSCHVORGANG AKTIV ===")
        
    print(f"Starte Suche nach Zwischendateien im Ordner: {folder}\n")
    
    files_to_process = []
    
    # --- ANFANG DER KORREKTUR ---
    # Wir verwenden pathlib für eine robustere Pfad-Analyse.
    for file in Path(folder).rglob('*.odt'):
        # Beispiel: file = "C:/.../hitler OXFORD1.doc.odt"
        # file.stem ergibt "hitler OXFORD1.doc"
        file_name_stem = file.stem

        # Prüfen, ob der Dateiname (ohne .odt) auf eine der Original-Endungen endet
        if any(file_name_stem.lower().endswith(ext) for ext in original_extensions):
            # Der `stem` der .odt-Datei ist bereits der Name der Quelldatei.
            # Wir müssen ihn nur noch im selben Verzeichnis suchen.
            source_file = file.parent / file_name_stem

            # Füge die .odt-Datei zur Löschliste hinzu, wenn die Quelldatei existiert
            if source_file.exists():
                files_to_process.append(str(file)) # Konvertiere zurück zu String für Konsistenz
    # --- ENDE DER KORREKTUR ---

    if not files_to_process:
        print("Keine Zwischendateien zum Verarbeiten gefunden.")
        return

    if is_dry_run:
        print(f"{len(files_to_process)} potenzielle Zwischendateien gefunden.")
        print(f"Schreibe eine Liste der Dateien in die Log-Datei: {log_filepath}")

        try:
            with open(log_filepath, "w", encoding="utf-8") as logfile:
                logfile.write("# Protokoll des TESTLAUFS (keine Dateien wurden gelöscht)\n")
                logfile.write(f"# Erstellt am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                logfile.write(f"# Durchsuchter Ordner: {folder}\n")
                logfile.write("=" * 50 + "\n\n")
                logfile.write(f"--- DATEIEN, DIE GELÖSCHT WÜRDEN ({len(files_to_process)}) ---\n")
                for path in sorted(files_to_process):
                    logfile.write(f"{path}\n")
            print("\n[OK] Testlauf-Log wurde erfolgreich erstellt.")
        except Exception as e:
            print(f"\n[FEHLER] Die Log-Datei konnte nicht geschrieben werden: {e}")

    else:
        print("Die folgenden Zwischendateien wurden zur Löschung identifiziert:")
        for f in sorted(files_to_process):
            print(f"  - {f}")
        
        confirm = input("\nMöchten Sie diese Dateien wirklich löschen? (j/n): ").lower()
        if confirm != 'j':
            print("Löschvorgang abgebrochen.")
            return

        print(f"\nStarte Löschvorgang und erstelle Log-Datei: {log_filepath}")
        successful_deletions = []
        failed_deletions = []

        for f_path in files_to_process:
            try:
                os.remove(f_path)
                successful_deletions.append(f_path)
                print(f"GELÖSCHT: {os.path.basename(f_path)}")
            except Exception as e:
                failed_deletions.append((f_path, str(e)))
                print(f"FEHLER bei '{os.path.basename(f_path)}': {e}")
        
        try:
            with open(log_filepath, "w", encoding="utf-8") as logfile:
                logfile.write("# Protokoll des Aufräumvorgangs\n")
                logfile.write(f"# Erstellt am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                logfile.write("=" * 50 + "\n\n")
                logfile.write(f"--- ERFOLGREICH GELÖSCHT ({len(successful_deletions)}) ---\n")
                for path in sorted(successful_deletions): logfile.write(f"{path}\n")
                logfile.write(f"\n--- FEHLER BEIM LÖSCHEN ({len(failed_deletions)}) ---\n")
                if failed_deletions:
                    for path, error in sorted(failed_deletions): logfile.write(f"Datei: {path}\nFehler: {error}\n\n")
                else:
                    logfile.write("Keine Fehler aufgetreten.\n")
            print(f"\n[OK] Log-Datei wurde erfolgreich erstellt.")
        except Exception as e:
            print(f"\n[FEHLER] Die Log-Datei konnte nicht geschrieben werden: {e}")
            
        print(f"\nAufräumen abgeschlossen. {len(successful_deletions)} gelöscht, {len(failed_deletions)} fehlgeschlagen.")

# ==============================================================================
# --- HAUPT-AUSFÜHRUNGSBLOCK ---
# ==============================================================================
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
        output_log_filepath = validated_paths["log_filepath"]
        
        print("\nSkript wird mit folgenden Pfaden ausgeführt:")
        print(f"- Ziel-Ordner: {target_folder}")
        print(f"- Log-Datei: {output_log_filepath}\n")

        manage_intermediate_files(target_folder, output_log_filepath, DRY_RUN)

        destination_folder = validated_paths["target_folder"].parent
        
        print("")
        open_folder = input("Zielordner oeffnen? (j/n): ").lower()
        if open_folder == 'j':
            if sys.platform == "win32":
                os.startfile(str(destination_folder))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(destination_folder)])
            else:
                subprocess.run(["xdg-open", str(destination_folder)])
            print("\033[92mZielordner geoeffnet\033[0m")

    else:
        print("\nSkript wird aufgrund von Konfigurationsfehlern beendet.")

    print("\nSkript beendet.")
    input("Drücken Sie Enter, um das Fenster zu schließen.")