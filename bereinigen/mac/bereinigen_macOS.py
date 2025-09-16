import os

# Basisverzeichnis
base_directory = "/Users/gregorneuboeck/Desktop/ZPH1082_011_Eisendle"

# Schlüsselwörter für gezielte Löschung nach Dateinamen
delete_keywords = [
    "video_konvertierung",
    "konvertierungslog",
    "konvertierungslog_praesentation_tabelle",
    "konvertierungslog_html_mht",
    "bereinigungslog"
]

# Typische versteckte macOS-Dateien
mac_hidden_files = [
    ".DS_Store",
    ".Spotlight-V100",
    ".Trashes",
    ".fseventsd",
    ".TemporaryItems",
    ".VolumeIcon.icns"
]

# Zu löschende Dateiendungen (Groß-/Kleinschreibung ignorieren)
delete_extensions = [
    ".001", ".030", ".2gr", ".3gr", ".abk", ".acl", ".acm", ".acs", ".agd", ".alt", ".ani", ".ann", ".ax", ".bak", ".bat", ".bin", ".bmt", ".bof", ".bpl", ".cab", "cal", ".cat", ".cbd", ".cb", ".cbk", ".cfg", ".chk", ".chl", ".chm", ".chw", ".class", ".clb", ".clp", ".cnt", ".cnf", ".cnv", ".com", ".cov", ".cpe", ".cpi", ".cpl", ".cpx", ".crd", ".crl", ".cur", ".ctx", ".dat", ".db", ".dbs", ".dls", ".ds", ".dsz", ".dct", ".desklink", ".dfv", ".dic", ".dka", ".dki",
    ".dll", ".dmp", ".dsc", ".dr_", ".p01", ".ecf", ".ecw", ".ess", ".exc", ".ass", ".env", ".evt", ".exe", ".fcs", ".fi", ".flg", ".flt", ".fnt", ".fon", ".for", ".fot", ".fsd", ".fsi", ".gid", ".grd", ".grt", ".grp", ".he4", ".hic", ".him", ".hti", ".hlp", ".hpm", ".htt", ".htx", ".htz", ".hyp", ".icm", ".ico", ".id", ".idf", ".idx", ".inf", ".ini", ".ink", ".ins", ".in2", ".isr", ".isu", ".iwa", ".job", ".jpg^", ".ki", ".krn", ".ku4",
    ".last", ".lex", ".lgo", ".lib", ".liveupdate", ".ld", ".lnk", ".log", ".lst", ".lwa", ".m2v", ".mad", ".MAPIMail", ".mdb", ".ml", ".ms", ".msi", ".msc", ".msg", ".mbx", ".mbox", ".mod", ".mtm", ".mydocs", "._mp", ".nch", ".net", ".nls", ".nt", ".ns", ".olb", ".old", ".ocx", ".osd", ".ovl", ".pal", ".par", ".p01", ".p02", ".p03", ".pbk", ".pci", ".pco", ".pdr", ".pgm", ".pfm", ".pfb", ".pif", ".pip", ".pkg", ".plx", ".pnf", ".pol", ".pr4", ".pro", ".prx", ".ps2", ".ptm", ".pwl", ".qlc", ".qdat", ".qtp", ".qtr", ".qts", ".qtx", ".ra4", ".rat", ".rbk", ".reg", ".rle", ".rsc", ".sav", ".sca", ".scn", ".scf", ".scr", ".sdw", ".set", ".sf0", ".sfc", ".shx", ".sik", ".skp", ".sob", ".spd", ".swx", ".sys",
    ".sdb", ".sig", ".slt", ".smm", ".sol", ".spc", ".ss", ".stb", ".stt", ".sts", ".str", ".sty", ".syd", ".tab", ".t", ".tbs", ".temp", ".tbl", ".ths", ".tlb", ".tmp", ".tsc", ".tsk", ".ttf", ".ttx", ".tsp", ".tys", ".tyq", ".uce", ".url", ".umb", ".utf", ".vbx", ".vid", ".vue", ".vxd", ".wab", ".wa~", ".wbk", ".wbm", ".wlx", ".wof", ".w31", ".xml.pdf", ".x32", ".000", ".386", ".zip"
]

def delete_unwanted_files_and_empty_dirs(base_dir):
    for root, dirs, files in os.walk(base_dir, topdown=False):
        for filename in files:
            file_path = os.path.join(root, filename)
            lower_filename = filename.lower()

            # Bedingungen für Löschung
            if (
                filename in mac_hidden_files or
                filename.startswith("._") or
                filename.startswith('.') or
                filename.startswith('~') or  # <<< HIER IST DIE NEUE ZEILE
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
delete_unwanted_files_and_empty_dirs(base_directory)