import os
import sys
import shutil
import time
from datetime import datetime
from pathlib import Path

# Colorama für Statusmeldungen
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class Fore: GREEN = RED = YELLOW = CYAN = MAGENTA = WHITE = ""
    class Style: RESET_ALL = ""

def run_staging_workflow(ac_number, disk_id):
    """
    Workflow V11 (Angepasst):
    1. VL-Export (Stufe 4) vervollständigen (Fotos & Metadaten kopieren)
    2. LZA-Staging (Stufe 5) vorbereiten (Alles verschieben & strukturieren)
       - Images (.img, .raw) gehen in Unterordner 'images'
       - Logs (.csv, .log, .txt, .index) gehen in Unterordner 'logfiles'
    3. KEINE automatische Bereinigung mehr (verschoben nach K3)
    """
    # Pfad-Definition (Nutzt Path.home() für bessere Kompatibilität)
    base_root = Path.home() / "Documents" / "data"
    disk_path = base_root / ac_number / disk_id

    # Grundpfade
    f0 = disk_path / f"0_{disk_id}_picture-carrier"
    f1 = disk_path / f"1_{disk_id}_image-LZA"
    f2 = disk_path / f"2_{disk_id}_extracted-files"
    f3 = disk_path / f"3_{disk_id}_for-transfer"
    f4_vl = disk_path / f"4_{disk_id}_VL"
    f5_lza = disk_path / f"5_{disk_id}_LZA"

    print(f"\n{Fore.MAGENTA}===================================================")
    print(f"{Fore.WHITE}   STAGING-WORKFLOW V11 (REDUZIERT): VL & LZA")
    print(f"{Fore.MAGENTA}==================================================={Fore.RESET}")

    # Suche nach dem 'files' Ordner in Stufe 3 (wird für LZA-Umzug benötigt)
    src_files_dir = None
    if f3.exists():
        for item in f3.iterdir():
            if item.is_dir() and item.name.lower() == "files":
                src_files_dir = item
                break

    # Sicherheits-Abfrage
    print(f"{Fore.YELLOW}[!] HINWEIS: Dieses Skript strukturiert Stufe 5 für den Master-Index.")
    if input(" Staging jetzt starten? (j/n): ").lower() != 'j': return

    # --- HILFSFUNKTIONEN ---
    def safe_move_item(src, dest_dir, rename_to=None):
        if src.exists():
            try:
                if not dest_dir.exists(): dest_dir.mkdir(parents=True)
                target_name = rename_to if rename_to else src.name
                target = dest_dir / target_name
                if target.exists():
                    if target.is_dir(): shutil.rmtree(target)
                    else: os.remove(target)
                shutil.move(str(src), str(target))
                print(f"{Fore.GREEN} [Move] -> {src.name} verschoben nach {dest_dir.name}/{target_name}")
                return True
            except Exception as e:
                print(f"{Fore.RED} [!] Fehler bei {src.name}: {e}")
        return False

    # --- SCHRITT 1: VL-EXPORT VERVOLLSTÄNDIGEN ---
    print(f"\n{Fore.CYAN}--- SCHRITT 1: Metadaten nach VL (Stufe 4) kopieren ---")
    if not f4_vl.exists():
        f4_vl.mkdir(parents=True)

    # A) Fotos (.tif) aus Stufe 0 kopieren
    if f0.exists():
        for tif in f0.glob("*.tif"):
            if not (f4_vl / tif.name).exists():
                shutil.copy2(tif, f4_vl)
                print(f"{Fore.GREEN} [Kopie] -> Foto {tif.name} nach VL kopiert.")
    
    # B) Inhaltsübersichten aus Stufe 2 kopieren
    meta_f2 = [f"2_{disk_id}_extracted-files.content", f"2_{disk_id}_extracted-files_tree.txt"]
    for item in meta_f2:
        src_item = f2 / item
        if src_item.exists() and not (f4_vl / item).exists():
            shutil.copy2(src_item, f4_vl)
            print(f"{Fore.GREEN} [Kopie] -> Übersicht {item} nach VL kopiert.")

    # C) Technischen Index (erstellt von H1) verifizieren
    index_name = f"3_{disk_id}_for-transfer.index"
    if (f4_vl / index_name).exists():
        print(f"{Fore.GREEN} [OK] Technischer Index bereits in VL vorhanden.")
    else:
        print(f"{Fore.YELLOW} [!] Hinweis: Index {index_name} wurde noch nicht in VL gefunden.")

    # --- SCHRITT 2: LZA-STAGING (ORDNER 5 STRUKTURIEREN) ---
    print(f"\n{Fore.CYAN}--- SCHRITT 2: LZA-Staging (Stufe 5 strukturieren) ---")
    
    # KORREKTUR: Ordner NICHT löschen, nur sicherstellen, dass er existiert
    if not f5_lza.exists():
        f5_lza.mkdir(parents=True)
    
    # NEU: Unterordner für Logs und Image anlegen (Singular "image" für Konsistenz!)
    lza_logs_dir = f5_lza / "logfiles"
    lza_images_dir = f5_lza / "image"  # <--- HIER GEÄNDERT: aus "images" wurde "image"
    
    if not lza_logs_dir.exists():
        lza_logs_dir.mkdir(parents=True)
    if not lza_images_dir.exists():
        lza_images_dir.mkdir(parents=True)

    # A) Konsolidierung bereits vorhandener 'logfiles' Unterordner
    for source_stage in [f0, f1, f2, f3]:
        sub_log = source_stage / "logfiles"
        if sub_log.exists() and sub_log.is_dir():
            for item in sub_log.iterdir():
                shutil.move(str(item), str(lza_logs_dir / item.name))
            try: sub_log.rmdir()
            except: pass

    # B) Bilder aus Ordner 0 (Originale) in logfiles verschieben
    if f0.exists():
        for item in f0.iterdir():
            if item.is_file(): shutil.move(str(item), str(lza_logs_dir / item.name))

    # C) Nutzdaten verschieben und umbenennen in '3_files' (Falls vorhanden)
    if src_files_dir:
        safe_move_item(src_files_dir, f5_lza, rename_to="3_files")

    # D) Ordner 1 (Image-LZA) verschieben - MIT NEUER UNTERSCHEIDUNG
    if f1.exists():
        for item in f1.iterdir():
            if item.is_file():
                ext = item.suffix.lower()
                # GEÄNDERT: Images gehen in den 'image'-Unterordner (Singular)
                if ext in [".img", ".raw"]:
                    shutil.move(str(item), str(lza_images_dir / item.name))
                    print(f"{Fore.GREEN} [Move] -> Image {item.name} nach image/ verschoben.")
                # NEU: Logs (csv, log) gehen in den 'logfiles'-Unterordner
                elif ext in [".csv", ".log"]:
                    shutil.move(str(item), str(lza_logs_dir / item.name))
                    print(f"{Fore.GREEN} [Move] -> Log {item.name} nach logfiles/ verschoben.")
                # Andere Dateien (z.B. .dd, .001, .bin) bleiben im Hauptordner
                else:
                    shutil.move(str(item), str(f5_lza / item.name))
                    print(f"{Fore.GREEN} [Move] -> {item.name} nach Stufe 5 (Hauptordner) verschoben.")
        print(f"{Fore.GREEN} [Move] -> Inhalte aus Stufe 1 strukturiert nach Stufe 5 verschoben.")

    # E) Alle Berichte aus Ordner 2 (Inhalte) nach logfiles verschieben
    items_f2 = [f"2_{disk_id}_extracted-files.content", 
            f"2_{disk_id}_extracted-files_brunnhilde-summary.json", 
            f"2_{disk_id}_extracted-files_tree.txt", 
            f"2_{disk_id}_extracted-files_brunnhilde"]
    for item in items_f2:
        if (f2 / item).exists():
            safe_move_item(f2 / item, lza_logs_dir)

    # F) Alle verbliebenen Dateien aus Ordner 3 (Index, Logs, Tree) nach logfiles verschieben
    # NEU: .txt wurde zur Liste hinzugefügt, damit auch die Tree-Datei hier landet
    if f3.exists():
        for item in f3.iterdir():
            if item.is_file() and item.suffix in [".log", ".index", ".txt"]:
                safe_move_item(item, lza_logs_dir)

    print(f"\n{Fore.MAGENTA}===================================================")
    print(f"{Fore.GREEN} STAGING ERFOLGREICH BEENDET")
    print(f" Die Stufen 0, 1, 2 und 3 sind nun bereit für den Master-Index (Skript L)")
    print(f" und die PREMIS-Erstellung (Skript J).")
    print(f"{Fore.MAGENTA}==================================================={Style.RESET_ALL}")

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        run_staging_workflow(sys.argv[1], sys.argv[2])
    else:
        print(f"{Fore.RED}Fehler: AC-Nummer und ID fehlen.")