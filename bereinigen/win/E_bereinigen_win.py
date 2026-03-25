# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import sys
import subprocess
from collections import defaultdict
from pathlib import Path
from datetime import datetime

# ==============================================================================
# 🔧 KONFIGURATION
# ==============================================================================

DRY_RUN = False
CREATE_LOG_FILE = True
DELETE_KEYWORDS = [ "video_konvertierung", "konvertierungslog", "konvertierungslog_praesentation_tabelle", "konvertierungslog_html_mht", "bereinigungslog" ]
SYSTEM_HIDDEN_FILES = [ "Thumbs.db", "desktop.ini" ]
DELETE_EXTENSIONS = [
    ".001", ".030", ".2gr", ".3gr", ".abk", ".acl", ".acm", ".acs", ".agd", ".alt", ".ani", ".ann", ".ax", ".bak", ".bat", ".bin", ".bmt", ".bof", ".bpl", ".cab", "cal", ".cat", ".cbd", ".cb", ".cbk", ".cfg", ".chk", ".chl", ".chm", ".chw", ".class", ".clb", ".clp", ".cnt", ".cnf", ".cnv", ".com", ".cov", ".cpe", ".cpi", ".cpl", ".cpx", ".crd", ".crl", ".cur", ".ctx", ".dat", ".db", ".dbs", ".dls", ".ds", ".dsz", ".dct", ".desklink", ".dfv", ".dic", ".dka", ".dki",
    ".dll", ".dmp", ".dsc", ".dr_", ".drv", ".p01", ".ecf", ".ecw", ".ess", ".exc", ".ass", ".env", ".evt", ".exe", ".fcs", ".fi", ".flg", ".flt", ".fnt", ".fon", ".for", ".fot", ".fsd", ".fsi", ".gid", ".grd", ".grt", ".grp", ".he4", ".hic", ".him", ".hti", ".hlp", ".hpm", ".htt", ".htx", ".htz", ".hyp", ".icm", ".ico", ".id", ".idf", ".idx", ".inf", ".ini", ".ink", ".ins", ".in2", ".isr", ".isu", ".iwa", ".job", ".jpg^", ".ki", ".krn", ".ku4",
    ".last", ".lex", ".lgo", ".lib", ".liveupdate", ".ld", ".lnk", ".log", ".lst", ".lwa", ".m2v", ".mad", ".MAPIMail", ".mdb", ".ml", ".ms", ".msi", ".msc", ".msg", ".mbx", ".mbox", ".mod", ".mtm", ".mydocs", "._mp", ".nch", ".net", ".nls", ".nt", ".ns", ".olb", ".old", ".ocx", ".osd", ".ovl", ".pal", ".par", ".p01", ".p02", ".p03", ".pbk", ".pci", ".pco", ".pdr", ".pgm", ".pfm", ".pfb", ".pif", ".pip", ".pkg", ".plx", ".pnf", ".pol", ".pr4", ".pro", ".prx", ".ps2", ".ptm", ".pwl", ".qlc", ".qdat", ".qtp", ".qtr", ".qts", ".qtx", ".ra4", ".rat", ".rbk", ".reg", ".rle", ".rsc", ".sav", ".sca", ".scn", ".scf", ".scr", ".sdw", ".set", ".sf0", ".sfc", ".shx", ".sik", ".skp", ".sob", ".spd", ".swx", ".sys",
    ".sdb", ".sig", ".slt", ".smm", ".sol", ".spc", ".ss", ".stb", ".stt", ".sts", ".str", ".sty", ".syd", ".tab", ".t", ".tbs", ".temp", ".tbl", ".ths", ".tlb", ".tmp", ".tsc", ".tsk", ".ttf", ".ttx", ".tsp", ".tys", ".tyq", ".uce", ".url", ".umb", ".utf", ".vbx", ".vid", ".vue", ".vxd", ".wab", ".wa~", ".wbm", ".wlx", ".wof", ".w31", ".xml.pdf", ".x32", ".000", ".386", ".zip"
]

def setup_and_validate_paths(ac_number, disk_archive_id):
    project_base_path = Path.home() / "Documents/data" / ac_number / disk_archive_id
    transfer_folder = project_base_path / f"3_{disk_archive_id}_for-transfer"
    paths = {
        "base_directory": transfer_folder / "files",
        "log_file_path": transfer_folder / f"3_{disk_archive_id}_for-transfer_delete-all.log",
        "preview_log_file_path": transfer_folder / f"3_{disk_archive_id}_for-transfer_delete-preview-all.log"
    }
    if not paths["base_directory"].is_dir(): print(f"\033[91mFehler: Der zu bereinigende Ordner wurde nicht gefunden:\n{paths['base_directory']}\033[0m"); return None
    if not paths["log_file_path"].parent.is_dir(): print(f"\033[91mFehler: Der Ordner für die Log-Datei existiert nicht:\n{paths['log_file_path'].parent}\033[0m"); return None
    print("\033[92mAlle Pfade wurden erfolgreich gefunden und validiert.\033[0m"); return paths

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
            f.write(f"Protokoll der Bereinigung vom {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
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
    except Exception as e:
        print(f"[FEHLER] {mode.capitalize()}-Log-Datei konnte nicht erstellt werden: {e}")

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
            except Exception: pass
    return files_to_delete, empty_dirs_to_delete

def perform_deletion(files_to_delete, empty_dirs_to_delete, extensions_counter, final_deleted_files, final_deleted_dirs):
    """Führt den eigentlichen Löschvvorgang für die übergebenen Listen durch."""
    print("\n--- Starte Löschvorgang ---")
    
    for file_path in files_to_delete:
        try:
            os.remove(file_path)
            print(f"[OK] Datei gelöscht: {file_path}")
            final_deleted_files.append(file_path)
            
            ext = next((ext for ext in DELETE_EXTENSIONS if file_path.lower().endswith(ext)), "Andere")
            extensions_counter[ext] += 1
        except Exception as e:
            print(f"[FEHLER] Fehler beim Löschen von {file_path}: {e}")

    for dir_path in sorted(empty_dirs_to_delete, key=len, reverse=True):
        try:
            os.rmdir(dir_path)
            print(f"[OK] Leerer Ordner gelöscht: {dir_path}")
            final_deleted_dirs.append(dir_path)
        except Exception as e:
            print(f"[FEHLER] Fehler beim Löschen des Ordners {dir_path}: {e}")
            
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
        base_directory = validated_paths["base_directory"]
        log_file_path = validated_paths["log_file_path"]
        preview_log_file_path = validated_paths["preview_log_file_path"]

        print(f"\nSkript wird mit folgenden Pfaden ausgeführt:\n- Zu bereinigender Ordner: {base_directory}")
        if CREATE_LOG_FILE: print(f"- Vorschau-Log: {preview_log_file_path}\n- Finales Log: {log_file_path}\n")

        print("\n--- Starte Analyse: Suche nach zu löschenden Elementen... ---")
        files_to_delete, empty_dirs_to_delete = find_unwanted_items(base_directory)

        if not files_to_delete and not empty_dirs_to_delete:
            print("\nAnalyse abgeschlossen: Keine zu löschenden Dateien oder Ordner gefunden.")
        else:
            print(f"\nAnalyse abgeschlossen: {len(files_to_delete)} Dateien und {len(empty_dirs_to_delete)} leere Ordner zur Löschung identifiziert.")

            if CREATE_LOG_FILE:
                preview_extensions_count = defaultdict(int)
                for f in files_to_delete:
                    ext = next((ext for ext in DELETE_EXTENSIONS if f.lower().endswith(ext)), "Andere")
                    preview_extensions_count[ext] += 1
                write_log_file(preview_log_file_path, 'preview', preview_extensions_count, files_to_delete, empty_dirs_to_delete)
                print(f"\n\033[93mBITTE PRÜFEN: Eine Vorschau der zu löschenden Dateien wurde hier gespeichert:\n{preview_log_file_path}\033[0m")

            if not DRY_RUN:
                confirm = input("\nMöchten Sie den Löschvorgang wirklich starten? (j/n): ").lower()
                if confirm != 'j':
                    print("Löschvorgang vom Benutzer abgebrochen.")
                    sys.exit(0)
            else:
                print("""\n============================================================
=== TESTLAUF AKTIV ===
Es werden keine Dateien gelöscht, nur Aktionen simuliert.
============================================================\n""")

            final_deleted_extensions_count = defaultdict(int)
            final_deleted_files = []
            final_deleted_dirs = []

            if DRY_RUN:
                print("--- Simulation des Löschvorgangs ---")
                final_deleted_files = files_to_delete
                final_deleted_dirs = empty_dirs_to_delete
                for f in final_deleted_files:
                    print(f"[Testlauf] Datei würde gelöscht: {f}")
                    ext = next((ext for ext in DELETE_EXTENSIONS if f.lower().endswith(ext)), "Andere")
                    final_deleted_extensions_count[ext] += 1
                for d in final_deleted_dirs: print(f"[Testlauf] Leerer Ordner würde gelöscht: {d}")
            else:
                perform_deletion(files_to_delete, empty_dirs_to_delete, final_deleted_extensions_count, final_deleted_files, final_deleted_dirs)

            if CREATE_LOG_FILE and (final_deleted_files or final_deleted_dirs):
                write_log_file(log_file_path, 'final', final_deleted_extensions_count, final_deleted_files, final_deleted_dirs)

        # --- ANFANG: KORRIGIERTER CODE-BLOCK ---
        destination_folder = validated_paths["base_directory"].parent
        
        # --- Zielordner optional öffnen ---
        print("")
        open_folder = input("Zielordner oeffnen? (j/n): ").lower()
        if open_folder == 'j':
            if sys.platform == "win32":
                # KORREKTUR: Das Path-Objekt wird explizit in einen String umgewandelt
                os.startfile(str(destination_folder))
            elif sys.platform == "darwin":
                # KORREKTUR: Das Path-Objekt wird explizit in einen String umgewandelt
                subprocess.run(["open", str(destination_folder)])
            else:
                # KORREKTUR: Das Path-Objekt wird explizit in einen String umgewandelt
                subprocess.run(["xdg-open", str(destination_folder)])
            # Angepasst an den Stil des bestehenden Skripts
            print("\033[92mZielordner geoeffnet\033[0m")
        # --- ENDE: HINZUGEFÜGTER CODE-BLOCK ---

    else:
        print("\nSkript wird aufgrund von Konfigurationsfehlern beendet.")

    print("\nSkript beendet.")