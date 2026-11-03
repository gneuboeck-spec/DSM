# SPDX-FileCopyrightText: 2025 Florian Lüftner <florian.lueftner@posteo.com>
#
# SPDX-License-Identifier: MIT

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class Fore: GREEN = RED = YELLOW = CYAN = MAGENTA = WHITE = ""
    class Style: RESET_ALL = ""

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

def setup_and_validate_paths(ac_number, disk_archive_id, project_base_path_override=None):
    # NEU: Wenn ein Pfad aus dem Menü übergeben wurde, nutzen wir diesen.
    # Andernfalls greift der alte Fallback-Pfad.
    if project_base_path_override:
        project_base_path = Path(project_base_path_override)
    else:
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
        print(f"{Fore.RED}Fehler: Der Ziel-Ordner (VL) wurde nicht gefunden:\n{paths['target_folder']}{Style.RESET_ALL}")
        return None
    
    print(f"{Fore.GREEN}Alle Pfade wurden erfolgreich gefunden und validiert.{Style.RESET_ALL}")
    return paths

# ==============================================================================
# --- LOGIK FÜR "ZWISCHENDATEIEN (ODF) LÖSCHEN" ---
# ==============================================================================

def manage_intermediate_files(folder, log_filepath, is_dry_run):
    if is_dry_run:
        print("=== TESTLAUF AKTIV (KEINE ODF-DATEIEN WERDEN GELÖSCHT) ===")
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
        return 0

    if is_dry_run:
        print(f"{len(files_to_process)} potenzielle ODF-Zwischendateien gefunden.")
        try:
            with open(log_filepath, "w", encoding="utf-8") as logfile:
                logfile.write("# Protokoll des TESTLAUFS (keine ODF-Dateien wurden gelöscht)\n" + f"# Erstellt am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" + "="*50 + "\n\n")
                logfile.write(f"--- DATEIEN, DIE GELÖSCHT WÜRDEN ({len(files_to_process)}) ---\n")
                for path in sorted(files_to_process): logfile.write(f"{path}\n")
            print(f"\n{Fore.GREEN}[OK] Testlauf-Log wurde erfolgreich erstellt.{Style.RESET_ALL}")
        except Exception as e: print(f"\n{Fore.RED}[FEHLER] Die Log-Datei konnte nicht geschrieben werden: {e}{Style.RESET_ALL}")
        return 0
    else:
        print("Die folgenden ODF-Zwischendateien wurden zur Löschung identifiziert:")
        for f in sorted(files_to_process): print(f"  - {f}")
        
        confirm = input(f"\n{Fore.YELLOW}Möchten Sie diese ODF-Dateien wirklich löschen? (j/n): {Style.RESET_ALL}").lower()
        if confirm != 'j': print("ODF-Löschvorgang abgebrochen."); return 0

        print(f"\nStarte ODF-Löschvorgang und erstelle Log-Datei: {log_filepath}")
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
            print(f"\n{Fore.GREEN}[OK] ODF-Log-Datei wurde erfolgreich erstellt.{Style.RESET_ALL}")
        except Exception as e: print(f"\n{Fore.RED}[FEHLER] Die Log-Datei konnte nicht geschrieben werden: {e}{Style.RESET_ALL}")
        print(f"\nODF-Aufräumen abgeschlossen. {len(successful_deletions)} gelöscht, {len(failed_deletions)} fehlgeschlagen.")
        return len(successful_deletions)

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
        return 0

    print("Die folgenden, durch Konvertierung erstellten WAV-Dateien wurden identifiziert:")
    for f in files_to_delete: print(f"  - {os.path.basename(f)}")
    
    confirm = input(f"\n{Fore.YELLOW}Möchten Sie diese WAV-Dateien wirklich löschen? (j/n): {Style.RESET_ALL}").lower()
    if confirm != 'j': print("WAV-Löschvorgang abgebrochen."); return 0

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
        print(f"\n{Fore.GREEN}[OK] WAV-Log-Datei wurde erfolgreich erstellt: {log_filepath}{Style.RESET_ALL}")
    except Exception as e: print(f"\n{Fore.RED}[FEHLER] Die Log-Datei konnte nicht geschrieben werden: {e}{Style.RESET_ALL}")
            
    print(f"\nWAV-Aufräumen abgeschlossen. {deleted_count} von {len(files_to_delete)} WAV-Dateien gelöscht.")
    return deleted_count

# ==============================================================================
# --- HAUPT-AUSFÜHRUNGSBLOCK ---
# ==============================================================================
if __name__ == "__main__":
    try:
        ac_number_input = sys.argv[1]
        disk_archive_id_input = sys.argv[2]
        print(f"Werte aus der Kommandozeile erhalten: AC={ac_number_input}, ID={disk_archive_id_input}")
        
        # NEU: Datenpfad aus menu.py übernehmen (sys.argv[3] oder Umgebungsvariable DATA_PATH)
        if len(sys.argv) >= 4:
            data_path_input = Path(sys.argv[3])
        else:
            data_path_input = Path(os.environ.get("DATA_PATH", Path.home() / "Documents/data" / ac_number_input / disk_archive_id_input))
            
    except IndexError:
        print(f"{Fore.RED}FEHLER: AC-Nummer und Datenträger-ID wurden nicht übergeben.{Style.RESET_ALL}"); sys.exit(1)

    validated_paths = setup_and_validate_paths(
        ac_number_input, 
        disk_archive_id_input,
        project_base_path_override=data_path_input
    )

    if validated_paths:
        while True:
            print(f"\n{Fore.MAGENTA}========================================")
            print(f"{Fore.CYAN}  Wählen Sie eine Aufräum-Aktion:")
            print(f"{Fore.MAGENTA}========================================")
            print(f"{Fore.WHITE}  1 - ODF- und WAV-Zwischendateien löschen")
            print(f"{Fore.WHITE}  Q - Beenden")
            print(f"{Fore.MAGENTA}========================================{Style.RESET_ALL}")
            choice = input(f"{Fore.YELLOW}Ihre Wahl: {Style.RESET_ALL}").strip().lower()

            if choice == '1':
                print("\n--- Aktion: ODF- und WAV-Zwischendateien in einem Rutsch löschen ---")
                
                # --- SCHRITT 1: ODF-Dateien löschen ---
                print("\n" + "="*60)
                print("  SCHRITT 1/2: ODF-Zwischendateien")
                print("="*60)
                odf_deleted = manage_intermediate_files(
                    folder=validated_paths["target_folder"],
                    log_filepath=validated_paths["log_filepath_odf"],
                    is_dry_run=DELETE_ODF_DRY_RUN
                )
                
                # Kurze Pause zwischen den Schritten
                print("\n" + "-"*60)
                
                # --- SCHRITT 2: WAV-Dateien löschen ---
                print("\n" + "="*60)
                print("  SCHRITT 2/2: Konvertierte WAV-Dateien")
                print("="*60)
                wav_deleted = find_and_delete_intermediate_wavs(
                    folder=validated_paths["target_folder"],
                    log_filepath=validated_paths["log_filepath_wav"]
                )
                
                # --- ZUSAMMENFASSUNG ---
                print("\n" + "="*60)
                print("  ZUSAMMENFASSUNG")
                print("="*60)
                print(f"  ODF-Dateien gelöscht: {odf_deleted}")
                print(f"  WAV-Dateien gelöscht: {wav_deleted}")
                print(f"  Gesamt gelöscht:       {odf_deleted + wav_deleted}")
                print("="*60)
                
                input("\nAktion beendet. Drücken Sie Enter, um zum Menü zurückzukehren.")
            
            elif choice == 'q':
                break
            else:
                print("\nUngültige Auswahl. Bitte erneut versuchen.")

        destination_folder = validated_paths["target_folder"].parent
        
        print("")
        open_folder = input(f"{Fore.YELLOW}Zielordner oeffnen? (j/n): {Style.RESET_ALL}").lower()
        if open_folder == 'j':
            if sys.platform == "win32":
                os.startfile(str(destination_folder))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(destination_folder)])
            else:
                subprocess.run(["xdg-open", str(destination_folder)])
            print(f"{Fore.GREEN}Zielordner geoeffnet{Style.RESET_ALL}")

    else:
        print(f"\n{Fore.RED}Skript wird aufgrund von Konfigurationsfehlern beendet.{Style.RESET_ALL}")

    print(f"\n{Fore.MAGENTA}Skript beendet.{Style.RESET_ALL}")
    input(f"{Fore.CYAN}Drücken Sie Enter, um das Fenster zu schließen.{Style.RESET_ALL}")