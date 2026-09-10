import subprocess
import sys
from pathlib import Path

# =====================================================
# Grundeinstellungen
# =====================================================

# Die Datei, in der sich dieses Skript befindet
MENU_FILE = Path(__file__).resolve()

# Der Hauptordner, in dem die menu.py liegt
SCRIPT_DIR = MENU_FILE.parent

# Diese Ordner werden nicht nach Python-Skripten durchsucht
EXCLUDED_DIRS = {
    ".venv",
    ".git",
    "__pycache__",
    ".idea",
    ".vscode",
}

# Diese Dateien werden nicht als startbare Skripte angezeigt
IGNORED_FILES = {
    MENU_FILE.name
}

# Ordner, die als eigene Menüeinträge angezeigt werden (mit Untermenü)
SUBMENU_DIRS = {
    "Textdokumente_vergleichen"
}


# =====================================================
# Hilfsfunktionen
# =====================================================

def print_header(ac_number, disk_id, current_path):
    """Zeigt den Header mit den aktuellen Werten an."""
    print("===================================================")
    print("           PYTHON SKRIPT STARTER")
    print("===================================================")
    print(f" Aktuelle AC-Nummer:      {ac_number}")
    print(f" Aktuelle Datenträger-ID: {disk_id}")
    print(f" Aktueller Ordner:        {current_path}")
    print("---------------------------------------------------")


def is_excluded_folder(script_path: Path) -> bool:
    """
    Prüft, ob die Datei in einem ausgeschlossenen Ordner liegt.
    """
    try:
        rel_path = script_path.relative_to(SCRIPT_DIR)
    except ValueError:
        return True

    folders = rel_path.parts[:-1]
    return any(folder in EXCLUDED_DIRS for folder in folders)


def is_in_submenu_dir(script_path: Path) -> bool:
    """
    Prüft, ob die Datei in einem der SUBMENU_DIRS liegt.
    """
    try:
        rel_path = script_path.relative_to(SCRIPT_DIR)
    except ValueError:
        return False

    if len(rel_path.parts) < 2:
        return False

    return rel_path.parts[0] in SUBMENU_DIRS


def get_main_menu_scripts():
    """
    Sucht alle Python-Skripte rekursiv, außer in SUBMENU_DIRS.
    """
    scripts = []
    submenu_entries = []

    # Füge SUBMENU_DIRS als Einträge hinzu
    for subdir_name in sorted(SUBMENU_DIRS):
        subdir_path = SCRIPT_DIR / subdir_name
        if subdir_path.is_dir():
            submenu_entries.append(subdir_name)

    # Suche alle Skripte rekursiv
    for path in SCRIPT_DIR.rglob("*.py"):
        if path.name in IGNORED_FILES:
            continue

        if is_excluded_folder(path):
            continue

        # Überspringe Skripte in SUBMENU_DIRS
        if is_in_submenu_dir(path):
            continue

        scripts.append(path)

    # Sortierung nach relativem Pfad
    scripts = sorted(
        scripts,
        key=lambda p: str(p.relative_to(SCRIPT_DIR)).lower()
    )

    return submenu_entries, scripts


def get_submenu_scripts(submenu_dir_name: str):
    """
    Sucht alle Python-Skripte in einem spezifischen Untermenü-Ordner.
    """
    scripts = []
    submenu_path = SCRIPT_DIR / submenu_dir_name

    for path in submenu_path.rglob("*.py"):
        if path.name in IGNORED_FILES:
            continue

        if is_excluded_folder(path):
            continue

        scripts.append(path)

    # Sortierung nach Dateiname
    scripts = sorted(scripts, key=lambda p: p.name.lower())

    return scripts


def get_folder_shortcut(folder_name: str) -> str:
    """
    Gibt den ersten Buchstaben des Ordnernamens als Shortcut zurück.
    """
    return folder_name[0].upper() if folder_name else ""


def start_submenu(folder_name: str):
    """
    Startet die start.bat eines Unterordners als separaten Prozess.
    """
    submenu_path = SCRIPT_DIR / folder_name
    start_bat = submenu_path / "start.bat"
    
    if not start_bat.exists():
        print(f"\n[FEHLER] start.bat nicht gefunden in: {submenu_path}")
        input("Drücken Sie Enter, um fortzufahren.")
        return
    
    print(f"\n--- Starte Unterordner: {folder_name} ---")
    print(f"Die start.bat wird als separater Prozess gestartet.")
    print(f"Nach dem Beenden kehren Sie automatisch zum Hauptmenü zurück.\n")
    
    # Starte die start.bat als separaten Prozess
    subprocess.run(
        [str(start_bat)],
        cwd=str(submenu_path),
        shell=True
    )
    
    print(f"\n--- Unterordner {folder_name} wurde beendet. ---")
    input("Drücken Sie Enter, um zum Hauptmenü zurückzukehren.")


# =====================================================
# Hauptprogramm
# =====================================================

def main():
    """Zeigt ein Menü an, verwaltet AC-Nummer/Disk-ID und führt Skripte aus."""

    # Empfängt die Werte von der start.bat
    if len(sys.argv) >= 3:
        ac_number = sys.argv[1]
        disk_id = sys.argv[2]
    else:
        print("Fehler: AC-Nummer und Datenträger-ID wurden nicht übergeben.")
        ac_number = "NICHT GESETZT"
        disk_id = "NICHT GESETZT"

    current_submenu = None  # None = Hauptmenü

    while True:
        current_path = current_submenu if current_submenu else "Hauptmenü"
        print_header(ac_number, disk_id, current_path)

        if current_submenu is None:
            # Hauptmenü
            submenu_entries, scripts = get_main_menu_scripts()
        else:
            # Untermenü
            submenu_entries = []
            scripts = get_submenu_scripts(current_submenu)

        entry_num = 1

        # === Normale Skripte (zuerst) ===
        if scripts:
            print("\n   --- Skripte ---")
            for script_path in scripts:
                print(f"   {entry_num:3} - {script_path.name}")
                entry_num += 1

        # === Untermenü-Ordner (danach, mit Buchstaben-Shortcut) ===
        if submenu_entries:
            print("\n   --- Ordner ---")
            for folder_name in submenu_entries:
                shortcut = get_folder_shortcut(folder_name)
                print(f"   {shortcut}   - [ORDNER] {folder_name}")

        if not submenu_entries and not scripts:
            print("\n   Keine Einträge gefunden.")

        print("\n---------------------------------------------------")
        print("   N - Neue Nummern eingeben")
        if current_submenu is not None:
            print("   B - Zurück zum Hauptmenü")
        print("   Q - Beenden")
        print("===================================================")

        choice = input("\nBitte Nummer oder Buchstaben eingeben: ").strip().lower()

        if choice == "q":
            break

        elif choice == "b" and current_submenu is not None:
            current_submenu = None
            continue

        elif choice == "n":
            print("\n--- Bitte neue Werte eingeben ---")
            new_ac = input(f"Neue AC-Nummer (alt: {ac_number}): ").strip()
            new_disk = input(f"Neue Datenträger-ID (alt: {disk_id}): ").strip()

            if new_ac:
                ac_number = new_ac
            else:
                print("Keine neue AC-Nummer eingegeben. Alter Wert bleibt erhalten.")

            if new_disk:
                disk_id = new_disk
            else:
                print("Keine neue Datenträger-ID eingegeben. Alter Wert bleibt erhalten.")

            input("\nDrücken Sie Enter, um fortzufahren.")
            continue

        # Prüfe ob es ein Buchstaben-Shortcut für einen Ordner ist
        if current_submenu is None and choice.isalpha():
            choice_upper = choice.upper()
            for folder_name in submenu_entries:
                if get_folder_shortcut(folder_name) == choice_upper:
                    # NEU: Starte die start.bat des Unterordners als separaten Prozess
                    start_submenu(folder_name)
                    break
            else:
                # Buchstabe passt zu keinem Ordner
                print("\nUngueltige Eingabe.")
                input("Druecken Sie Enter, um fortzufahren.")
            continue

        # Ansonsten versuche als Nummer zu interpretieren
        try:
            choice_index = int(choice) - 1

            if 0 <= choice_index < len(scripts):
                script_to_run = scripts[choice_index]

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
            print("\nUngueltige Eingabe. Bitte eine Nummer, einen Buchstaben oder N/B/Q eingeben.")
            input("Druecken Sie Enter, um fortzufahren.")

        except Exception as e:
            print(f"\nEin unerwarteter Fehler ist aufgetreten: {e}")
            input("Druecken Sie Enter, um fortzufahren.")


if __name__ == "__main__":
    main()