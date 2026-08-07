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


# =====================================================
# Hilfsfunktionen
# =====================================================

def print_header(ac_number, disk_id):
    """Zeigt den Header mit den aktuellen Werten an."""
    print("===================================================")
    print(" PYTHON SKRIPT STARTER (Umgebung: .venv ist aktiv)")
    print("===================================================")
    print(f" Aktuelle AC-Nummer:      {ac_number}")
    print(f" Aktuelle Datenträger-ID: {disk_id}")
    print("---------------------------------------------------")
    print("\n Verfügbare Skripte:\n")


def is_excluded_folder(script_path: Path) -> bool:
    """
    Prüft, ob die Datei in einem ausgeschlossenen Ordner liegt.
    """
    try:
        rel_path = script_path.relative_to(SCRIPT_DIR)
    except ValueError:
        return True

    # Der letzte Teil ist der Dateiname.
    # Wir prüfen nur die darüberliegenden Ordner.
    folders = rel_path.parts[:-1]

    return any(folder in EXCLUDED_DIRS for folder in folders)


def get_scripts():
    """
    Sucht alle Python-Skripte im Hauptordner und in allen Unterordnern.
    Ausgeschlossene Ordner und die menu.py selbst werden ignoriert.
    """
    scripts = []

    for path in SCRIPT_DIR.rglob("*.py"):
        if path.name in IGNORED_FILES:
            continue

        if is_excluded_folder(path):
            continue

        scripts.append(path)

    # Sortierung nach relativem Pfad, unabhängig von Groß-/Kleinschreibung
    return sorted(
        scripts,
        key=lambda p: str(p.relative_to(SCRIPT_DIR)).lower()
    )


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

    while True:
        print_header(ac_number, disk_id)

        scripts = get_scripts()

        if not scripts:
            print("   Keine Python-Skripte gefunden.")
        else:
            for i, script_path in enumerate(scripts, 1):
                rel_path = script_path.relative_to(SCRIPT_DIR)
                print(f"   {i:3} - {rel_path}")

        print("\n   N - Neue Nummern eingeben")
        print("   Q - Beenden\n")
        print("===================================================")

        choice = input("Bitte Nummer des Skripts eingeben (oder N / Q): ").strip().lower()

        if choice == "q":
            break

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

        try:
            choice_index = int(choice) - 1

            if 0 <= choice_index < len(scripts):
                script_to_run = scripts[choice_index]

                print(f"\n--- Starte Skript: {script_to_run.relative_to(SCRIPT_DIR)} ---")
                print(f"Uebergebe AC-Nummer: {ac_number}")
                print(f"Uebergebe Datenträger-ID: {disk_id}\n")

                # Übergibt die Werte als Kommandozeilen-Argumente an das Zielskript.
                # Arbeitsverzeichnis ist der Ordner des jeweiligen Skripts.
                subprocess.run(
                    [
                        sys.executable,
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
            print("\nUngueltige Eingabe. Bitte eine Nummer, 'N' oder 'Q' eingeben.")
            input("Druecken Sie Enter, um fortzufahren.")

        except Exception as e:
            print(f"\nEin unerwarteter Fehler ist aufgetreten: {e}")
            input("Druecken Sie Enter, um fortzufahren.")


if __name__ == "__main__":
    main()