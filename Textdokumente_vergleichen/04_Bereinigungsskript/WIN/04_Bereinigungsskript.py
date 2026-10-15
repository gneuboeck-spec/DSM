# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import sys
import shutil
import subprocess
import stat
from collections import defaultdict
from pathlib import Path
from datetime import datetime

# GUI-Importe für die Dialogfenster
import tkinter as tk
from tkinter import filedialog, messagebox

# ==============================================================================
# 🔧 KONFIGURATION
# ==============================================================================

DRY_RUN = False  # Auf True setzen, um nur zu simulieren ohne wirklich zu löschen
DELETE_KEYWORDS = [ "video_konvertierung", "konvertierungslog", "konvertierungslog_praesentation_tabelle", "konvertierungslog_html_mht", "bereinigungslog" ]
SYSTEM_HIDDEN_FILES = [ "Thumbs.db", "desktop.ini" ]
DELETE_EXTENSIONS = [
    ".001", ".030", ".2gr", ".3gr", ".abk", ".acl", ".acm", ".acs", ".agd", ".alt", ".ani", ".ann", ".ax", ".bak", ".bat", ".bin", ".bmt", ".bof", ".bpl", ".cab", "cal", ".cat", ".cbd", ".cb", ".cbk", ".cfg", ".chk", ".chl", ".chm", ".chw", ".class", ".clb", ".clp", ".cnt", ".cnf", ".cnv", ".com", ".cov", ".cpe", ".cpi", ".cpl", ".cpx", ".crd", ".crl", ".cur", ".ctx", ".dat", ".db", ".dbs", ".dls", ".ds", ".dsz", ".dct", ".desklink", ".dfv", ".dic", ".dka", ".dki",
    ".dll", ".dmp", ".dsc", ".dr_", ".drv", ".p01", ".ecf", ".ecw", ".ess", ".exc", ".ass", ".env", ".evt", ".exe", ".fcs", ".fi", ".flg", ".flt", ".fnt", ".fon", ".for", ".fot", ".fsd", ".fsi", ".gid", ".grd", ".grt", ".grp", ".he4", ".hic", ".him", ".hti", ".hlp", ".hpm", ".htt", ".htx", ".htz", ".hyp", ".icm", ".ico", ".id", ".idf", ".idx", ".inf", ".ini", ".ink", ".ins", ".in2", ".isr", ".isu", ".iwa", ".job", ".jpg^", ".ki", ".krn", ".ku4",
    ".last", ".lex", ".lgo", ".lib", ".liveupdate", ".ld", ".lnk", ".log", ".lst", ".lwa", ".m2v", ".mad", ".MAPIMail", ".mdb", ".ml", ".ms", ".msi", ".msc", ".msg", ".mbx", ".mbox", ".mod", ".mtm", ".mydocs", "._mp", ".nch", ".net", ".nls", ".nt", ".ns", ".olb", ".old", ".ocx", ".osd", ".ovl", ".pal", ".par", ".p01", ".p02", ".p03", ".pbk", ".pci", ".pco", ".pdr", ".pgm", ".pfm", ".pfb", ".pif", ".pip", ".pkg", ".plx", ".pnf", ".pol", ".pr4", ".pro", ".prx", ".ps2", ".ptm", ".pwl", ".qlc", ".qdat", ".qtp", ".qtr", ".qts", ".qtx", ".ra4", ".rat", ".rbk", ".reg", ".rle", ".rsc", ".sav", ".sca", ".scn", ".scf", ".scr", ".sdw", ".set", ".sf0", ".sfc", ".shx", ".sik", ".skp", ".sob", ".spd", ".swx", ".sys",
    ".sdb", ".sig", ".slt", ".smm", ".sol", ".spc", ".ss", ".stb", ".stt", ".sts", ".str", ".sty", ".syd", ".tab", ".t", ".tbs", ".temp", ".tbl", ".ths", ".tlb", ".tmp", ".tsc", ".tsk", ".ttf", ".ttx", ".tsp", ".tys", ".tyq", ".uce", ".url", ".umb", ".utf", ".vbx", ".vid", ".vue", ".vxd", ".wab", ".wa~", ".wbm", ".wlx", ".wof", ".w31", ".xml.pdf", ".x32", ".000", ".386"
]

# ==============================================================================
# --- SKRIPT-LOGIK ---
# ==============================================================================

def write_log_file(log_path, mode, extensions_counter, files_list, dirs_list):
    """Schreibt die Zusammenfassung in eine Log-Datei (entweder Vorschau oder final)."""
    header_text = "VORSCHAU: Folgende Elemente wurden zur Löschung identifiziert" if mode == 'preview' else "BERICHT: Folgende Elemente WURDEN GELÖSCHT"
    
    print(f"\nErstelle {mode}-Log-Datei: {log_path}")
    try:
        sorted_items = sorted(extensions_counter.items(), key=lambda item: item[1], reverse=True)
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"Protokoll der VL-Bereinigung vom {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"STATUS: {header_text}\n" + "=" * 60 + "\n")
            
            f.write("Zusammenfassung der Dateitypen:\n")
            f.write(f"{'TYP':<15} ANZAHL\n-----------------------\n")
            if not sorted_items:
                f.write("Keine Dateien mit den angegebenen Endungen gefunden.\n")
            else:
                for ext, count in sorted_items:
                    f.write(f"{ext:<15} {count}\n")
            
            f.write(f"\n\n--- Detaillierte Liste der {len(files_list)} Dateien ---\n")
            for file_path in sorted(files_list):
                f.write(f"{file_path}\n")

            f.write(f"\n\n--- Detaillierte Liste der {len(dirs_list)} leeren Ordner ---\n")
            for dir_path in sorted(dirs_list):
                f.write(f"{dir_path}\n")
        print(f"[OK] {mode.capitalize()}-Log-Datei erfolgreich erstellt.")
        return True
    except Exception as e:
        print(f"[FEHLER] {mode.capitalize()}-Log-Datei konnte nicht erstellt werden: {e}")
        return False

def find_unwanted_items(base_dir):
    """Durchsucht ein Verzeichnis und gibt Listen der zu löschenden Elemente zurück."""
    files_to_delete = []
    empty_dirs_to_delete = []
    
    for root, dirs, files in os.walk(base_dir, topdown=False):
        for filename in files:
            file_path = os.path.join(root, filename)
            lower_filename = filename.lower()
            matched_ext = next((ext for ext in DELETE_EXTENSIONS if lower_filename.endswith(ext)), None)
            should_delete = (
                lower_filename in SYSTEM_HIDDEN_FILES or
                filename.startswith("._") or (filename.startswith('.') and filename not in ['.git', '.gitignore']) or
                filename.startswith('~') or any(keyword in lower_filename for keyword in DELETE_KEYWORDS) or
                matched_ext is not None
            )
            if should_delete:
                files_to_delete.append(file_path)

        for dirname in dirs:
            dir_path = os.path.join(root, dirname)
            try:
                if not os.listdir(dir_path):
                    empty_dirs_to_delete.append(dir_path)
            except Exception: 
                pass
    return files_to_delete, empty_dirs_to_delete

def perform_deletion(files_to_delete, empty_dirs_to_delete, extensions_counter, final_deleted_files, final_deleted_dirs):
    """Führt den eigentlichen Löschvorgang für die übergebenen Listen durch."""
    print("\n--- Starte Löschvorgang ---")
    
    for file_path in files_to_delete:
        try:
            # 1. Versuch: Normaler Löschversuch
            os.remove(file_path)
            print(f"[OK] Datei gelöscht: {file_path}")
            final_deleted_files.append(file_path)
            
            ext = next((ext for ext in DELETE_EXTENSIONS if file_path.lower().endswith(ext)), "Andere")
            extensions_counter[ext] += 1
            
        except PermissionError:
            # 2. Versuch: Wenn die Datei schreibgeschützt ist, Attribut entfernen und erneut versuchen
            try:
                os.chmod(file_path, stat.S_IWRITE)
                os.remove(file_path)
                print(f"[OK] Datei gelöscht (Schreibschutz entfernt): {file_path}")
                final_deleted_files.append(file_path)
                
                ext = next((ext for ext in DELETE_EXTENSIONS if file_path.lower().endswith(ext)), "Andere")
                extensions_counter[ext] += 1
            except Exception as e2:
                print(f"[FEHLER] Kein Zugriff auf: {file_path}")
                print(f"         Grund: Datei ist wahrscheinlich gerade in Verwendung oder eine geschützte Systemdatei. ({e2})")
                
        except Exception as e:
            print(f"[FEHLER] Unerwarteter Fehler beim Löschen von {file_path}: {e}")

    # Ordner-Logik
    for dir_path in sorted(empty_dirs_to_delete, key=len, reverse=True):
        try:
            os.rmdir(dir_path)
            print(f"[OK] Leerer Ordner gelöscht: {dir_path}")
            final_deleted_dirs.append(dir_path)
        except Exception as e:
            print(f"[FEHLER] Fehler beim Löschen des Ordners {dir_path}: {e}")

# ==============================================================================
# --- HAUPT-AUSFÜHRUNGSBLOCK (ANGEPASST FÜR MENU.PY) ===========================
# ==============================================================================
if __name__ == "__main__":
    # 1. Pfade aus sys.argv holen (werden von der menu.py übergeben)
    if len(sys.argv) < 3:
        print("❌ Fehler: Quellverzeichnis und Log-Verzeichnis fehlen.")
        print("Verwendung: python 04_bereinigung.py <quellverzeichnis> <log_verzeichnis>")
        input("Drücken Sie die Eingabetaste, um dieses Fenster zu schließen...")
        sys.exit(1)

    source_dir = sys.argv[1]
    log_dir = sys.argv[2]

    # 2. GUI initialisieren und Hauptfenster verstecken (für Bestätigungsdialoge benötigt)
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    root.update()

    try:
        base_path = Path(source_dir)
        log_path = Path(log_dir)

        if not base_path.is_dir():
            messagebox.showerror("Fehler", f"Das ausgewählte Quellverzeichnis existiert nicht:\n{base_path}")
            sys.exit(1)
            
        if not log_path.is_dir():
            messagebox.showerror("Fehler", f"Das ausgewählte Log-Verzeichnis existiert nicht:\n{log_path}")
            sys.exit(1)

        print(f"\nSkript wird mit folgenden Pfaden ausgeführt:")
        print(f"- Zu bereinigender Ordner: {base_path}")
        print(f"- Log-Ausgabeverzeichnis: {log_path}\n")

        # 3. Analyse durchführen
        print("--- Starte Analyse: Suche nach zu löschenden Elementen... ---")
        files_to_delete, empty_dirs_to_delete = find_unwanted_items(base_path)

        if not files_to_delete and not empty_dirs_to_delete:
            print("\nAnalyse abgeschlossen: Keine zu löschenden Dateien oder Ordner gefunden.")
            messagebox.showinfo("Analyse abgeschlossen", "Es wurden keine zu löschenden Dateien oder leeren Ordner gefunden.")
        else:
            print(f"\nAnalyse abgeschlossen: {len(files_to_delete)} Dateien und {len(empty_dirs_to_delete)} leere Ordner zur Löschung identifiziert.")

            # Vorschau-Log erstellen (optional, aber hilfreich)
            preview_log_name = f"bereinigung_VORSCHAU_{base_path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            preview_log_file = log_path / preview_log_name
            
            preview_extensions_count = defaultdict(int)
            for f in files_to_delete:
                ext = next((ext for ext in DELETE_EXTENSIONS if f.lower().endswith(ext)), "Andere")
                preview_extensions_count[ext] += 1
            
            write_log_file(preview_log_file, 'preview', preview_extensions_count, files_to_delete, empty_dirs_to_delete)

            # 4. Bestätigung über GUI (ersetzt die unschöne input()-Abfrage im Konsolenfenster)
            confirm_msg = (
                f"Es wurden {len(files_to_delete)} Dateien und {len(empty_dirs_to_delete)} leere Ordner zur Löschung gefunden.\n\n"
                f"Eine Vorschau wurde gespeichert unter:\n{preview_log_file}\n\n"
                f"Möchten Sie den Löschvorgang wirklich starten?"
            )
            
            if not messagebox.askyesno("Löschvorgang bestätigen", confirm_msg):
                print("Löschvorgang vom Benutzer abgebrochen.")
                sys.exit(0)

            # 5. Löschvorgang oder Simulation
            final_deleted_extensions_count = defaultdict(int)
            final_deleted_files = []
            final_deleted_dirs = []

            if DRY_RUN:
                print("\n=== TESTLAUF (DRY_RUN) AKTIV ===")
                print("--- Simulation ---")
                final_deleted_files = files_to_delete
                final_deleted_dirs = empty_dirs_to_delete
            else:
                perform_deletion(files_to_delete, empty_dirs_to_delete, final_deleted_extensions_count, final_deleted_files, final_deleted_dirs)

            # 6. Finales Log schreiben
            if final_deleted_files or final_deleted_dirs:
                final_log_name = f"geloeschte_{base_path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                final_log_file = log_path / final_log_name
                write_log_file(final_log_file, 'final', final_deleted_extensions_count, final_deleted_files, final_deleted_dirs)
                
                print("\n\033[92mBereinigung erfolgreich abgeschlossen!\033[0m")
                messagebox.showinfo("Erfolg", f"Bereinigung abgeschlossen.\n\nDas finale Log wurde gespeichert unter:\n{final_log_file}")
            else:
                messagebox.showinfo("Info", "Keine Dateien wurden tatsächlich gelöscht.")

        # 7. Abschluss-Dialog: Ordner öffnen?
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
        # 8. Fenster offen halten für Doppelklick-Start
        print("\n" + "="*50)
        input("Drücken Sie die Eingabetaste, um dieses Fenster zu schließen...")