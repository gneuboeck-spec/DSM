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

def run_final_archiving(ac_number, disk_id):
    """
    0. Komprimiert NUR den Brunnhilde-Unterordner zu .tar.gz (Speicherplatz-Optimierung)
    1. Erstellt BagIt (verschiebt alles nach data/, inkl. der neuen .tar.gz Datei)
    2. Verschiebt Master-Index ins Bag-Root (Tag-File)
    3. Generiert mets.xml im Bag-Root (Tag-File)
    4. Aktualisiert BagIt Manifeste (SHA-256 für die neuen Dateien)
    5. Der Ordner 5_..._LZA bleibt als fertiges BagIt-Archiv (AIP) erhalten.
    6. Löscht alte Stufen 0-3 (VL bleibt erhalten)
    """
    base_root = Path(r"C:\Users\digit\Documents\data")
    disk_path = base_root / ac_number / disk_id
    f5_lza = disk_path / f"5_{disk_id}_LZA"
    f4_vl = disk_path / f"4_{disk_id}_VL"
    
    # Dateinamen definieren
    master_index_name = f"5_{disk_id}_LZA.index"
    premis_name = f"5_{disk_id}_LZA_premis.xml"

    print(f"\n{Fore.MAGENTA}===================================================")
    print(f"{Fore.WHITE}   FINALISIERUNG: BAGIT & METS (mit Teil-Komprimierung)")
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

        # --- SCHRITT 2: MASTER-INDEX AN DAS ROOT VERSCHIEBEN ---
        print(f"\n{Fore.CYAN}--- SCHRITT 2: Master-Index als Tag-File positionieren ---")
        
        index_source_path = None
        for p in (f5_lza / "data").rglob(master_index_name):
            index_source_path = p
            break
        
        if index_source_path and index_source_path.exists():
            final_index_path = f5_lza / master_index_name
            shutil.move(str(index_source_path), str(final_index_path))
            print(f"{Fore.GREEN} [OK] Master-Index verschoben nach: {final_index_path.name}")
        else:
            print(f"{Fore.RED} [!] Master-Index '{master_index_name}' nicht in data/ gefunden!")

        # --- SCHRITT 3: METS GENERIEREN ---
        print(f"\n{Fore.CYAN}--- SCHRITT 3: METS-Datei generieren ---")
        
        mets_index_path = master_index_name
        mets_premis_path = f"data/logfiles/{premis_name}"
        
        mets_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<mets xmlns="http://www.loc.gov/METS/" xmlns:xlink="http://www.w3.org/1999/xlink" OBJID="{ac_number}_{disk_id}">
    <dmdSec ID="DMD_0001">
        <mdRef LOCTYPE="URL" MDTYPE="OTHER" OTHERMDTYPE="MASTER-INDEX" xlink:href="{mets_index_path}" />
    </dmdSec>
    <amdSec>
        <techMD ID="TMD_0001">
            <mdRef LOCTYPE="URL" MDTYPE="PREMIS" xlink:href="{mets_premis_path}" />
        </techMD>
    </amdSec>
    <fileSec><fileGrp USE="Content"><file ID="BAG_0001"><FLocat LOCTYPE="URL" xlink:href="data/" /></file></fileGrp></fileSec>
    <structMap TYPE="physical"><div TYPE="AIP" LABEL="{disk_id}"><div TYPE="VOLUME" DMDID="DMD_0001" ADMID="TMD_0001"><fptr FILEID="BAG_0001"/></div></div></structMap>
</mets>'''
        
        mets_file_path = f5_lza / "mets.xml"
        with open(mets_file_path, "w", encoding="utf-8") as f:
            f.write(mets_content)
        print(f"{Fore.GREEN} [OK] mets.xml im Bag-Root erstellt.")

        # --- SCHRITT 4: BAGIT AKTUALISIEREN ---
        print(f"\n{Fore.CYAN}--- SCHRITT 4: BagIt Manifeste aktualisieren ---")
        # BagIt berechnet nun die SHA-256 Prüfsummen für die .tar.gz Datei und die mets.xml
        bag.save(manifests=True) 
        print(f"{Fore.GREEN} [OK] BagIt-Prüfsummen (SHA-256) aktualisiert.")

        # --- SCHRITT 5: ABSCHLUSS-CHECK ---
        print(f"\n{Fore.CYAN}--- SCHRITT 5: Abschluss-Check ---")
        print(f"{Fore.GREEN} [INFO] Der BagIt-Ordner ({f5_lza.name}) bleibt als fertiges Archiv (AIP) bestehen.")

        # --- SCHRITT 6: ALTE STUFEN 0-3 LÖSCHEN (VL STUFE 4 BLEIBT) ---
        print(f"\n{Fore.CYAN}--- SCHRITT 6: Alte Stufen 0-3 bereinigen ---")
        
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
        run_final_archiving(sys.argv[1], sys.argv[2])
    else:
        print(f"{Fore.RED}Fehler: AC-Nummer und ID fehlen. Aufruf: script.py <AC_NUMMER> <DISK_ID>")