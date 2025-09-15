import os
import sys

# --- KONFIGURATION ---
# Stellen Sie sicher, dass dieser Pfad mit dem in Ihrem Konvertierungs-Skript übereinstimmt.
target_folder = "/Users/gregorneuboeck/Desktop/Texdateien_konvertieren"
# --- ENDE DER KONFIGURATION ---


def find_and_delete_intermediate_files(folder):
    """
    Durchsucht den Ordner rekursiv und löscht ODF-Zwischendateien,
    die während der Konvertierung erstellt wurden.
    """
    print(f"Starte Suche nach Zwischendateien im Ordner: {folder}\n")
    
    files_to_delete = []
    
    # Schritt 1: Sammle alle Dateien im Verzeichnisbaum
    all_found_files = set()
    for root, _, files in os.walk(folder):
        for name in files:
            all_found_files.add(os.path.join(root, name))

    # Schritt 2: Identifiziere die zu löschenden Zwischendateien
    for filepath in all_found_files:
        path, filename = os.path.split(filepath)
        
        # Ignoriere versteckte Dateien und temporäre Dateien
        if filename.startswith('.') or filename.startswith('~'):
            continue
            
        parts = filename.split('.')
        
        # Eine potenzielle Zwischendatei hat mindestens 3 Teile: name.original_ext.odf_ext
        if len(parts) >= 3:
            odf_ext = parts[-1].lower()
            
            # Prüfe, ob es sich um eine unserer ODF-Zieldateien handelt
            if odf_ext in {"odt", "ods", "odp"}:
                # Baue den Namen der vermuteten Originaldatei zusammen
                # z.B. aus "Report.ppt.odp" wird "Report.ppt"
                original_filename = ".".join(parts[:-1])
                original_filepath = os.path.join(path, original_filename)
                
                # DIE ENTSCHEIDENDE PRÜFUNG:
                # Lösche die Datei nur, wenn die Originaldatei auch existiert.
                if original_filepath in all_found_files:
                    files_to_delete.append(filepath)

    # Schritt 3: Führe die Löschung nach Bestätigung durch
    if not files_to_delete:
        print("Keine Zwischendateien zum Löschen gefunden.")
        return

    print("Die folgenden Zwischendateien werden gelöscht:")
    for f in files_to_delete:
        print(f"  - {os.path.basename(f)}")
    
    # Sicherheitsabfrage an den Benutzer
    # Um die Abfrage zu überspringen, kommentieren Sie die nächsten 3 Zeilen aus
    # und entfernen Sie die Einrückung des folgenden for-Blocks.
    confirm = input("\nMöchten Sie diese Dateien wirklich löschen? (j/n): ").lower()
    if confirm != 'j':
        print("Löschvorgang abgebrochen.")
        return

    deleted_count = 0
    for f in files_to_delete:
        try:
            os.remove(f)
            print(f"Gelöscht: {os.path.basename(f)}")
            deleted_count += 1
        except Exception as e:
            print(f"FEHLER beim Löschen von {os.path.basename(f)}: {e}")
            
    print(f"\nAufräumen abgeschlossen. {deleted_count} von {len(files_to_delete)} Zwischendateien gelöscht.")


if __name__ == "__main__":
    if not os.path.isdir(target_folder):
        print(f"FEHLER: Der angegebene Ordner existiert nicht: {target_folder}")
        sys.exit(1)
    find_and_delete_intermediate_files(target_folder)