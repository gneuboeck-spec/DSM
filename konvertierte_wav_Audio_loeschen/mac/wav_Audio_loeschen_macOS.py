# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import sys

# --- KONFIGURATION ---
# Stellen Sie sicher, dass dieser Pfad mit dem in Ihrem Konvertierungs-Skript übereinstimmt.
target_folder = "/Users/gregorneuboeck/Desktop/Audiodateien_konvertieren"

# Dies ist die Liste der möglichen *Original*-Endungen.
# Sie sollte mit der `source_audio_extensions`-Liste aus Ihrem Konverter übereinstimmen.
source_audio_extensions = {".aiff", ".flac", ".ogg", ".wav", ".m4a", ".wma", ".aac", ".mp3"}
# --- ENDE DER KONFIGURATION ---


def find_and_delete_intermediate_wavs(folder):
    """
    Durchsucht den Ordner rekursiv und löscht WAV-Dateien,
    die während der Konvertierung aus anderen Formaten erstellt wurden.
    """
    print(f"Starte Suche nach konvertierten WAV-Dateien im Ordner: {folder}\n")
    
    files_to_delete = []
    
    # Schritt 1: Sammle alle Dateien im Verzeichnisbaum
    all_found_files = set()
    for root, _, files in os.walk(folder):
        for name in files:
            all_found_files.add(os.path.join(root, name))

    # Schritt 2: Identifiziere die zu löschenden WAV-Dateien
    for filepath in all_found_files:
        path, filename = os.path.split(filepath)
        
        if filename.startswith('.') or filename.startswith('~'):
            continue
            
        # Wir suchen explizit nach Dateien, die auf .wav enden
        if filename.lower().endswith('.wav'):
            parts = filename.split('.')
            
            # Eine potenzielle Zwischendatei hat mindestens 3 Teile: name.original_ext.wav
            if len(parts) >= 3:
                # Rekonstruiere die vermutete Original-Endung
                original_ext = f".{parts[-2].lower()}"
                
                # Prüfe, ob die vermutete Original-Endung in unserer Liste der Quellformate ist
                if original_ext in source_audio_extensions:
                    # Baue den Namen der vermuteten Originaldatei zusammen
                    # z.B. aus "song.flac.wav" wird "song.flac"
                    original_filename = ".".join(parts[:-1])
                    original_filepath = os.path.join(path, original_filename)
                    
                    # DIE ENTSCHEIDENDE PRÜFUNG:
                    # Lösche die .wav-Datei nur, wenn die dazugehörige Originaldatei auch existiert.
                    if original_filepath in all_found_files:
                        files_to_delete.append(filepath)

    # Schritt 3: Führe die Löschung nach Bestätigung durch
    if not files_to_delete:
        print("Keine konvertierten WAV-Dateien zum Löschen gefunden.")
        return

    print("Die folgenden, durch Konvertierung erstellten WAV-Dateien werden gelöscht:")
    for f in files_to_delete:
        print(f"  - {os.path.basename(f)}")
    
    # Sicherheitsabfrage an den Benutzer
    confirm = input("\nMöchten Sie diese Dateien wirklich löschen? (j/n): ").lower()
    if confirm != 'j':
        print("Löschvorgang abgebrochen.")
        return

    deleted_count = 0
    print() # Leere Zeile für bessere Lesbarkeit
    for f in files_to_delete:
        try:
            os.remove(f)
            print(f"Gelöscht: {os.path.basename(f)}")
            deleted_count += 1
        except Exception as e:
            print(f"FEHLER beim Löschen von {os.path.basename(f)}: {e}")
            
    print(f"\nAufräumen abgeschlossen. {deleted_count} von {len(files_to_delete)} WAV-Dateien gelöscht.")


if __name__ == "__main__":
    if not os.path.isdir(target_folder):
        print(f"FEHLER: Der angegebene Ordner existiert nicht: {target_folder}")
        sys.exit(1)
    find_and_delete_intermediate_wavs(folder=target_folder)
