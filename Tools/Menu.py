# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import subprocess
import sys
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

# =====================================================
# Grundeinstellungen
# =====================================================

# Die Datei, in der sich dieses Skript befindet
MENU_FILE = Path(__file__).resolve()

# Der Tools-Ordner, in dem die menu.py liegt
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
# Für den Tools-Ordner aktuell leer, kann aber in Zukunft erweitert werden
SUBMENU_DIRS = set()

# Explizite Shortcut-Zuweisung für Untermenü-Ordner
FOLDER_SHORTCUTS = {}

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
# Hilfsfunktionen
# =====================================================

def print_header(current_path):
    """Zeigt den farbigen Header für das Tools-Menü an (ohne AC/Disk-ID)."""
    print(f"{Fore.MAGENTA}==================================================={Style.RESET_ALL}")
    print(f"{Fore.CYAN}           PYTHON SKRIPTE TOOLS{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}==================================================={Style.RESET_ALL}")
    print(f"{Fore.WHITE} Aktueller Ordner:        {Fore.GREEN}{current_path}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}---------------------------------------------------{Style.RESET_ALL}")


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
    Sucht alle Python-Skripte rekursiv im Tools-Ordner.
    """
    scripts = []
    submenu_entries = []

    # Füge SUBMENU_DIRS als Einträge hinzu (aktuell leer für Tools)
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
    Gibt den Shortcut für einen Ordner zurück.
    """
    if folder_name in FOLDER_SHORTCUTS:
        return FOLDER_SHORTCUTS[folder_name]
    return folder_name[0].upper() if folder_name else ""


def start_submenu(folder_name: str):
    """
    Startet die start.bat eines Unterordners als separaten Prozess.
    """
    submenu_path = SCRIPT_DIR / folder_name
    start_bat = submenu_path / "start.bat"
    
    if not start_bat.exists():
        print(f"\n{Fore.RED}[FEHLER] start.bat nicht gefunden in: {submenu_path}{Style.RESET_ALL}")
        input(f"{Fore.YELLOW}Drücken Sie Enter, um fortzufahren.{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.CYAN}--- Starte Unterordner: {folder_name} ---{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Die start.bat wird als separater Prozess gestartet.{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Nach dem Beenden kehren Sie automatisch zum Tools-Menü zurück.{Style.RESET_ALL}\n")
    
    subprocess.run(
        [str(start_bat)],
        cwd=str(submenu_path),
        shell=True
    )
    
    print(f"\n{Fore.GREEN}--- Unterordner '{folder_name}' wurde beendet. ---{Style.RESET_ALL}")
    input(f"{Fore.YELLOW}Drücken Sie Enter, um zum Tools-Menü zurückzukehren.{Style.RESET_ALL}")


# =====================================================
# Hauptprogramm
# =====================================================

def main():
    """Zeigt ein Menü an und führt Tools aus (ohne AC/Disk-ID)."""

    current_submenu = None  # None = Hauptmenü

    while True:
        current_path = current_submenu if current_submenu else "Tools-Hauptmenü"
        print_header(current_path)

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
            print(f"\n{Fore.CYAN}   --- Tools ---{Style.RESET_ALL}")
            for script_path in scripts:
                print(f"   {Fore.GREEN}{entry_num:3}{Style.RESET_ALL} - {Fore.WHITE}{script_path.name}{Style.RESET_ALL}")
                entry_num += 1

        # === Untermenü-Ordner (danach, mit Buchstaben-Shortcut) ===
        if submenu_entries:
            print(f"\n{Fore.CYAN}   --- Ordner ---{Style.RESET_ALL}")
            for folder_name in submenu_entries:
                shortcut = get_folder_shortcut(folder_name)
                print(f"   {Fore.GREEN}{shortcut}{Style.RESET_ALL}   - {Fore.WHITE}[ORDNER] {folder_name}{Style.RESET_ALL}")

        if not submenu_entries and not scripts:
            print(f"\n{Fore.YELLOW}   Keine Einträge gefunden.{Style.RESET_ALL}")

        print(f"\n{Fore.MAGENTA}---------------------------------------------------{Style.RESET_ALL}")
        if current_submenu is not None:
            print(f"   {Fore.GREEN}B{Style.RESET_ALL} - {Fore.WHITE}Zurück zum Tools-Hauptmenü{Style.RESET_ALL}")
        print(f"   {Fore.RED}Q{Style.RESET_ALL} - {Fore.WHITE}Beenden{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}==================================================={Style.RESET_ALL}")

        choice = input(f"\n{Fore.YELLOW}Bitte Nummer oder Buchstaben eingeben: {Style.RESET_ALL}").strip().lower()

        if choice == "q":
            print(f"\n{Fore.CYAN}Menü wird beendet. Auf Wiedersehen!{Style.RESET_ALL}")
            break

        elif choice == "b" and current_submenu is not None:
            print(f"\n{Fore.CYAN}Zurück zum Tools-Hauptmenü...{Style.RESET_ALL}")
            current_submenu = None
            continue

        # Prüfe ob es ein Buchstaben-Shortcut für einen Ordner ist
        if current_submenu is None and choice.isalpha():
            choice_upper = choice.upper()
            for folder_name in submenu_entries:
                if get_folder_shortcut(folder_name) == choice_upper:
                    start_submenu(folder_name)
                    break
            else:
                print(f"\n{Fore.RED}[FEHLER] Ungueltige Eingabe.{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Druecken Sie Enter, um fortzufahren.{Style.RESET_ALL}")
            continue

        # Ansonsten versuche als Nummer zu interpretieren
        try:
            choice_index = int(choice) - 1

            if 0 <= choice_index < len(scripts):
                script_to_run = scripts[choice_index]

                print(f"\n{Fore.CYAN}--- Starte Tool: {script_to_run.name} ---{Style.RESET_ALL}")
                print(f"{Fore.WHITE}Keine AC/Disk-ID Übergabe (Tool-spezifisch).{Style.RESET_ALL}\n")

                subprocess.run(
                    [
                        PYTHON_EXECUTABLE,
                        str(script_to_run)
                    ],
                    cwd=script_to_run.parent
                )

                print(f"\n{Fore.MAGENTA}----------------------------------------------------{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Tool-Ausfuehrung beendet. Druecken Sie Enter, um zum Menue zurueckzukehren.{Style.RESET_ALL}")

            else:
                print(f"\n{Fore.RED}[FEHLER] Ungueltige Auswahl.{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Druecken Sie Enter, um fortzufahren.{Style.RESET_ALL}")

        except ValueError:
            print(f"\n{Fore.RED}[FEHLER] Ungueltige Eingabe. Bitte eine Nummer, einen Buchstaben oder B/Q eingeben.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Druecken Sie Enter, um fortzufahren.{Style.RESET_ALL}")

        except Exception as e:
            print(f"\n{Fore.RED}[FEHLER] Ein unerwarteter Fehler ist aufgetreten: {e}{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Druecken Sie Enter, um fortzufahren.{Style.RESET_ALL}")


if __name__ == "__main__":
    main()