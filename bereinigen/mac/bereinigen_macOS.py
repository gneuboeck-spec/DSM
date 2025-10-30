# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import sys
from collections import defaultdict

# --- KONFIGURATION ---

# 1. Geben Sie hier den Pfad zum Ordner ein, der bereinigt werden soll.
base_directory = "/Users/gregorneuboeck/Desktop/ZPH1082_011_Eisendle"

# 2. TRUE/FALSE-SCHALTER FÜR TESTLAUF
#    True:  Nur anzeigen, welche Dateien/Ordner gelöscht würden.
#    False: Dateien und Ordner tatsächlich löschen.
dry_run = True

# 3. LOG-DATEI ERSTELLEN
#    True:  Erstellt eine Log-Datei mit einer Zusammenfassung der Dateitypen.
#    False: Erstellt keine Log-Datei.
create_log_file = True
log_file_name = "bereinigungs_report_macos.txt"  # Name der Log-Datei

# 4. Schlüsselwörter für gezielte Löschung nach Dateinamen
delete_keywords = [
    "video_konvertierung",
    "konvertierungslog",
    "konvertierungslog_praesentation_tabelle",
    "konvertierungslog_html_mht",
    "bereinigungslog"
]

# 5. Typische versteckte macOS-Dateien
mac_hidden_files = [
    ".DS_Store",
    ".Spotlight-V100",
    ".Trashes",
    ".fseventsd",
    ".TemporaryItems",
    ".VolumeIcon.icns"
]

# 6. Zu löschende Dateiendungen (Groß-/Kleinschreibung ignorieren)
delete_extensions = [
    ".001", ".030", ".2gr", ".3gr", ".abk", ".acl", ".acm", ".acs", ".agd", ".alt", ".ani", ".ann", ".ax", ".bak", ".bat", ".bin", ".bmt", ".bof", ".bpl", ".cab", "cal", ".cat", ".cbd", ".cb", ".cbk", ".cfg", ".chk", ".chl", ".chm", ".chw", ".class", ".clb", ".clp", ".cnt", ".cnf", ".cnv", ".com", ".cov", ".cpe", ".cpi", ".cpl", ".cpx", ".crd", ".crl", ".cur", ".ctx", ".dat", ".db", ".dbs", ".dls", ".ds", ".dsz", ".dct", ".desklink", ".dfv", ".dic", ".dka", ".dki",
    ".dll", ".dmp", ".dsc", ".dr_", ".p01", ".ecf", ".ecw", ".ess", ".exc", ".ass", ".env", ".evt", ".exe", ".fcs", ".fi", ".flg", ".flt", ".fnt", ".fon", ".for", ".fot", ".fsd", ".fsi", ".gid", ".grd", ".grt", ".grp", ".he4", ".hic", ".him", ".hti", ".hlp", ".hpm", ".htt", ".htx", ".htz", ".hyp", ".icm", ".ico", ".id", ".idf", ".idx", ".inf", ".ini", ".ink", ".ins", ".in2", ".isr", ".isu", ".iwa", ".job", ".jpg^", ".ki", ".krn", ".ku4",
    ".last", ".lex", ".lgo", ".lib", ".liveupdate", ".ld", ".lnk", ".log", ".lst", ".lwa", ".m2v", ".mad", ".MAPIMail", ".mdb", ".ml", ".ms", ".msi", ".msc", ".msg", ".mbx", ".mbox", ".mod", ".mtm", ".mydocs", "._mp", ".nch", ".net", ".nls", ".nt", ".ns", ".olb", ".old", ".ocx", ".osd", ".ovl", ".pal", ".par", ".p01", ".p02", ".p03", ".pbk", ".pci", ".pco", ".pdr", ".pgm", ".pfm", ".pfb", ".pif", ".pip", ".pkg", ".plx", ".pnf", ".pol", ".pr4", ".pro", ".prx", ".ps2", ".ptm", ".pwl", ".qlc", ".qdat", ".qtp", ".qtr", ".qts", ".qtx", ".ra4", ".rat", ".rbk", ".reg", ".rle", ".rsc", ".sav", ".sca", ".scn", ".scf", ".scr", ".sdw", ".set", ".sf0", ".sfc", ".shx", ".sik", ".skp", ".sob", ".spd", ".swx", ".sys",
    ".sdb", ".sig", ".slt", ".smm", ".sol", ".spc", ".ss", ".stb", ".stt", ".sts", ".str", ".sty", ".syd", ".tab", ".t", ".tbs", ".temp", ".tbl", ".ths", ".tlb", ".tmp", ".tsc", ".tsk", ".ttf", ".ttx", ".tsp", ".tys", ".tyq", ".uce", ".url", ".umb", ".utf", ".vbx", ".vid", ".vue", ".vxd", ".wab", ".wa~", ".wbm", ".wlx", ".wof", ".w31", ".xml.pdf", ".x32", ".000", ".386", ".zip"
]
# --- ENDE DER KONFIGURATION ---


def write_log_file(log_path, extensions_counter):
    """Schreibt die Zusammenfassung der Dateitypen in eine Log-Datei."""
    print(f"\nErstelle Log-Datei: {log_path}")
    try:
        # Sortiere die Einträge nach Anzahl (absteigend)
        sorted_items = sorted(extensions_counter.items(), key=lambda item: item[1], reverse=True)

        with open(log_path, 'w', encoding='utf-8') as f:
            f.write("Anzahl und Typ der zu löschenden Dateien\n")
            f.write("========================================\n")

            if not sorted_items:
                f.write("Keine Dateien mit den angegebenen Endungen gefunden.\n")
            else:
                for ext, count in sorted_items:
                    f.write(f"{count}\t{ext}\n")
        print("[OK] Log-Datei erfolgreich erstellt.")
    except Exception as e:
        print(f"[FEHLER] Log-Datei konnte nicht erstellt werden: {e}")


def delete_unwanted_files_and_empty_dirs(base_dir, is_dry_run, extensions_counter):
    """
    Durchsucht ein Verzeichnis und löscht unerwünschte Dateien und leere Unterordner.
    Zählt dabei die Dateiendungen für den Log.
    """
    action_prefix = "[Testlauf] " if is_dry_run else ""

    for root, dirs, files in os.walk(base_dir, topdown=False):
        for filename in files:
            file_path = os.path.join(root, filename)
            lower_filename = filename.lower()

            # Prüfen, ob die Datei aufgrund ihrer Endung gelöscht werden soll
            matched_ext = None
            for ext in delete_extensions:
                if lower_filename.endswith(ext):
                    matched_ext = ext
                    break

            # Gesamtbedingung für das Löschen (macOS-spezifisch)
            should_delete = (
                filename in mac_hidden_files or
                filename.startswith("._") or
                (filename.startswith('.') and filename not in ['.git', '.gitignore']) or # Schützt Git-Dateien
                filename.startswith('~') or
                any(keyword in lower_filename for keyword in delete_keywords) or
                matched_ext is not None
            )

            if should_delete:
                # Nur wenn die Löschung aufgrund einer Endung erfolgt, für den Report zählen
                if matched_ext:
                    extensions_counter[matched_ext] += 1
                
                if is_dry_run:
                    print(f"{action_prefix}Datei würde gelöscht: {file_path}")
                else:
                    try:
                        os.remove(file_path)
                        print(f"[OK] Datei gelöscht: {file_path}")
                    except Exception as e:
                        print(f"[FEHLER] Fehler beim Löschen {file_path}: {e}")

        # Leere Verzeichnisse entfernen
        for dirname in dirs:
            dir_path = os.path.join(root, dirname)
            try:
                if not os.listdir(dir_path):
                    if is_dry_run:
                        print(f"{action_prefix}Leerer Ordner würde gelöscht: {dir_path}")
                    else:
                        os.rmdir(dir_path)
                        print(f"[OK] Leerer Ordner gelöscht: {dir_path}")
            except Exception as e:
                print(f"[FEHLER] Fehler beim Löschen des Ordners {dir_path}: {e}")


# --- Skriptausführung ---
if __name__ == "__main__":
    # Optional: Ein Platzhalter-Check, falls das Skript geteilt wird
    if "/IhrBenutzername/" in base_directory:
        print("""
============================================================
BITTE BEARBEITEN SIE DAS SKRIPT!
Ersetzen Sie 'IhrBenutzername' im Pfad 'base_directory'.
============================================================
""")
        sys.exit(1)

    if not os.path.isdir(base_directory):
        print(f"FEHLER: Der angegebene Ordner existiert nicht: {base_directory}")
        sys.exit(1)

    if dry_run:
        print("""
============================================================
=== TESTLAUF AKTIV ===
Es werden keine Dateien gelöscht, nur Aktionen simuliert.
============================================================
""")

    # Zähler für die Dateitypen initialisieren
    deleted_extensions_count = defaultdict(int)

    # Hauptfunktion ausführen
    delete_unwanted_files_and_empty_dirs(base_directory, dry_run, deleted_extensions_count)

    # Log-Datei erstellen, wenn aktiviert und Zähler nicht leer ist
    if create_log_file and deleted_extensions_count:
        log_file_path = os.path.join(base_directory, log_file_name)
        write_log_file(log_file_path, deleted_extensions_count)

    print("\nSkriptdurchlauf beendet.")