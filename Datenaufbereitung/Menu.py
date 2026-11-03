# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import subprocess
import sys
import os
from pathlib import Path

# ==============================================================================
# 🔧 FARB-INITIALISIERUNG (Konsistenz mit allen anderen Skripten)
# ==============================================================================
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class Fore: GREEN = RED = YELLOW = CYAN = MAGENTA = WHITE = ""
    class Style: RESET_ALL = ""

try:
    import tkinter as tk
    from tkinter import filedialog
    TK_AVAILABLE = True
except Exception:
    TK_AVAILABLE = False


# =====================================================
# Grundeinstellungen
# =====================================================
MENU_FILE = Path(__file__).resolve()
SCRIPT_DIR = MENU_FILE.parent

EXCLUDED_DIRS = {".venv", ".git", "__pycache__", ".idea", ".vscode"}
IGNORED_FILES = {MENU_FILE.name}

# Wenn True, wird der Datenpfad als zusätzliches Argument übergeben:
# python skript.py AC ID DATENPFAD
# Falls deine Subskripte Probleme mit einem dritten Argument haben,
# kannst du das auf False stellen. Dann wird nur die Umgebungsvariable DATA_PATH gesetzt.
PASS_DATA_PATH_AS_ARGUMENT = True

# Verwende denselben Interpreter, mit dem dieses Menü selbst läuft.
# Das ist robust gegen unterschiedliche Installationspfade
# (User-Installation vs. System-Installation usw.).
# Falls das Menü mit pythonw.exe gestartet wurde, bevorzuge python.exe,
# damit Konsolenskripte sichtbar bleiben.
PYTHON_EXECUTABLE = sys.executable
if Path(PYTHON_EXECUTABLE).name.lower() == "pythonw.exe":
    candidate = Path(PYTHON_EXECUTABLE).with_name("python.exe")
    if candidate.exists():
        PYTHON_EXECUTABLE = str(candidate)


# =====================================================
# Hilfsfunktionen für Ordnerauswahl
# =====================================================
def ask_directory(title, initial_dir=None):
    """
    Öffnet einen Ordner-Auswahldialog.
    Falls tkinter nicht verfügbar ist, wird nach einem manuellen Pfad gefragt.
    """
    if initial_dir is not None:
        initial_dir = Path(initial_dir)
        if not initial_dir.exists():
            initial_dir = SCRIPT_DIR

    if TK_AVAILABLE:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        try:
            if initial_dir is not None:
                selected = filedialog.askdirectory(
                    title=title,
                    initialdir=str(initial_dir)
                )
            else:
                selected = filedialog.askdirectory(title=title)
        finally:
            root.destroy()

        if not selected:
            return None

        return Path(selected).resolve()

    # Fallback ohne tkinter
    if initial_dir is not None:
        print(f"{Fore.WHITE}Startordner: {initial_dir}{Style.RESET_ALL}")

    raw = input(f"{Fore.YELLOW}{title}\nBitte vollständigen Ordnerpfad eingeben (leer = Abbrechen): {Style.RESET_ALL}").strip().strip('"')
    if not raw:
        return None

    p = Path(raw).expanduser()
    if not p.is_dir():
        print(f"{Fore.RED}[FEHLER] Der angegebene Pfad ist kein vorhandener Ordner.{Style.RESET_ALL}")
        return None

    return p.resolve()


def select_ac_folder(initial_dir=None):
    """Schritt 1: AC-Ordner auswählen."""
    print(f"\n{Fore.CYAN}Schritt 1: AC-Ordner auswählen.{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Der Name dieses Ordners wird als AC-Nummer verwendet.{Style.RESET_ALL}")

    ac_path = ask_directory("Schritt 1: AC-Ordner auswählen", initial_dir or SCRIPT_DIR)

    if ac_path is None:
        print(f"{Fore.YELLOW}Auswahl abgebrochen.{Style.RESET_ALL}")
        return None

    print(f"{Fore.GREEN}Gewählter AC-Ordner: {ac_path.name} -> {ac_path}{Style.RESET_ALL}")
    return ac_path


def select_disk_folder(ac_path, initial_dir=None):
    """Schritt 2: ID-Unterordner innerhalb des AC-Ordners auswählen."""
    if not ac_path or not Path(ac_path).is_dir():
        print(f"{Fore.RED}[FEHLER] Es ist kein gültiger AC-Ordner gesetzt.{Style.RESET_ALL}")
        return None

    ac_path = Path(ac_path).resolve()

    if initial_dir is not None and Path(initial_dir).exists():
        current_initial = Path(initial_dir).resolve()
    else:
        current_initial = ac_path

    print(f"\n{Fore.CYAN}Schritt 2: ID-Unterordner auswählen.{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Der ID-Ordner muss ein Unterordner von {ac_path} sein.{Style.RESET_ALL}")

    while True:
        disk_path = ask_directory("Schritt 2: ID-Unterordner auswählen", current_initial)

        if disk_path is None:
            print(f"{Fore.YELLOW}Auswahl abgebrochen.{Style.RESET_ALL}")
            return None

        if disk_path == ac_path:
            print(f"{Fore.RED}[FEHLER] Der ID-Ordner darf nicht der AC-Ordner selbst sein.{Style.RESET_ALL}")
            print(f"{Fore.WHITE}Bitte einen Unterordner auswählen.{Style.RESET_ALL}")
            current_initial = ac_path
            continue

        try:
            disk_path.relative_to(ac_path)
            print(f"{Fore.GREEN}Gewählter ID-Ordner: {disk_path.name} -> {disk_path}{Style.RESET_ALL}")
            return disk_path
        except ValueError:
            print(f"{Fore.RED}[FEHLER] Der gewählte Ordner liegt nicht im AC-Ordner.{Style.RESET_ALL}")
            print(f"{Fore.WHITE}Bitte erneut einen Unterordner des AC-Ordners auswählen.{Style.RESET_ALL}")
            current_initial = ac_path
            continue


def select_ac_and_disk():
    """Geführte Auswahl: Erst AC-Ordner, dann ID-Unterordner."""
    ac_path = select_ac_folder(SCRIPT_DIR)
    if ac_path is None:
        return None, None, False

    disk_path = select_disk_folder(ac_path)
    if disk_path is None:
        return ac_path, None, False

    return ac_path, disk_path, True


def ensure_ac_disk_path(ac_path, disk_path):
    """
    Prüft, ob AC-Ordner und ID-Ordner gesetzt sind.
    Falls nicht, wird der Benutzer zur Auswahl aufgefordert.
    """
    if ac_path is not None:
        ac_path = Path(ac_path).resolve()
    if disk_path is not None:
        disk_path = Path(disk_path).resolve()

    while True:
        if not ac_path or not ac_path.is_dir():
            ac_path = select_ac_folder(SCRIPT_DIR)
            if ac_path is None:
                return ac_path, disk_path, False

            # Wenn ein neuer AC-Ordner gewählt wurde, passt die alte ID in der Regel nicht mehr.
            disk_path = None

        if not disk_path or not disk_path.is_dir():
            disk_path = select_disk_folder(ac_path)
            if disk_path is None:
                return ac_path, disk_path, False

        try:
            disk_path.relative_to(ac_path)
            return ac_path, disk_path, True
        except ValueError:
            print(f"{Fore.YELLOW}[WARNUNG] Der ID-Ordner liegt nicht im AC-Ordner.{Style.RESET_ALL}")
            print(f"{Fore.WHITE}Bitte ID-Ordner neu auswählen.{Style.RESET_ALL}")
            disk_path = None


# =====================================================
# Anzeige / Skriptsuche
# =====================================================
def print_header(ac_path, disk_path):
    """Zeigt den farbigen Header mit den aktuellen Werten an."""
    ac_display = ac_path.name if ac_path else "❌ NICHT GESETZT"
    disk_display = disk_path.name if disk_path else "❌ NICHT GESETZT"

    if disk_path:
        path_display = str(disk_path)
    elif ac_path:
        path_display = str(ac_path)
    else:
        path_display = "❌ NICHT GESETZT"

    # Farbige Darstellung der Statuswerte
    if ac_path:
        ac_colored = f"{Fore.GREEN}{ac_display}{Style.RESET_ALL}"
    else:
        ac_colored = f"{Fore.RED}{ac_display}{Style.RESET_ALL}"

    if disk_path:
        disk_colored = f"{Fore.GREEN}{disk_display}{Style.RESET_ALL}"
    else:
        disk_colored = f"{Fore.RED}{disk_display}{Style.RESET_ALL}"

    if disk_path:
        path_colored = f"{Fore.GREEN}{path_display}{Style.RESET_ALL}"
    elif ac_path:
        path_colored = f"{Fore.YELLOW}{path_display}{Style.RESET_ALL}"
    else:
        path_colored = f"{Fore.RED}{path_display}{Style.RESET_ALL}"

    print(f"{Fore.MAGENTA}==================================================={Style.RESET_ALL}")
    print(f"{Fore.CYAN}           DATENAUFBEREITUNG - MENÜ{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}==================================================={Style.RESET_ALL}")
    print(f"{Fore.WHITE} Aktuelle AC-Nummer:      {ac_colored}")
    print(f"{Fore.WHITE} Aktuelle Datenträger-ID: {disk_colored}")
    print(f"{Fore.WHITE} Aktueller Datenpfad:     {path_colored}")
    print(f"{Fore.MAGENTA}---------------------------------------------------{Style.RESET_ALL}")


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

    scripts = sorted(scripts, key=lambda p: str(p.relative_to(SCRIPT_DIR)).lower())
    return scripts


# =====================================================
# Hauptprogramm
# =====================================================
def main():
    ac_path = None
    disk_path = None

    # Optional: Falls das Menü selbst mit Pfaden gestartet wird.
    # Beispiel:
    # python menu.py "C:\daten\AC123" "C:\daten\AC123\ID456"
    if len(sys.argv) >= 3:
        arg_ac = Path(sys.argv[1]).expanduser()
        arg_disk = Path(sys.argv[2]).expanduser()

        if arg_ac.is_dir():
            ac_path = arg_ac.resolve()

        if arg_disk.is_dir():
            disk_path = arg_disk.resolve()

        if ac_path and disk_path:
            try:
                disk_path.relative_to(ac_path)
            except ValueError:
                disk_path = None

        if not ac_path:
            disk_path = None

    while True:
        print_header(ac_path, disk_path)
        scripts = get_scripts()
        entry_num = 1

        if scripts:
            print(f"\n{Fore.CYAN}   --- Skripte ---{Style.RESET_ALL}")
            for script_path in scripts:
                print(f"   {Fore.GREEN}{entry_num:3}{Style.RESET_ALL} - {Fore.WHITE}{script_path.name}{Style.RESET_ALL}")
                entry_num += 1
        else:
            print(f"\n{Fore.YELLOW}   Keine Skripte gefunden.{Style.RESET_ALL}")

        print(f"\n{Fore.MAGENTA}---------------------------------------------------{Style.RESET_ALL}")
        print(f"   {Fore.GREEN}A{Style.RESET_ALL} - {Fore.WHITE}AC-Ordner auswählen{Style.RESET_ALL}")
        print(f"   {Fore.GREEN}D{Style.RESET_ALL} - {Fore.WHITE}ID-Ordner auswählen{Style.RESET_ALL}")
        print(f"   {Fore.GREEN}N{Style.RESET_ALL} - {Fore.WHITE}Neue Auswahl starten (AC + ID){Style.RESET_ALL}")
        print(f"   {Fore.GREEN}B{Style.RESET_ALL} - {Fore.WHITE}Zurück / Beenden{Style.RESET_ALL}")
        print(f"   {Fore.RED}Q{Style.RESET_ALL} - {Fore.WHITE}Beenden{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}==================================================={Style.RESET_ALL}")

        choice = input(f"\n{Fore.YELLOW}Bitte Nummer oder Buchstabe eingeben: {Style.RESET_ALL}").strip().lower()

        if choice == "q":
            print(f"\n{Fore.CYAN}Menü wird beendet. Auf Wiedersehen!{Style.RESET_ALL}")
            break

        elif choice == "b":
            print(f"\n{Fore.CYAN}Zurück zum Hauptmenü...{Style.RESET_ALL}")
            break

        elif choice == "a":
            new_ac = select_ac_folder(ac_path or SCRIPT_DIR)
            if new_ac is not None:
                ac_path = new_ac

                # Alte ID nur behalten, wenn sie zufällig im neuen AC-Ordner liegt
                if disk_path is not None:
                    try:
                        disk_path.relative_to(ac_path)
                    except ValueError:
                        disk_path = None

            input(f"\n{Fore.YELLOW}Drücken Sie Enter, um fortzufahren.{Style.RESET_ALL}")
            continue

        elif choice == "d":
            if not ac_path:
                print(f"\n{Fore.YELLOW}Bitte zuerst einen AC-Ordner auswählen (Menüpunkt A).{Style.RESET_ALL}")
            else:
                new_disk = select_disk_folder(ac_path, disk_path or ac_path)
                if new_disk is not None:
                    disk_path = new_disk

            input(f"\n{Fore.YELLOW}Drücken Sie Enter, um fortzufahren.{Style.RESET_ALL}")
            continue

        elif choice == "n":
            new_ac, new_disk, ok = select_ac_and_disk()
            if ok:
                ac_path = new_ac
                disk_path = new_disk
            else:
                if new_ac is not None:
                    ac_path = new_ac
                    disk_path = None

            input(f"\n{Fore.YELLOW}Drücken Sie Enter, um fortzufahren.{Style.RESET_ALL}")
            continue

        try:
            choice_index = int(choice) - 1

            if 0 <= choice_index < len(scripts):
                script_to_run = scripts[choice_index]

                ac_path, disk_path, success = ensure_ac_disk_path(ac_path, disk_path)
                if not success:
                    input(f"\n{Fore.YELLOW}Drücken Sie Enter, um fortzufahren.{Style.RESET_ALL}")
                    continue

                ac_number = ac_path.name
                disk_id = disk_path.name
                data_path = disk_path

                print(f"\n{Fore.CYAN}--- Starte Skript: {script_to_run.name} ---{Style.RESET_ALL}")
                print(f"{Fore.WHITE}Uebergebe AC-Nummer:      {Fore.GREEN}{ac_number}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}Uebergebe Datenträger-ID: {Fore.GREEN}{disk_id}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}Uebergebe Datenpfad:      {Fore.GREEN}{data_path}{Style.RESET_ALL}\n")

                env = os.environ.copy()
                env["AC_NUMBER"] = ac_number
                env["DISK_ID"] = disk_id
                env["DATA_PATH"] = str(data_path)

                cmd = [
                    PYTHON_EXECUTABLE,
                    str(script_to_run),
                    ac_number,
                    disk_id
                ]

                if PASS_DATA_PATH_AS_ARGUMENT:
                    cmd.append(str(data_path))

                subprocess.run(
                    cmd,
                    cwd=script_to_run.parent,
                    env=env
                )

                print(f"\n{Fore.MAGENTA}----------------------------------------------------{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Skript-Ausfuehrung beendet. Druecken Sie Enter, um zum Menue zurueckzukehren.{Style.RESET_ALL}")

            else:
                print(f"\n{Fore.RED}[FEHLER] Ungueltige Auswahl.{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Druecken Sie Enter, um fortzufahren.{Style.RESET_ALL}")

        except ValueError:
            print(f"\n{Fore.RED}[FEHLER] Ungueltige Eingabe. Bitte eine Nummer oder A/D/N/B/Q eingeben.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Druecken Sie Enter, um fortzufahren.{Style.RESET_ALL}")

        except Exception as e:
            print(f"\n{Fore.RED}[FEHLER] Ein unerwarteter Fehler ist aufgetreten: {e}{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Druecken Sie Enter, um fortzufahren.{Style.RESET_ALL}")


if __name__ == "__main__":
    main()