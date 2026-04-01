import os
import sys
import shutil
import bagit
import time
from pathlib import Path

def run_lza_bagging(ac_number, disk_id):
    """
    Sammelt Dateien aus den Ordnern 0, 1, 2 und 3 in den Ordner 5 
    und wandelt Ordner 5 in einen BagIt-Container um.
    """
    # --- BASIS-KONFIGURATION ---
    # Stammverzeichnis deiner Datenrettung
    base_root = Path(r"C:\Users\digit\Documents\data")
    
    # Pfad-Struktur: .../data/AC15993802/ZPH1705-120_04-12-03-01/
    disk_path = base_root / ac_number / disk_id

    # Definition der Quell- und Zielpfade mit den variablen Teilen
    folder_0 = disk_path / f"0_{disk_id}_picture-carrier"
    folder_1 = disk_path / f"1_{disk_id}_image-LZA"
    folder_2 = disk_path / f"2_{disk_id}_extracted-files"
    folder_3 = disk_path / f"3_{disk_id}_for-transfer"
    folder_5 = disk_path / f"5_{disk_id}_LZA" # Das Ziel-Verzeichnis (der spätere Bag)

    print(f"\n===================================================")
    print(f" LZA-ARCHIVIERUNG & BAGIT-ERSTELLUNG")
    print(f"===================================================")
    print(f"AC-Nummer:  {ac_number}")
    print(f"ZPH-ID:     {disk_id}")
    print(f"Zielordner: {folder_5.name}")
    print(f"---------------------------------------------------\n")

    # Prüfen, ob der Zielordner (Ordner 5) existiert
    if not folder_5.exists():
        print(f"FEHLER: Zielordner {folder_5} wurde nicht gefunden!")
        return

    def safe_move(src, dest_dir):
        """Hilfsfunktion zum sicheren Verschieben von Dateien und Ordnern."""
        if src.exists():
            try:
                target = dest_dir / src.name
                # Falls das Ziel bereits existiert (z.B. durch abgebrochenen Vorversuch), löschen
                if target.exists():
                    if target.is_dir(): shutil.rmtree(target)
                    else: os.remove(target)
                
                shutil.move(str(src), str(dest_dir))
                print(f" [OK] Verschoben: {src.name}")
            except Exception as e:
                print(f" [!] Fehler beim Verschieben von {src.name}: {e}")
        else:
            print(f" [ ] Nicht gefunden (übersprungen): {src.name}")

    # --- SCHRITT 1: DATEIEN IN ORDNER 5 ZUSAMMENFÜHREN ---
    
    print("Sammle Daten in Ordner 5...")

    # A) Ganze Ordner 0 und 1 verschieben
    safe_move(folder_0, folder_5)
    safe_move(folder_1, folder_5)

    # B) Spezifische Dateien/Ordner aus Ordner 2
    files_from_2 = [
        f"2_{disk_id}_extracted-files.content",
        f"2_{disk_id}_extracted-files_brunnhilde-summary.json",
        f"2_{disk_id}_extracted-files_tree.txt",
        f"2_{disk_id}_extracted-files_brunnhilde" # Unterordner
    ]
    for item in files_from_2:
        safe_move(folder_2 / item, folder_5)

    # C) Spezifische Dateien aus Ordner 3
    files_from_3 = [
        f"3_{disk_id}_for-transfer.index",
        f"3_{disk_id}_for-transfer_all-conversions.log",
        f"3_{disk_id}_for-transfer_delete-all.log",
        f"3_{disk_id}_for-transfer_delete-converted-odfs.log",
        f"3_{disk_id}_for-transfer_delete-converted-wavs.log",
        f"3_{disk_id}_for-transfer_delete-preview-all.log"
    ]
    for item in files_from_3:
        safe_move(folder_3 / item, folder_5)

    # --- SCHRITT 2: SYSTEMPAUSE GEGEN PERMISSION ERROR ---
    # Wichtig unter Windows: Kurz warten, damit alle Dateizugriffe (Handles)
    # vom Verschieben wirklich geschlossen sind, bevor BagIt den Ordner sperrt.
    print("\nDateien gesammelt. Warte 3 Sekunden auf Windows-Dateifreigabe...")
    time.sleep(3)

    # --- SCHRITT 3: BAGIT ERSTELLEN ---
    print(f"\nStarte BagIt-Erstellung in: {folder_5.name}")
    print("Berechne Prüfsummen (SHA-256), bitte warten...")

    metadata = {
        'Contact-Name': 'Datenrettung Digit',
        'Source-Organization': 'Digit Lab',
        'External-Identifier': ac_number,
        'Disk-ID': disk_id,
        'Internal-Sender-Description': f"Datenrettung LZA-Paket fuer {disk_id}"
    }

    try:
        # Erstellt den Bag direkt in Ordner 5 (In-Place)
        # checksums=['sha256'] reicht für LZA meist aus und ist schneller als mehrere Verfahren
        bag = bagit.make_bag(str(folder_5), metadata, checksums=['sha256'])
        
        # Validierung des frisch erstellten Bags
        if bag.validate():
            print(f"\n===================================================")
            print(f" ERFOLG: Der Ordner {folder_5.name} ist jetzt ein")
            print(f" vollständig validierter BagIt-Container.")
            print(f"===================================================")
        else:
            print("\n[!] WARNUNG: Bag wurde erstellt, ist aber NICHT valide.")

    except Exception as e:
        print(f"\n[!] FEHLER während der BagIt-Erstellung:")
        print(f" Details: {e}")
        print("\n TIPP: Schließe alle Windows-Explorer Fenster, die diesen")
        print(" Ordner anzeigen, und versuche es erneut.")

if __name__ == "__main__":
    # Die Werte werden vom menu.py übergeben
    if len(sys.argv) >= 3:
        ac_in = sys.argv[1]
        zph_in = sys.argv[2]
        run_lza_bagging(ac_in, zph_in)
    else:
        print("Fehler: Zu wenige Argumente vom Menü übergeben.")
        input("Drücken Sie Enter zum Beenden...")