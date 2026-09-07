# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import sys
import hashlib
import csv
import stat
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# ==============================================================================
# 🔧 KONFIGURATION
# ==============================================================================

# Auf True setzen, um das Skript nur zu testen, ohne wirklich Dateien zu löschen
DRY_RUN = False  

# Chunk-Größe für das Hashing (8 MB), um auch große Dateien speicherschonend zu verarbeiten
CHUNK_SIZE = 8 * 1024 * 1024


# ==============================================================================
# === HILFSFUNKTIONEN ==========================================================
# ==============================================================================

def calculate_sha256(file_path: Path) -> str:
    """Berechnet den SHA-256 Hash einer Datei in Chunks."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(CHUNK_SIZE), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except PermissionError:
        return "PERMISSION_DENIED"
    except Exception as e:
        return f"ERROR_{str(e)}"


def format_size(size_bytes):
    """Formatiert Bytes in ein lesbares Format (KB, MB, GB)."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0


def write_log_file(log_path, mode, log_data):
    """Schreibt die Zusammenfassung in eine CSV-Log-Datei (Vorschau oder Final)."""
    header_text = "VORSCHAU: Folgende Elemente wurden zur Löschung identifiziert" if mode == 'preview' else "BERICHT: Folgende Elemente WURDEN GELÖSCHT"
    
    print(f"\nErstelle {mode}-Log-Datei: {log_path}")
    try:
        with open(log_path, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ['Gruppe_ID', 'Dateiname', 'Relativer_Pfad', 'Dateigröße', 'SHA256', 'Aktion']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            # Schreibe einen Kommentar in die erste Zeile (als Excel-Kommentar oder einfach Text davor)
            # Da CSV keine Header-Kommentare gut unterstützt, fügen wir es als erste Datenzeile ein oder lassen es im Konsolen-Log.
            # Wir schreiben es sauber als CSV.
            writer.writerows(log_data)
            
        print(f"[OK] {mode.capitalize()}-Log-Datei erfolgreich erstellt.")
        return True
    except Exception as e:
        print(f"[FEHLER] {mode.capitalize()}-Log-Datei konnte nicht erstellt werden: {e}")
        return False


def find_duplicate_groups(base_dir):
    """Durchsucht ein Verzeichnis und gibt Gruppen von Duplikaten zurück."""
    print("--- Starte Analyse: Suche nach Prüfsummendubletten... ---")
    
    # 1. Nach Größe gruppieren
    size_groups = defaultdict(list)
    total_files = 0
    
    for file_path in base_dir.rglob('*'):
        if file_path.is_file():
            try:
                size = file_path.stat().st_size
                size_groups[size].append(file_path)
                total_files += 1
            except Exception:
                continue

    print(f"   ✅ {total_files} Dateien gescannt.")
    
    potential_duplicates = {size: files for size, files in size_groups.items() if len(files) > 1}
    print(f"   ℹ️  {len(potential_duplicates)} Größen-Kategorien mit potenziellen Duplikaten gefunden.")

    # 2. Prüfsummen berechnen
    print("   Berechne SHA-256 Prüfsummen für potenzielle Duplikate...")
    hash_groups = defaultdict(list)
    files_to_hash = sum(len(files) for files in potential_duplicates.values())
    hashed_count = 0

    for size, files in potential_duplicates.items():
        for file_path in files:
            file_hash = calculate_sha256(file_path)
            if file_hash and not file_hash.startswith("ERROR"):
                unique_key = f"{size}_{file_hash}"
                hash_groups[unique_key].append(file_path)
            
            hashed_count += 1
            if hashed_count % 100 == 0:
                print(f"   ⏳ Fortschritt: {hashed_count}/{files_to_hash} Dateien gehasht...", end='\r')
    
    print(f"\n   ✅ {hashed_count} Prüfsummen berechnet.")

    # 3. Echte Duplikate filtern
    actual_duplicates = {key: files for key, files in hash_groups.items() if len(files) > 1}
    return actual_duplicates, total_files


def perform_deletion(duplicate_groups, base_dir, log_dir):
    """Führt den eigentlichen Löschvorgang durch und erstellt das finale Log."""
    print("\n--- Starte Löschvorgang ---")
    
    final_log_data = []
    deleted_count = 0
    saved_space_bytes = 0

    for group_id, (unique_key, files) in enumerate(duplicate_groups.items(), 1):
        size_str, file_hash = unique_key.split('_', 1)
        size_bytes = int(size_str)
        
        # Erste Datei ist das Original
        original_file = files[0]
        final_log_data.append({
            'Gruppe_ID': f"GRUPPE_{group_id:03d}",
            'Dateiname': original_file.name,
            'Relativer_Pfad': str(original_file.relative_to(base_dir)),
            'Dateigröße': format_size(size_bytes),
            'SHA256': file_hash,
            'Aktion': 'BEHALTEN (Original)'
        })

        # Rest sind Duplikate
        for dup_file in files[1:]:
            if DRY_RUN:
                action_str = "GELÖSCHT (Simulation)"
                deleted_count += 1
                saved_space_bytes += size_bytes
            else:
                try:
                    # 1. Versuch: Normaler Löschversuch
                    dup_file.unlink()
                    action_str = "GELÖSCHT (Duplikat)"
                    deleted_count += 1
                    saved_space_bytes += size_bytes
                    print(f"[OK] Datei gelöscht: {dup_file.name}")
                    
                except PermissionError:
                    # 2. Versuch: Schreibschutz entfernen
                    try:
                        os.chmod(dup_file, stat.S_IWRITE)
                        dup_file.unlink()
                        action_str = "GELÖSCHT (Schreibschutz entfernt)"
                        deleted_count += 1
                        saved_space_bytes += size_bytes
                        print(f"[OK] Datei gelöscht (Schreibschutz entfernt): {dup_file.name}")
                    except Exception as e2:
                        action_str = f"FEHLER: {e2}"
                        print(f"[FEHLER] Kein Zugriff auf: {dup_file.name} ({e2})")
                except Exception as e:
                    action_str = f"FEHLER: {e}"
                    print(f"[FEHLER] Unerwarteter Fehler beim Löschen von {dup_file.name}: {e}")

            final_log_data.append({
                'Gruppe_ID': f"GRUPPE_{group_id:03d}",
                'Dateiname': dup_file.name,
                'Relativer_Pfad': str(dup_file.relative_to(base_dir)),
                'Dateigröße': format_size(size_bytes),
                'SHA256': file_hash,
                'Aktion': action_str
            })

    return final_log_data, deleted_count, saved_space_bytes


# ==============================================================================
# --- HAUPT-AUSFÜHRUNGSBLOCK (ANGEPASST FÜR MENU.PY) ===========================
# ==============================================================================
if __name__ == "__main__":
    # 1. Pfade aus sys.argv holen
    if len(sys.argv) < 3:
        print("❌ Fehler: Quellverzeichnis und Log-Verzeichnis fehlen.")
        print("Verwendung: python 01_dublikatenfinder.py <quellverzeichnis> <log_verzeichnis>")
        input("Drücken Sie die Eingabetaste, um dieses Fenster zu schließen...")
        sys.exit(1)

    source_dir = sys.argv[1]
    log_dir = sys.argv[2]

    # 2. GUI initialisieren
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    root.update()

    try:
        base_path = Path(source_dir).resolve()
        log_path = Path(log_dir).resolve()

        if not base_path.is_dir():
            messagebox.showerror("Fehler", f"Das ausgewählte Quellverzeichnis existiert nicht:\n{base_path}")
            sys.exit(1)
            
        if not log_path.is_dir():
            messagebox.showerror("Fehler", f"Das ausgewählte Log-Verzeichnis existiert nicht:\n{log_path}")
            sys.exit(1)

        print(f"\nSkript wird mit folgenden Pfaden ausgeführt:")
        print(f"- Zu prüfender Ordner: {base_path}")
        print(f"- Log-Ausgabeverzeichnis: {log_path}\n")

        if DRY_RUN:
            print("\n\033[93m=== TESTLAUF (DRY_RUN) AKTIV ===\033[0m")
            print("Es werden keine Dateien wirklich gelöscht.\n")

        # 3. Analyse durchführen
        duplicate_groups, total_files = find_duplicate_groups(base_path)

        if not duplicate_groups:
            print("\nAnalyse abgeschlossen: Keine Prüfsummendubletten gefunden.")
            messagebox.showinfo("Analyse abgeschlossen", "Es wurden keine Prüfsummendubletten gefunden.\nAlle Dateien sind einzigartig.")
            sys.exit(0)

        # 4. Vorschau-Log erstellen
        preview_log_data = []
        preview_deleted_count = 0
        preview_saved_bytes = 0

        for group_id, (unique_key, files) in enumerate(duplicate_groups.items(), 1):
            size_str, file_hash = unique_key.split('_', 1)
            size_bytes = int(size_str)
            
            preview_log_data.append({
                'Gruppe_ID': f"GRUPPE_{group_id:03d}",
                'Dateiname': files[0].name,
                'Relativer_Pfad': str(files[0].relative_to(base_path)),
                'Dateigröße': format_size(size_bytes),
                'SHA256': file_hash,
                'Aktion': 'BEHALTEN (Original)'
            })
            
            for dup_file in files[1:]:
                preview_log_data.append({
                    'Gruppe_ID': f"GRUPPE_{group_id:03d}",
                    'Dateiname': dup_file.name,
                    'Relativer_Pfad': str(dup_file.relative_to(base_path)),
                    'Dateigröße': format_size(size_bytes),
                    'SHA256': file_hash,
                    'Aktion': 'ZUM LÖSCHEN VORGEMERKT'
                })
                preview_deleted_count += 1
                preview_saved_bytes += size_bytes

        preview_log_name = f"dublikaten_VORSCHAU_{base_path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        preview_log_file = log_path / preview_log_name
        
        write_log_file(preview_log_file, 'preview', preview_log_data)

        # 5. Vorschau-Datei automatisch öffnen, damit der Benutzer sie kontrollieren kann
        try:
            if sys.platform == "win32":
                os.startfile(str(preview_log_file))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(preview_log_file)])
            else:
                subprocess.run(["xdg-open", str(preview_log_file)])
        except Exception:
            pass # Falls das Öffnen fehlschlägt, fahren wir trotzdem fort

        # 6. Bestätigung über GUI
        confirm_msg = (
            f"Es wurden {len(duplicate_groups)} Gruppen mit insgesamt {preview_deleted_count} Duplikaten gefunden.\n"
            f"Potenziell freigegebener Speicher: {format_size(preview_saved_bytes)}\n\n"
            f"Eine Vorschau-Liste wurde erstellt und geöffnet unter:\n{preview_log_file}\n\n"
            f"Möchten Sie die als 'VORGEMERKT' markierten Dateien jetzt wirklich löschen?"
        )
        
        if not messagebox.askyesno("Löschvorgang bestätigen", confirm_msg):
            print("Löschvorgang vom Benutzer abgebrochen.")
            sys.exit(0)

        # 7. Löschvorgang durchführen
        final_log_data, actual_deleted_count, actual_saved_bytes = perform_deletion(
            duplicate_groups, base_path, log_path
        )

        # 8. Finales Log schreiben
        if actual_deleted_count > 0 or DRY_RUN:
            final_log_name = f"dublikaten_GELÖSCHT_{base_path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            final_log_file = log_path / final_log_name
            write_log_file(final_log_file, 'final', final_log_data)
            
            print(f"\n\033[92mBereinigung erfolgreich abgeschlossen!\033[0m")
            messagebox.showinfo(
                "Erfolg", 
                f"Bereinigung abgeschlossen.\n\n"
                f"Gelöschte Duplikate: {actual_deleted_count}\n"
                f"Freigegebener Speicher: {format_size(actual_saved_bytes)}\n\n"
                f"Das finale Log wurde gespeichert unter:\n{final_log_file}"
            )
        else:
            messagebox.showinfo("Info", "Keine Dateien wurden tatsächlich gelöscht (möglicherweise aufgrund von Zugriffsfehlern).")

        # 9. Abschluss-Dialog: Ordner öffnen?
        if messagebox.askyesno("Analyse abgeschlossen", f"Die Bereinigung ist fertig.\n\nMöchten Sie das bereinigte Verzeichnis öffnen?\n{source_dir}"):
            if sys.platform == "win32":
                os.startfile(str(base_path))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(base_path)])
            else:
                subprocess.run(["xdg-open", str(base_path)])

    except Exception as e:
        messagebox.showerror("Unerwarteter Fehler", f"Ein Fehler ist aufgetreten:\n{str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        # 10. Fenster offen halten für Doppelklick-Start
        print("\n" + "="*50)
        input("Drücken Sie die Eingabetaste, um dieses Fenster zu schließen...")