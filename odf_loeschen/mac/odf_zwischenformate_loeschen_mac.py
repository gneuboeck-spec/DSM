import os
import sys
from datetime import datetime

# --- KONFIGURATION (für macOS anpassen) ---

# 1. Geben Sie hier den Pfad zum zu bereinigenden Ordner an.
#    Verwenden Sie den Standard-Pfadstil von macOS.
#    Beispiel: /Users/IhrBenutzername/Desktop/Projektordner
target_folder = "/Users/IhrBenutzername/Desktop/AC15993802/ZPH1705-120_04-12-03-01/2_ZPH1705-120_04-12-03-01_extracted-files"

# 2. Name der Log-Datei. Sie wird automatisch im `target_folder` erstellt.
output_log_filename = "bereinigungslog_final.txt"

# 3. TRUE/FALSE-SCHALTER für den Testlauf
#    True:  Nur simulieren und eine Liste der zu löschenden Dateien im Log erstellen. Es wird nichts gelöscht.
#    False: Dateien nach Bestätigung tatsächlich löschen und den Vorgang protokollieren.
dry_run = True
# --- ENDE DER KONFIGURATION ---


def manage_intermediate_files(folder, log_filepath, is_dry_run):
    """
    Findet Zwischendateien. Im Testlauf (dry_run=True) werden sie nur protokolliert.
    Im Echtlauf (dry_run=False) werden sie nach Bestätigung gelöscht und protokolliert.
    """
    
    # Header für den aktuellen Modus
    if is_dry_run:
        print("=== TESTLAUF AKTIV (KEINE DATEIEN WERDEN GELÖSCHT) ===")
    else:
        print("=== ECHTER LÖSCHVORGANG AKTIV ===")
        
    print(f"Starte Suche nach Zwischendateien im Ordner: {folder}\n")
    
    files_to_process = []
    
    # Schritt 1 & 2: Dateien finden (plattformunabhängige Logik)
    all_found_files = set()
    for root, _, files in os.walk(folder):
        for name in files:
            all_found_files.add(os.path.join(root, name))

    for filepath in all_found_files:
        path, filename = os.path.split(filepath)
        if filename.startswith('.') or filename.startswith('~'):
            continue
        parts = filename.split('.')
        if len(parts) >= 3:
            odf_ext = parts[-1].lower()
            if odf_ext in {"odt", "ods", "odp"}:
                original_filename = ".".join(parts[:-1])
                original_filepath = os.path.join(path, original_filename)
                if original_filepath in all_found_files:
                    files_to_process.append(filepath)

    if not files_to_process:
        print("Keine Zwischendateien zum Verarbeiten gefunden.")
        return

    # --- Logik basierend auf dem dry_run-Schalter ---

    if is_dry_run:
        # --- LOGIK FÜR DEN TESTLAUF ---
        print(f"{len(files_to_process)} potenzielle Zwischendateien gefunden.")
        print(f"Schreibe eine Liste der Dateien in die Log-Datei: {log_filepath}")

        try:
            with open(log_filepath, "w", encoding="utf-8") as logfile:
                logfile.write("# Protokoll des TESTLAUFS (keine Dateien wurden gelöscht)\n")
                logfile.write(f"# Erstellt am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                logfile.write(f"# Durchsuchter Ordner: {folder}\n")
                logfile.write("=" * 50 + "\n\n")
                logfile.write(f"--- DATEIEN, DIE GELÖSCHT WÜRDEN ({len(files_to_process)}) ---\n")
                for path in files_to_process:
                    logfile.write(f"{path}\n")
            print("\n[OK] Testlauf-Log wurde erfolgreich erstellt.")
        except Exception as e:
            print(f"\n[FEHLER] Die Log-Datei konnte nicht geschrieben werden: {e}")

    else:
        # --- LOGIK FÜR DEN ECHTEN LÖSCHVORGANG ---
        print("Die folgenden Zwischendateien wurden zur Löschung identifiziert:")
        for f in files_to_process:
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
                for path in successful_deletions: logfile.write(f"{path}\n")
                logfile.write(f"\n--- FEHLER BEIM LÖSCHEN ({len(failed_deletions)}) ---\n")
                if failed_deletions:
                    for path, error in failed_deletions: logfile.write(f"Datei: {path}\nFehler: {error}\n\n")
                else:
                    logfile.write("Keine Fehler aufgetreten.\n")
            print(f"\n[OK] Log-Datei wurde erfolgreich erstellt.")
        except Exception as e:
            print(f"\n[FEHLER] Die Log-Datei konnte nicht geschrieben werden: {e}")
            
        print(f"\nAufräumen abgeschlossen. {len(successful_deletions)} gelöscht, {len(failed_deletions)} fehlgeschlagen.")


if __name__ == "__main__":
    # Optional: Ein Platzhalter-Check, falls das Skript geteilt wird
    if "IhrBenutzername" in target_folder:
        print("""
============================================================
BITTE BEARBEITEN SIE DAS SKRIPT!
Ersetzen Sie 'IhrBenutzername' im Pfad 'target_folder'.
============================================================
""")
        sys.exit(1)

    if not os.path.isdir(target_folder):
        print(f"FEHLER: Der angegebene Ordner existiert nicht: {target_folder}")
        sys.exit(1)
    
    # Der vollständige Pfad zur Log-Datei wird jetzt hier automatisch zusammengesetzt
    log_file_path = os.path.join(target_folder, output_log_filename)
    
    manage_intermediate_files(target_folder, log_file_path, dry_run)