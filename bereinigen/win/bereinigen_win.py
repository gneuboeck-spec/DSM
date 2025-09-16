import os
import sys

# --- KONFIGURATION (Für Windows 11 anpassen) ---

# 1. Geben Sie hier den Pfad zum Ordner ein, der bereinigt werden soll.
#    Verwenden Sie normale Slashes (/), Python wandelt sie korrekt um.
base_directory = "C:/Users/digit/Desktop/ZPH1082_011_Eisendle"

# 2. Schlüsselwörter für gezielte Löschung nach Dateinamen (unverändert)
delete_keywords = [
    "video_konvertierung",
    "konvertierungslog",
    "konvertierungslog_praesentation_tabelle",
    "konvertierungslog_html_mht",
    "bereinigungslog"
]

# 3. Typische versteckte Systemdateien (für Windows angepasst)
system_hidden_files = [
    "Thumbs.db",    # Windows-Vorschaubilder-Cache
    "desktop.ini"   # Windows-Ordnerkonfiguration
]

# 4. Zu löschende Dateiendungen (unverändert)
delete_extensions = [
    ".001", ".030", ".2gr", ".3gr", ".abk", ".acl", ".acm", ".acs", ".agd", ".alt", ".ani", ".ann", ".ax", ".bak", ".bat", ".bin", ".bmt", ".bof", ".bpl", ".cab", "cal", ".cat", ".cbd", ".cb", ".cbk", ".cfg", ".chk", ".chl", ".chm", ".chw", ".class", ".clb", ".clp", ".cnt", ".cnf", ".cnv", ".com", ".cov", ".cpe", ".cpi", ".cpl", ".cpx", ".crd", ".crl", ".cur", ".ctx", ".dat", ".db", ".dbs", ".dls", ".ds", ".dsz", ".dct", ".desklink", ".dfv", ".dic", ".dka", ".dki",
    ".dll", ".dmp", ".dsc", ".dr_", ".drv", ".p01", ".ecf", ".ecw", ".ess", ".exc", ".ass", ".env", ".evt", ".exe", ".fcs", ".fi", ".flg", ".flt", ".fnt", ".fon", ".for", ".fot", ".fsd", ".fsi", ".gid", ".grd", ".grt", ".grp", ".he4", ".hic", ".him", ".hti", ".hlp", ".hpm", ".htt", ".htx", ".htz", ".hyp", ".icm", ".ico", ".id", ".idf", ".idx", ".inf", ".ini", ".ink", ".ins", ".in2", ".isr", ".isu", ".iwa", ".job", ".jpg^", ".ki", ".krn", ".ku4",
    ".last", ".lex", ".lgo", ".lib", ".liveupdate", ".ld", ".lnk", ".log", ".lst", ".lwa", ".m2v", ".mad", ".MAPIMail", ".mdb", ".ml", ".ms", ".msi", ".msc", ".msg", ".mbx", ".mbox", ".mod", ".mtm", ".mydocs", "._mp", ".nch", ".net", ".nls", ".nt", ".ns", ".olb", ".old", ".ocx", ".osd", ".ovl", ".pal", ".par", ".p01", ".p02", ".p03", ".pbk", ".pci", ".pco", ".pdr", ".pgm", ".pfm", ".pfb", ".pif", ".pip", ".pkg", ".plx", ".pnf", ".pol", ".pr4", ".pro", ".prx", ".ps2", ".ptm", ".pwl", ".qlc", ".qdat", ".qtp", ".qtr", ".qts", ".qtx", ".ra4", ".rat", ".rbk", ".reg", ".rle", ".rsc", ".sav", ".sca", ".scn", ".scf", ".scr", ".sdw", ".set", ".sf0", ".sfc", ".shx", ".sik", ".skp", ".sob", ".spd", ".swx", ".sys",
    ".sdb", ".sig", ".slt", ".smm", ".sol", ".spc", ".ss", ".stb", ".stt", ".sts", ".str", ".sty", ".syd", ".tab", ".t", ".tbs", ".temp", ".tbl", ".ths", ".tlb", ".tmp", ".tsc", ".tsk", ".ttf", ".ttx", ".tsp", ".tys", ".tyq", ".uce", ".url", ".umb", ".utf", ".vbx", ".vid", ".vue", ".vxd", ".wab", ".wa~", ".wbk", ".wbm", ".wlx", ".wof", ".w31", ".xml.pdf", ".x32", ".000", ".386", ".zip"
]
# --- ENDE DER KONFIGURATION ---


# Ersetze "IhrBenutzername" im Pfad, falls es noch der Platzhalter ist
if "IhrBenutzername" in base_directory:
    print("="*60)
    print("BITTE BEARBEITEN SIE DAS SKRIPT!")
    print("Ersetzen Sie 'IhrBenutzername' in der Variable 'base_directory' mit Ihrem tatsächlichen Windows-Benutzernamen.")
    print("="*60)
    sys.exit(1)


def delete_unwanted_files_and_empty_dirs(base_dir):
    for root, dirs, files in os.walk(base_dir, topdown=False):
        for filename in files:
            file_path = os.path.join(root, filename)
            lower_filename = filename.lower()

            # Angepasste Bedingungen für Windows
            # Die Prüfungen auf '._' und '.'-Dateien sind für plattformübergreifende Sauberkeit beibehalten.
            if (
                lower_filename in system_hidden_files or
                filename.startswith("._") or
                (filename.startswith('.') and filename not in ['.git', '.gitignore']) or # Git-Dateien explizit schützen
                filename.startswith('~') or
                any(keyword in lower_filename for keyword in delete_keywords) or
                any(lower_filename.endswith(ext) for ext in delete_extensions)
            ):
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
                    os.rmdir(dir_path)
                    print(f"[OK] Leerer Ordner gelöscht: {dir_path}")
            except Exception as e:
                print(f"[FEHLER] Fehler beim Löschen des Ordners {dir_path}: {e}")

# Ausführung
if __name__ == "__main__":
    if not os.path.isdir(base_directory):
        print(f"FEHLER: Der angegebene Ordner existiert nicht: {base_directory}")
        sys.exit(1)
    delete_unwanted_files_and_empty_dirs(base_directory)