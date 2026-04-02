import os
import sys
import shutil
import bagit
import time
import tarfile
from datetime import datetime
from pathlib import Path

def run_lza_bagging(ac_number, disk_id):
    """
    Sammelt Dateien, erstellt einen BagIt-Container, verpackt diesen in ein TAR 
    und bereinigt abschließend den temporären Bag-Ordner.
    """
    # --- BASIS-KONFIGURATION ---
    base_root = Path(r"C:\Users\digit\Documents\data")
    disk_path = base_root / ac_number / disk_id

    # Pfade definieren
    folder_0 = disk_path / f"0_{disk_id}_picture-carrier"
    folder_1 = disk_path / f"1_{disk_id}_image-LZA"
    folder_2 = disk_path / f"2_{disk_id}_extracted-files"
    folder_3 = disk_path / f"3_{disk_id}_for-transfer"
    folder_5 = disk_path / f"5_{disk_id}_LZA" 

    print(f"\n===================================================")
    print(f" LZA-ARCHIVIERUNG, BAGIT & TAR-PACKER")
    print(f"===================================================")
    print(f"AC-Nummer:  {ac_number}")
    print(f"ZPH-ID:     {disk_id}")
    print(f"---------------------------------------------------")

    # --- NEU: SICHERHEITS-CHECK FÜR EXPLORER ---
    print(f"\n [!] WICHTIGER HINWEIS:")
    print(f" Damit BagIt den Ordner '{folder_5.name}' verarbeiten kann,")
    print(f" MÜSSEN alle Windows-Explorer-Fenster geschlossen sein,")
    print(f" die diesen Ordner oder seine Unterordner anzeigen.")
    print(f" (Ansonsten droht ein 'Zugriff verweigert' Fehler)")
    
    confirm_explorer = input(f"\n Sind alle Explorer-Fenster geschlossen? (j/n): ").lower()
    if confirm_explorer != 'j':
        print("\n Abbruch durch Benutzer. Bitte Fenster schließen und neu starten.")
        return

    if not folder_5.exists():
        print(f"\nFEHLER: Zielordner {folder_5} wurde nicht gefunden!")
        return

    def safe_move(src, dest_dir):
        """Verschiebt Dateien/Ordner tolerant und gibt Rückmeldung."""
        if src.exists():
            try:
                target = dest_dir / src.name
                if target.exists():
                    if target.is_dir(): shutil.rmtree(target)
                    else: os.remove(target)
                
                shutil.move(str(src), str(dest_dir))
                print(f" [OK] Verschoben: {src.name}")
                return True
            except Exception as e:
                print(f" [!] FEHLER beim Verschieben von {src.name}: {e}")
                return False
        else:
            # Hier ist die gewünschte Rückmeldung für nicht gefundene Dateien
            print(f" [-] ÜBERSPRUNGEN: {src.name} (Datei/Ordner nicht vorhanden)")
            return False

    # --- SCHRITT 1: DATEIEN IN ORDNER 5 ZUSAMMENFÜHREN ---
    print("\nSammle vorhandene Daten in Ordner 5...")
    
    # A) Ganze Ordner 0 und 1
    safe_move(folder_0, folder_5)
    safe_move(folder_1, folder_5)

    # B) Dateien/Ordner aus Ordner 2
    files_from_2 = [
        f"2_{disk_id}_extracted-files.content",
        f"2_{disk_id}_extracted-files_brunnhilde-summary.json",
        f"2_{disk_id}_extracted-files_tree.txt",
        f"2_{disk_id}_extracted-files_brunnhilde"
    ]
    for item in files_from_2:
        safe_move(folder_2 / item, folder_5)

    # C) Dateien aus Ordner 3
    files_from_3 = [
        f"3_{disk_id}_for-transfer.index",
        f"3_{disk_id}_for-transfer_all-conversions.log",
        f"3_{disk_id}_for-transfer_delete-all.log",
        f"3_{disk_id}_for-transfer_delete-converted-odfs.log",
        f"3_{disk_id}_for-transfer_delete-converted-wavs.log",
        f"3_{disk_id}_for-transfer_delete-preview-all.log",
        f"3_{disk_id}_for-transfer_repair-file-extension.log"
    ]
    for item in files_from_3:
        safe_move(folder_3 / item, folder_5)

    # --- SCHRITT 2: KURZE PAUSE ---
    # Hilft Windows, Dateihandles wirklich freizugeben
    time.sleep(2)

    # --- SCHRITT 3: BAGIT ERSTELLEN ---
    print(f"\nStarte BagIt-Erstellung...")
    metadata = {
        'Contact-Name': 'Datenrettung Digit',
        'Source-Organization': 'Digit Lab',
        'External-Identifier': ac_number,
        'ZPH-ID': disk_id,
        'Internal-Sender-Description': f"LZA-Paket fuer {disk_id}"
    }

    try:
        bag = bagit.make_bag(str(folder_5), metadata, checksums=['sha256'])
        
        if bag.validate():
            print(f" [OK] BagIt-Container erfolgreich validiert.")
            
            # --- SCHRITT 4: TAR-ARCHIV ERSTELLEN ---
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            tar_name = f"{ac_number}_{disk_id}_{timestamp}.tar"
            tar_path = disk_path / tar_name
            
            print(f"\nErstelle TAR-Archiv: {tar_name}")
            
            try:
                with tarfile.open(tar_path, "w") as tar:
                    tar.add(folder_5, arcname=folder_5.name)
                
                print(f" [OK] TAR-Archiv erfolgreich erstellt.")
                
                # --- SCHRITT 5: BEREINIGUNG (Ordner 5 löschen) ---
                print(f"\nBereinige temporäre Daten...")
                try:
                    shutil.rmtree(folder_5)
                    print(f" [OK] Temporärer Ordner '{folder_5.name}' wurde gelöscht.")
                except Exception as e_del:
                    print(f" [!] HINWEIS: Ordner '{folder_5.name}' konnte nicht gelöscht werden: {e_del}")
                    print(f"     Bitte manuell löschen.")

                print(f"\n===================================================")
                print(f" ABSCHLUSS: Archivpaket erfolgreich erstellt.")
                print(f" Datei: {tar_name}")
                print(f"===================================================")

            except Exception as e_tar:
                print(f" [!] KRITISCHER FEHLER beim Erstellen des TAR-Archivs: {e_tar}")
        else:
            print("\n [!] ABBRUCH: Bag ist nicht valide. TAR wurde nicht erstellt.")

    except Exception as e:
        print(f"\n [!] FEHLER während der BagIt-Erstellung: {e}")
        print(" TIPP: Meistens ist ein offenes Explorer-Fenster schuld.")

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        run_lza_bagging(sys.argv[1], sys.argv[2])
    else:
        print("Fehler: AC-Nummer und ZPH-ID fehlen.")
        input("Enter zum Beenden...")