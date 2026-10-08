# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import sys
import shutil
import bagit
import time
import tarfile
import glob
from datetime import datetime
from pathlib import Path

# Colorama für Statusmeldungen
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class Fore: GREEN = RED = YELLOW = CYAN = MAGENTA = WHITE = ""
    class Style: RESET_ALL = ""

def compress_and_remove_folder(folder_path: Path, output_name: str):
    """
    Hilfsfunktion: Komprimiert einen spezifischen Ordner zu .tar.gz und löscht den Originalordner.
    """
    if folder_path.exists() and folder_path.is_dir():
        print(f"{Fore.CYAN} -> Komprimiere: {folder_path.name}")
        output_path = folder_path.parent / output_name
        
        # w:gz steht für write + gzip Komprimierung
        with tarfile.open(output_path, "w:gz") as tar:
            # arcname sorgt dafür, dass im Archiv nur der Ordnername als Wurzel liegt
            tar.add(folder_path, arcname=folder_path.name)
            
        print(f"{Fore.GREEN}    [OK] Archiv erstellt: {output_name}")
        print(f"{Fore.YELLOW}    -> Lösche unkomprimierten Originalordner zur Speicherplatzfreigabe...")
        shutil.rmtree(folder_path)
        print(f"{Fore.GREEN}    [OK] Originalordner erfolgreich gelöscht.")
    else:
        print(f"{Fore.YELLOW}    [INFO] Ordner nicht gefunden, Komprimierung übersprungen: {folder_path}")

def run_final_archiving(ac_number, disk_id, project_base_path_override=None):
    """
    0. Komprimiert NUR den Brunnhilde-Unterordner zu .tar.gz (Speicherplatz-Optimierung)
    1. Erstellt BagIt (verschiebt alles nach data/, inkl. der neuen .tar.gz Datei)
    2. Belässt Master-Index in data/logfiles/ (kein Verschieben ins Root mehr)
    3. Aktualisiert BagIt Manifeste (SHA-256 für die neuen Dateien)
    4. BENENNT den Ordner von 5_..._LZA in nur noch ... (disk_id) um.
    5. Löscht alte Stufen 0-3 (VL bleibt erhalten)
    """
    # NEU: Wenn ein Pfad aus dem Menü übergeben wurde, nutzen wir diesen direkt als Basis.
    if project_base_path_override:
        disk_path = Path(project_base_path_override)
    else:
        base_root = Path(r"C:\Users\digit\Documents\data")
        disk_path = base_root / ac_number / disk_id
        
    f5_lza = disk_path / f"5_{disk_id}_LZA"
    f4_vl = disk_path / f"4_{disk_id}_VL"
    
    # Dateinamen definieren
    master_index_name = f"5_{disk_id}_LZA.index"
    premis_name = f"5_{disk_id}_LZA_premis.xml"

    print(f"\n{Fore.MAGENTA}===================================================")
    print(f"{Fore.WHITE}   FINALISIERUNG: BAGIT (mit Teil-Komprimierung)")
    print(f"{Fore.MAGENTA}==================================================={Fore.RESET}")

    if not f5_lza.exists():
        print(f"{Fore.RED}[FEHLER] Ordner {f5_lza.name} nicht gefunden!")
        return

    # Sicherheits-Check
    print(f"{Fore.YELLOW}[!] HINWEIS: Explorer-Fenster von {f5_lza.name} schliessen.")
    if input(" Komprimierung, Bagging und Archivierung jetzt starten? (j/n): ").lower() != 'j': 
        return

    try:
        # --- SCHRITT 0: GEZIELTE SPEICHERPLATZ-OPTIMIERUNG (VOR BAGIT) ---
        print(f"\n{Fore.CYAN}--- SCHRITT 0: Gezielte Komprimierung des Brunnhilde-Ordners ---")
        
        # NUR der spezifische Unterordner in 'logfiles' wird komprimiert
        brunnhilde_folder = f5_lza / "logfiles" / f"2_{disk_id}_extracted-files_brunnhilde"
        compress_and_remove_folder(brunnhilde_folder, f"2_{disk_id}_extracted-files_brunnhilde.tar.gz")
        
        print(f"{Fore.GREEN} [OK] Schritt 0 abgeschlossen. BagIt wird nun mit dem komprimierten Archiv erstellt.")

        # --- SCHRITT 1: BAGIT ERSTELLEN ---
        print(f"\n{Fore.CYAN}--- SCHRITT 1: BagIt-Container erstellen ---")
        metadata = {
            'Contact-Name': 'Datenrettung Digit',
            'ZPH-ID': disk_id,
            'External-Identifier': ac_number
        }
        # Erstellt den Bag (Inhalt wandert nach data/, inkl. der soeben erstellten .tar.gz Datei)
        bag = bagit.make_bag(str(f5_lza), metadata, checksums=['sha256'])
        print(f"{Fore.GREEN} [OK] Basis-Bag erstellt.")

        # --- SCHRITT 2: MASTER-INDEX IN DATA/LOGFILES BELASSEN ---
        print(f"\n{Fore.CYAN}--- SCHRITT 2: Master-Index Position prüfen ---")
        
        expected_index_path = f5_lza / "data" / "logfiles" / master_index_name
        if expected_index_path.exists():
            print(f"{Fore.GREEN} [OK] Master-Index '{master_index_name}' verbleibt korrekt in data/logfiles/.")
        else:
            print(f"{Fore.YELLOW} [!] Hinweis: Master-Index '{master_index_name}' nicht in data/logfiles/ gefunden.")

        # --- SCHRITT 3: BAGIT AKTUALISIEREN ---
        print(f"\n{Fore.CYAN}--- SCHRITT 3: BagIt Manifeste aktualisieren ---")
        # BagIt berechnet nun die SHA-256 Prüfsummen für die neuen Dateien (z.B. .tar.gz)
        bag.save(manifests=True) 
        print(f"{Fore.GREEN} [OK] BagIt-Prüfsummen (SHA-256) aktualisiert.")

        # --- SCHRITT 4: ORDNER UMBENENNEN (5_..._LZA -> disk_id) ---
        print(f"\n{Fore.CYAN}--- SCHRITT 4: Archiv-Ordner final umbenennen ---")
        final_archive_path = disk_path / disk_id
        
        if f5_lza.exists() and not final_archive_path.exists():
            print(f"{Fore.YELLOW}    Benenne '{f5_lza.name}' um in '{disk_id}'...")
            f5_lza.rename(final_archive_path)
            print(f"{Fore.GREEN}    [OK] Ordner erfolgreich in '{disk_id}' umbenannt.")
            # Variable aktualisieren, damit die folgenden Meldungen den neuen Namen verwenden
            f5_lza = final_archive_path
        elif final_archive_path.exists():
            print(f"{Fore.YELLOW}    [WARNUNG] Zielordner '{final_archive_path.name}' existiert bereits. Umbenennung übersprungen.")
        
        print(f"{Fore.GREEN} [INFO] Der BagIt-Ordner ({f5_lza.name}) ist nun das fertige Archiv (AIP).")

        # --- SCHRITT 5: ALTE STUFEN 0-3 LÖSCHEN (VL STUFE 4 BLEIBT) ---
        print(f"\n{Fore.CYAN}--- SCHRITT 5: Alte Stufen 0-3 bereinigen ---")
        
        stages_to_delete = [
            f"0_{disk_id}_picture-carrier",
            f"1_{disk_id}_image-LZA",
            f"2_{disk_id}_extracted-files",
            f"3_{disk_id}_for-transfer"
        ]
        
        deleted_count = 0
        for stage_name in stages_to_delete:
            stage_path = disk_path / stage_name
            if stage_path.exists():
                try:
                    shutil.rmtree(stage_path)
                    print(f"{Fore.GREEN} [Cleanup] Gelöscht: {stage_name}")
                    deleted_count += 1
                except Exception as e:
                    print(f"{Fore.YELLOW} [WARNUNG] Konnte {stage_name} nicht löschen (z.B. durch offene Datei): {e}")
            else:
                print(f"{Fore.CYAN} [Info] {stage_name} existiert nicht (bereits gelöscht).")
        
        if f4_vl.exists():
            print(f"{Fore.CYAN} [Info] VL-Stufe (4_{disk_id}_VL) bleibt als Arbeitskopie erhalten.")
        
        print(f"{Fore.GREEN} [Cleanup] {deleted_count} von {len(stages_to_delete)} alten Stufen gelöscht.")

        print(f"\n{Fore.GREEN}===================================================")
        print(f" ARCHIVIERUNG ERFOLGREICH ABGESCHLOSSEN")
        print(f"==================================================={Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED} [!] KRITISCHER FEHLER: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        ac_number = sys.argv[1]
        disk_id = sys.argv[2]
        
        # NEU: Datenpfad aus menu.py übernehmen (sys.argv[3] oder Umgebungsvariable DATA_PATH)
        if len(sys.argv) >= 4:
            data_path_input = Path(sys.argv[3])
        else:
            env_path = os.environ.get("DATA_PATH")
            if env_path:
                data_path_input = Path(env_path)
            else:
                data_path_input = Path(r"C:\Users\digit\Documents\data") / ac_number / disk_id
                
        run_final_archiving(ac_number, disk_id, project_base_path_override=data_path_input)
    else:
        print(f"{Fore.RED}Fehler: AC-Nummer und ID fehlen. Aufruf: script.py <AC_NUMMER> <DISK_ID>")