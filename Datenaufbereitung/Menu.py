import subprocess
import sys
from pathlib import Path

# =====================================================
# Grundeinstellungen
# =====================================================
MENU_FILE = Path(__file__).resolve()
SCRIPT_DIR = MENU_FILE.parent

EXCLUDED_DIRS = {".venv", ".git", "__pycache__", ".idea", ".vscode"}
IGNORED_FILES = {MENU_FILE.name}

# =====================================================
# Hilfsfunktionen
# =====================================================
def print_header(ac_number, disk_id, current_path):
    """Zeigt den Header mit den aktuellen Werten an."""
    print("===================================================")
    print("           DATENAUFBEREITUNG - MENÜ")
    print("===================================================")
    
    ac_display = ac_number if ac_number and ac_number != "NICHT GESETZT" else "❌ NICHT GESETZT"
    disk_display = disk_id if disk_id and disk_id != "NICHT GESETZT" else "❌ NICHT GESETZT"
    
    print(f" Aktuelle AC-Nummer:      {ac_display}")
    print(f" Aktuelle Datenträger-ID: {disk_display}")
    print(f" Aktueller Ordner:        {current_path}")
    print("---------------------------------------------------")

def is_excluded_folder(script_path: Path) -> bool:
    """Prüft, ob die Datei in einem ausgeschlossenen Ordner liegt."""
    try:
        rel_path = script_path.relative_to(SCRIPT_DIR)
    except ValueError:
        return True
    folders = rel_path.parts[:-1]
    return any(folder in EXCLUDED_DIRS for folder in folders)

def get_scripts():
    """Sucht alle Python-Skripte rekursiv im aktuellen Ordner."""
    scripts = []
    
    for path in SCRIPT_DIR.rglob("*.py"):
        if path.name in IGNORED_FILES:
            continue
        if is_excluded_folder(path):
            continue
        scripts.append(path)

    # Sortierung nach relativem Pfad
    scripts = sorted(scripts, key=lambda p: str(p.relative_to(SCRIPT_DIR)).lower())
    return scripts

def ensure_ac_disk_id(ac_number, disk_id):
    """Prüft ob AC-Nummer und Datenträger-ID gesetzt sind."""
    ac_missing = not ac_number or ac_number == "NICHT GESETZT"
    disk_missing = not disk_id or disk_id == "NICHT GESETZT"
    
    if not ac_missing and not disk_missing:
        return ac_number, disk_id, True
    
    print("\n" + "=" * 50)
    print("  [WARNUNG] Fehlende Parameter!")
    print("=" * 50)
    print()
    
    if ac_missing:
        ac_number = input("AC-Nummer eingeben: ").strip()
    if disk_missing:
        disk_id = input("Datenträger-ID eingeben: ").strip()
    
    if not ac_number or not disk_id:
        print("\n[FEHLER] Beide Werte müssen eingegeben werden.")
        input("Drücken Sie Enter, um fortzufahren.")
        return ac_number, disk_id, False
    
    return ac_number, disk_id, True

# =====================================================
# Hauptprogramm
# =====================================================
def main():
    if len(sys.argv) >= 3:
        ac_number = sys.argv[1] if sys.argv[1] else "NICHT GESETZT"
        disk_id = sys.argv[2] if sys.argv[2] else "NICHT GESETZT"
    else:
        ac_number = "NICHT GESETZT"
        disk_id = "NICHT GESETZT"

    while True:
        print_header(ac_number, disk_id, "Datenaufbereitung")
        scripts = get_scripts()
        entry_num = 1

        if scripts:
            print("\n   --- Skripte ---")
            for script_path in scripts:
                # NUR DEN DATEINAMEN ANZEIGEN
                print(f"   {entry_num:3} - {script_path.name}")
                entry_num += 1
        else:
            print("\n   Keine Skripte gefunden.")

        print("\n---------------------------------------------------")
        print("   N - Neue Nummern eingeben")
        print("   B - Zurück zum Hauptmenü")
        print("   Q - Beenden")
        print("===================================================")

        choice = input("\nBitte Nummer eingeben: ").strip().lower()

        if choice == "q":
            break
        elif choice == "b":
            break
        elif choice == "n":
            print("\n--- Bitte neue Werte eingeben ---")
            new_ac = input(f"Neue AC-Nummer (alt: {ac_number}): ").strip()
            new_disk = input(f"Neue Datenträger-ID (alt: {disk_id}): ").strip()

            if new_ac: ac_number = new_ac
            if new_disk: disk_id = new_disk

            input("\nDrücken Sie Enter, um fortzufahren.")
            continue

        try:
            choice_index = int(choice) - 1

            if 0 <= choice_index < len(scripts):
                script_to_run = scripts[choice_index]

                ac_number, disk_id, success = ensure_ac_disk_id(ac_number, disk_id)
                if not success:
                    continue

                print(f"\n--- Starte Skript: {script_to_run.name} ---")
                print(f"Uebergebe AC-Nummer: {ac_number}")
                print(f"Uebergebe Datenträger-ID: {disk_id}\n")

                subprocess.run(
                    [
                        r"C:\Users\digit\AppData\Local\Programs\Python\Python313\python.exe",
                        str(script_to_run),
                        ac_number,
                        disk_id
                    ],
                    cwd=script_to_run.parent
                )

                print("\n----------------------------------------------------")
                input("Skript-Ausfuehrung beendet. Druecken Sie Enter, um zum Menue zurueckzukehren.")

            else:
                print("\nUngueltige Auswahl.")
                input("Druecken Sie Enter, um fortzufahren.")

        except ValueError:
            print("\nUngueltige Eingabe. Bitte eine Nummer oder N/B/Q eingeben.")
            input("Druecken Sie Enter, um fortzufahren.")

        except Exception as e:
            print(f"\nEin unerwarteter Fehler ist aufgetreten: {e}")
            input("Druecken Sie Enter, um fortzufahren.")

if __name__ == "__main__":
    main()