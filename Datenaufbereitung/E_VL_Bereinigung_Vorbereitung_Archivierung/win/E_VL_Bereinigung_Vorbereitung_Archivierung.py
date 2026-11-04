# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import sys
import shutil  # HINZUGEFÜGT für den Kopiervorgang
import subprocess
import stat
from collections import defaultdict
from pathlib import Path
from datetime import datetime

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class Fore: GREEN = RED = YELLOW = CYAN = MAGENTA = WHITE = ""
    class Style: RESET_ALL = ""

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
    ".sdb", ".sig", ".slt", ".smm", ".sol", ".spc", ".ss", ".stb", ".stt", ".sts", ".str", ".sty", ".syd", ".tab", ".t", ".tbs", ".temp", ".tbl", ".ths", ".tlb", ".tmp", ".tsc", ".tsk", ".ttf", ".ttx", ".tsp", ".tys", ".tyq", ".uce", ".url", ".umb", ".utf", ".vbx", ".vid", ".vue", ".vxd", ".wab", ".wa~", ".wbm", ".wlx", ".wof", ".w31", ".xml.pdf", ".x32", ".000", ".386"
]

def setup_and_validate_paths(ac_number, disk_archive_id, project_base_path_override=None):
    """Dynamische Pfaderstellung für VL-Bereinigung und LZA-Logging."""
    # NEU: Wenn ein Pfad aus dem Menü übergeben wurde, nutzen wir diesen.
    # Andernfalls greift der alte Fallback-Pfad.
    if project_base_path_override:
        project_base_path = Path(project_base_path_override)
    else:
        project_base_path = Path.home() / "Documents/data" / ac_number / disk_archive_id
    
    # Arbeitsverzeichnis: 4_..._VL/files
    vl_folder = project_base_path / f"4_{disk_archive_id}_VL"
    
    # Zielverzeichnis für Logs: 5_..._LZA/logfiles
    lza_log_folder = project_base_path / f"5_{disk_archive_id}_LZA" / "logfiles"

    paths = {
        "base_directory": vl_folder / "files",
        "log_file_path": lza_log_folder / f"4_{disk_archive_id}_VL_delete-all.log",
        "preview_log_file_path": lza_log_folder / f"4_{disk_archive_id}_VL_delete-preview-all.log"
    }

    # Überprüfung des Quellverzeichnisses
    if not paths["base_directory"].is_dir():
        print(f"{Fore.RED}Fehler: Der zu bereinigende Ordner (VL) wurde nicht gefunden:\n{paths['base_directory']}{Style.RESET_ALL}")
        return None

    # Sicherstellen, dass der Log-Ordner im LZA-Verzeichnis existiert
    try:
        lza_log_folder.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"{Fore.RED}Fehler: Konnte Log-Ordner in LZA nicht erstellen: {e}{Style.RESET_ALL}")
        return None

    print(f"{Fore.GREEN}Alle Pfade wurden erfolgreich gefunden und validiert.{Style.RESET_ALL}")
    return paths

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
        print(f"{Fore.GREEN}[OK] {mode.capitalize()}-Log-Datei erfolgreich erstellt.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[FEHLER] {mode.capitalize()}-Log-Datei konnte nicht erstellt werden: {e}{Style.RESET_ALL}")

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
    """Führt den eigentlichen Löschvorgang für die übergebenen Listen durch."""
    print(f"\n{Fore.CYAN}--- Starte Löschvorgang ---{Style.RESET_ALL}")
    
    for file_path in files_to_delete:
        try:
            # 1. Versuch: Normaler Löschversuch
            os.remove(file_path)
            print(f"   {Fore.GREEN}[OK]{Style.RESET_ALL} Datei gelöscht: {file_path}")
            final_deleted_files.append(file_path)
            
            ext = next((ext for ext in DELETE_EXTENSIONS if file_path.lower().endswith(ext)), "Andere")
            extensions_counter[ext] += 1
            
        except PermissionError:
            # 2. Versuch: Wenn die Datei schreibgeschützt ist, Attribut entfernen und erneut versuchen
            try:
                os.chmod(file_path, stat.S_IWRITE)
                os.remove(file_path)
                print(f"   {Fore.GREEN}[OK]{Style.RESET_ALL} Datei gelöscht (Schreibschutz entfernt): {file_path}")
                final_deleted_files.append(file_path)
                
                ext = next((ext for ext in DELETE_EXTENSIONS if file_path.lower().endswith(ext)), "Andere")
                extensions_counter[ext] += 1
            except Exception as e2:
                print(f"   {Fore.RED}[FEHLER]{Style.RESET_ALL} Kein Zugriff auf: {file_path}")
                print(f"          Grund: Datei ist wahrscheinlich gerade in Verwendung oder eine geschützte Systemdatei. ({e2})")
                
        except Exception as e:
            print(f"   {Fore.RED}[FEHLER]{Style.RESET_ALL} Unerwarteter Fehler beim Löschen von {file_path}: {e}")

    # Ordner-Logik bleibt unverändert
    for dir_path in sorted(empty_dirs_to_delete, key=len, reverse=True):
        try:
            os.rmdir(dir_path)
            print(f"   {Fore.GREEN}[OK]{Style.RESET_ALL} Leerer Ordner gelöscht: {dir_path}")
            final_deleted_dirs.append(dir_path)
        except Exception as e:
            print(f"   {Fore.RED}[FEHLER]{Style.RESET_ALL} Fehler beim Löschen des Ordners {dir_path}: {e}")
            
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
        print(f"{Fore.RED}FEHLER: AC-Nummer und Datenträger-ID wurden nicht übergeben.{Style.RESET_ALL}")
        sys.exit(1)

    # --- ANFANG DER ERWEITERUNG: KOPIERVORGANG VON 3 NACH 4 ---
    # NEU: Verwendet den ermittelten Datenpfad statt hartcodiertem Pfad
    project_base_path = data_path_input
    source_files_path = project_base_path / f"3_{disk_archive_id_input}_for-transfer" / "files"
    target_files_path = project_base_path / f"4_{disk_archive_id_input}_VL" / "files"

    if source_files_path.is_dir():
        print(f"\n--- Vorbereitung: Kopiere Dateien von Stufe 3 nach Stufe 4 ---")
        try:
            if target_files_path.exists():
                print(f"Zielverzeichnis existiert bereits, lösche altes Verzeichnis für frischen Export...")
                shutil.rmtree(target_files_path)
            
            shutil.copytree(source_files_path, target_files_path)
            print(f"{Fore.GREEN}[OK] Files-Ordner erfolgreich von Stufe 3 nach Stufe 4 kopiert.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[FEHLER] Kopievorgang fehlgeschlagen: {e}{Style.RESET_ALL}")
            sys.exit(1)
    else:
        print(f"{Fore.RED}Fehler: Quell-Ordner in Stufe 3 nicht gefunden: {source_files_path}{Style.RESET_ALL}")
        sys.exit(1)
    # --- ENDE DER ERWEITERUNG ---

    validated_paths = setup_and_validate_paths(
        ac_number_input, 
        disk_archive_id_input,
        project_base_path_override=data_path_input
    )
    
    if validated_paths:
        base_directory = validated_paths["base_directory"]
        log_file_path = validated_paths["log_file_path"]
        preview_log_file_path = validated_paths["preview_log_file_path"]

        print(f"\nSkript wird mit folgenden Pfaden ausgeführt:\n- Zu bereinigender Ordner: {base_directory}")
        if CREATE_LOG_FILE: print(f"- Vorschau-Log (LZA): {preview_log_file_path}\n- Finales Log (LZA): {log_file_path}\n")

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
                print(f"\n{Fore.YELLOW}BITTE PRÜFEN: Eine Vorschau wurde im LZA-Logordner gespeichert.{Style.RESET_ALL}")

            if not DRY_RUN:
                confirm = input(f"\n{Fore.YELLOW}Möchten Sie den Löschvorgang in der VL-Stufe wirklich starten? (j/n): {Style.RESET_ALL}").lower()
                if confirm != 'j':
                    print(f"{Fore.YELLOW}Löschvorgang vom Benutzer abgebrochen.{Style.RESET_ALL}")
                    sys.exit(0)
            else:
                print(f"\n{Fore.YELLOW}=== TESTLAUF AKTIV ==={Style.RESET_ALL}")

            final_deleted_extensions_count = defaultdict(int)
            final_deleted_files = []
            final_deleted_dirs = []

            if DRY_RUN:
                print(f"{Fore.CYAN}--- Simulation ---{Style.RESET_ALL}")
                final_deleted_files = files_to_delete
                final_deleted_dirs = empty_dirs_to_delete
            else:
                perform_deletion(files_to_delete, empty_dirs_to_delete, final_deleted_extensions_count, final_deleted_files, final_deleted_dirs)

            if CREATE_LOG_FILE and (final_deleted_files or final_deleted_dirs):
                write_log_file(log_file_path, 'final', final_deleted_extensions_count, final_deleted_files, final_deleted_dirs)

        # Zielordner der VL-Stufe öffnen
        destination_folder = validated_paths["base_directory"].parent
        print("")
        open_folder = input(f"{Fore.YELLOW}VL-Zielordner oeffnen? (j/n): {Style.RESET_ALL}").lower()
        if open_folder == 'j':
            if sys.platform == "win32":
                os.startfile(str(destination_folder))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(destination_folder)])
            else:
                subprocess.run(["xdg-open", str(destination_folder)])
            print(f"{Fore.GREEN}Zielordner geoeffnet{Style.RESET_ALL}")

    else:
        print(f"\n{Fore.RED}[FEHLER] Skript wird aufgrund von Konfigurationsfehlern beendet.{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}Skript beendet.{Style.RESET_ALL}")