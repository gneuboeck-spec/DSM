# SPDX-FileCopyrightText: 2025 Florian Lüftner <florian.lueftner@posteo.com>
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

DELETE_ODF_DRY_RUN = False

original_extensions = {
    ".doc", ".docx", ".rtf", ".wpd", ".wps", ".dot", ".dotx", ".wbk" 
}

SOURCE_AUDIO_EXTENSIONS_FOR_WAV_CLEANUP = {".aiff", ".flac", ".ogg", ".wav", ".m4a", ".wma", ".aac", ".mp3"}


# ==============================================================================
# --- PFAD-VALIDIERUNG ---
# ==============================================================================

def setup_and_validate_paths(ac_number, disk_archive_id):
    # Basis-Pfad des Projekts
    project_base_path = Path.home() / "Documents/data" / ac_number / disk_archive_id
    
    # Definition der Haupt-Ordner
    VL_folder = project_base_path / f"4_{disk_archive_id}_VL"
    LZA_folder = project_base_path / f"5_{disk_archive_id}_LZA"
    log_dir = LZA_folder / "logfiles"

    # WICHTIG: Den Log-Ordner in Stufe 5 erstellen, falls er noch nicht da ist
    if not log_dir.exists():
        log_dir.mkdir(parents=True, exist_ok=True)
    
    paths = {
        # Wo gelöscht wird (Stufe 4)
        "target_folder": VL_folder / "files",
        
        # Wo dokumentiert wird (Stufe 5 / logfiles)
        "log_filepath_odf": log_dir / f"4_{disk_archive_id}_VL_delete-converted-odfs.log",
        "log_filepath_wav": log_dir / f"4_{disk_archive_id}_VL_delete-converted-wavs.log",
    }

    # Validierung des Arbeitsverzeichnisses
    if not paths["target_folder"].is_dir():
        print(f"\033[91mFehler: Der Ziel-Ordner (VL) wurde nicht gefunden:\n{paths['target_folder']}\033[0m")
        return None
    
    print("\033[92mAlle Pfade wurden erfolgreich gefunden und validiert.\033[0m")
    return paths

# ==============================================================================
# --- LOGIK FÜR "ZWISCHENDATEIEN (ODF) LÖSCHEN" ---
# ==============================================================================

def manage_intermediate_files(folder, log_filepath, is_dry_run):
    if is_dry_run:
        print("=== TESTLAUF AKTIV (KEINE DATEIEN WERDEN GELÖSCHT) ===")
    else:
        print("=== ECHTER LÖSCHVORGANG AKTIV ===")
        
    print(f"Starte Suche nach ODF-Zwischendateien im Ordner: {folder}\n")
    
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
        print("Keine ODF-Zwischendateien zum Verarbeiten gefunden.")
        return

    if is_dry_run:
        print(f"{len(files_to_process)} potenzielle ODF-Zwischendateien gefunden.")
        try:
            with open(log_filepath, "w", encoding="utf-8") as logfile:
                logfile.write("# Protokoll des TESTLAUFS (keine ODF-Dateien wurden gelöscht)\n" + f"# Erstellt am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" + "="*50 + "\n\n")
                logfile.write(f"--- DATEIEN, DIE GELÖSCHT WÜRDEN ({len(files_to_process)}) ---\n")
                for path in sorted(files_to_process): logfile.write(f"{path}\n")
            print("\n[OK] Testlauf-Log wurde erfolgreich erstellt.")
        except Exception as e: print(f"\n[FEHLER] Die Log-Datei konnte nicht geschrieben werden: {e}")
    else:
        print("Die folgenden ODF-Zwischendateien wurden zur Löschung identifiziert:")
        for f in sorted(files_to_process): print(f"  - {f}")
        
        confirm = input("\nMöchten Sie diese Dateien wirklich löschen? (j/n): ").lower()
        if confirm != 'j': print("Löschvorgang abgebrochen."); return

        print(f"\nStarte Löschvorgang und erstelle Log-Datei: {log_filepath}")
        successful_deletions, failed_deletions = [], []
        for f_path in files_to_process:
            try:
                # Nutze Path(f_path).unlink() statt os.remove für bessere Pfadbehandlung
                Path(f_path).unlink() 
                successful_deletions.append(f_path)
                print(f"GELÖSCHT: {os.path.basename(f_path)}")
            except Exception as e:
                failed_deletions.append((f_path, str(e)))
                print(f"FEHLER bei '{os.path.basename(f_path)}': {e}")
        
        try:
            with open(log_filepath, "w", encoding="utf-8") as logfile:
                logfile.write("# Protokoll des Aufräumvorgangs (ODF)\n" + f"# Erstellt am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" + "="*50 + "\n\n")
                logfile.write(f"--- ERFOLGREICH GELÖSCHT ({len(successful_deletions)}) ---\n")
                for path in sorted(successful_deletions): logfile.write(f"{path}\n")
                logfile.write(f"\n--- FEHLER BEIM LÖSCHEN ({len(failed_deletions)}) ---\n")
                if failed_deletions:
                    for path, error in sorted(failed_deletions): logfile.write(f"Datei: {path}\nFehler: {error}\n\n")
                else: logfile.write("Keine Fehler aufgetreten.\n")
            print(f"\n[OK] Log-Datei wurde erfolgreich erstellt.")
        except Exception as e: print(f"\n[FEHLER] Die Log-Datei konnte nicht geschrieben werden: {e}")
        print(f"\nAufräumen abgeschlossen. {len(successful_deletions)} gelöscht, {len(failed_deletions)} fehlgeschlagen.")

# ==============================================================================
# --- LOGIK FÜR "KONVERTIERTE WAVs LÖSCHEN" ---
# ==============================================================================

def find_and_delete_intermediate_wavs(folder, log_filepath):
    print(f"Starte Suche nach konvertierten WAV-Dateien im Ordner: {folder}\n")
    
    files_to_delete = []
    all_found_files = set(os.path.join(root, name) for root, _, files in os.walk(folder) for name in files)

    for filepath in all_found_files:
        path, filename = os.path.split(filepath)
        if filename.startswith('.') or filename.startswith('~'): continue
        if filename.lower().endswith('.wav'):
            parts = filename.split('.')
            if len(parts) >= 3:
                original_ext = f".{parts[-2].lower()}"
                if original_ext in SOURCE_AUDIO_EXTENSIONS_FOR_WAV_CLEANUP:
                    original_filepath = os.path.join(path, ".".join(parts[:-1]))
                    if original_filepath in all_found_files:
                        files_to_delete.append(filepath)

    if not files_to_delete:
        print("Keine konvertierten WAV-Dateien zum Löschen gefunden.")
        return

    print("Die folgenden, durch Konvertierung erstellten WAV-Dateien werden gelöscht:")
    for f in files_to_delete: print(f"  - {os.path.basename(f)}")
    
    confirm = input("\nMöchten Sie diese Dateien wirklich löschen? (j/n): ").lower()
    if confirm != 'j': print("Löschvorgang abgebrochen."); return

    deleted_count, failed_deletions = 0, []
    print() 
    for f in files_to_delete:
        try:
            os.remove(f); print(f"Gelöscht: {os.path.basename(f)}"); deleted_count += 1
        except Exception as e:
            failed_deletions.append((f, str(e))); print(f"FEHLER beim Löschen von {os.path.basename(f)}: {e}")
            
    try:
        with open(log_filepath, "w", encoding="utf-8") as logfile:
            logfile.write("# Protokoll des Aufräumvorgangs (WAV)\n" + f"# Erstellt am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" + "=" * 50 + "\n\n")
            logfile.write(f"--- ERFOLGREICH GELÖSCHT ({deleted_count}) ---\n")
            successful_deletions = [f for f in files_to_delete if (f, '') not in [(fail[0], '') for fail in failed_deletions]]
            for path in sorted(successful_deletions): logfile.write(f"{path}\n")
            logfile.write(f"\n--- FEHLER BEIM LÖSCHEN ({len(failed_deletions)}) ---\n")
            if failed_deletions:
                for path, error in sorted(failed_deletions): logfile.write(f"Datei: {path}\nFehler: {error}\n\n")
            else: logfile.write("Keine Fehler aufgetreten.\n")
        print(f"\n[OK] Log-Datei wurde erfolgreich erstellt: {log_filepath}")
    except Exception as e: print(f"\n[FEHLER] Die Log-Datei konnte nicht geschrieben werden: {e}")
            
    print(f"\nAufräumen abgeschlossen. {deleted_count} von {len(files_to_delete)} WAV-Dateien gelöscht.")

# ==============================================================================
# --- HAUPT-AUSFÜHRUNGSBLOCK ---
# ==============================================================================
if __name__ == "__main__":
    try:
        ac_number_input, disk_archive_id_input = sys.argv[1], sys.argv[2]
        print(f"Werte aus der Kommandozeile erhalten: AC={ac_number_input}, ID={disk_archive_id_input}")
    except IndexError:
        print("FEHLER: AC-Nummer und Datenträger-ID wurden nicht übergeben."); sys.exit(1)

    validated_paths = setup_and_validate_paths(ac_number_input, disk_archive_id_input)

    if validated_paths:
        while True:
            print("\n========================================")
            print("  Wählen Sie eine Aufräum-Aktion:")
            print("========================================")
            print("  1 - Zwischendateien (ODF) löschen")
            print("  2 - Konvertierte WAV-Dateien löschen")
            print("  Q - Beenden")
            print("========================================")
            choice = input("Ihre Wahl: ").strip().lower()

            if choice == '1':
                print("\n--- Aktion: Zwischendateien (ODF) löschen ---")
                manage_intermediate_files(
                    folder=validated_paths["target_folder"],
                    log_filepath=validated_paths["log_filepath_odf"],
                    is_dry_run=DELETE_ODF_DRY_RUN
                )
                input("\nAktion beendet. Drücken Sie Enter, um zum Menü zurückzukehren.")
            
            elif choice == '2':
                print("\n--- Aktion: Konvertierte WAV-Dateien löschen ---")
                find_and_delete_intermediate_wavs(
                    folder=validated_paths["target_folder"],
                    log_filepath=validated_paths["log_filepath_wav"]
                )
                input("\nAktion beendet. Drücken Sie Enter, um zum Menü zurückzukehren.")
            
            elif choice == 'q':
                break
            else:
                print("\nUngültige Auswahl. Bitte erneut versuchen.")

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